from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from utils import GmailManager
from state import EmailState
import json 
import logging

llm = init_chat_model("gpt-4o",model_provider="openai")#our llm 
gmail_manager = GmailManager()#used to access gmail apis for utils file

#need to setup logging for error handling
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

def router_node(state: EmailState) ->EmailState:
    """Determines action to take based on current_query"""
    #logger.debug(f"Router node - Query: {state['current_query']}")
    prompt = ChatPromptTemplate.from_messages([
        ("system","""You are a router that determines the next email actions to take
         by analyzing user query. You must respond only with the action word:
         -action word: 'search' ->for finding and retrieving emails
         -action word:'send' -> for composing and sending emails
         -action word:'unclear' ->if intent isn't clear
         """),("human","{query}")])
        
    chain = prompt | llm #pipes output of prompt into llm ie building the pipeline
    response = chain.invoke({"query": state["current_query"]})#fill the prompt with actual query from state and invoke the LLM

    action= response.content.strip().lower()#the new action
    #logger.debug(f"Router determined action: {action}")
    state["email_action"] = action
    return state
    

def email_retrieval_node(state:EmailState) ->EmailState:
    """Retrieves emails based on query"""
    
    #logger.debug(f"Retrieval node - Action: {state['email_action']}")
    if state["email_action"] != "search":
        return state
    
    prompt = ChatPromptTemplate.from_messages([
        ("system","""Extract the search parameters from the user query
         Return a gmail search query string
         Examples :
         -"emails from Tarek" -> "from : Tarek"
         -emails about Project Tarek -> "subject: Project Tarek"    
         -emails from June-> "Date:June" "      
         """),("human","{query}")
    ])
    
    chain = prompt | llm
    search_query = chain.invoke({"query":state["current_query"]})
    try:
        emails = gmail_manager.search_emails(search_query.content)
        state["retrieved_emails"] = emails
        #logger.debug(f"Retrieved {len(emails)} emails")
    except Exception as e:
        #logger.error(f"Email search error: {e}")
        state["error"] = f"Failed to search emails: {str(e)}"
    return state

def email_send_node(state:EmailState)->EmailState:
    """Composes and sends email to the recipient based on query"""
    if state["email_action"] != "send":
        return state
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract email parameters from the user query.
        Return ONLY a valid JSON object with exactly these keys: "to","cc", "subject", "body".
        Note that cc is either None or an email depending on user query.
        If no CC is mentioned, set "cc" to None.
        If multiple CCs are mentioned, separate them with commas.
        Do not include any other text, explanations, or markdown formatting.
        
        Example format:
        {{
            "to": "example@email.com",
            "cc":  None or "cc@email.com"
            "subject": "Subject line here",
            "body": "Email body content here"
        }}
        
        Make the body professional and well-formatted."""),
        ("human", "{query}")
    ])

    chain = prompt | llm
    response = chain.invoke({"query": state["current_query"]})

    #logger.debug(f"LLM response for email composition: {response.content}")
    
    try:
        # Clean the response content to ensure it's valid JSON
        content = response.content.strip()
        
        # Remove any markdown formatting if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        email_params = json.loads(content)
        #logger.debug(f"Parsed email params: {email_params}")
        
        # Validate required fields
        required_fields = ["to", "subject", "body"]
        for field in required_fields:
            if field not in email_params:
                raise ValueError(f"Missing required field: {field}")
        
        # Send the email
        #logger.debug(f"Attempting to send email to: {email_params['to']}")
        result = gmail_manager.send_emails(
            to=email_params["to"],
            subject=email_params["subject"],
            body=email_params["body"],
            cc = email_params["cc"]
        )
        
        #logger.debug(f"Send result: {result}")
        
        state["sent_email"] = email_params
        state["metadata"]["send_results"] = result
        
        if not result.get("success", False):
            state["error"] = f"Email sending failed: {result.get('error', 'Unknown error')}"
        
    except json.JSONDecodeError as e:
        #logger.error(f"JSON parsing error: {e}")
        #logger.error(f"Raw content: {response.content}")
        state["error"] = f"Failed to parse email parameters: {str(e)}"
    except Exception as e:
        #logger.error(f"Email composition/sending error: {e}")
        state["error"] = f"Failed to compose/send email: {str(e)}"
    
    return state


def final_response_node(state: EmailState) -> EmailState:
    """Generate final response to user summarizing the actions taken"""
    #logger.debug(f"Final response node - Action: {state.get('email_action')}")
    #logger.debug(f"Error state: {state.get('error')}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Generate a helpful response to the user based on the action taken.
        Include relevant details from the state.
        Be concise and informative.
        
        If there was an error, provide helpful troubleshooting suggestions.
        If email was sent successfully, confirm the details.
        If emails were retrieved, summarize the results."""),
        ("human", """
        Action: {action}
        Query: {query}
        Retrieved Emails: {emails}
        Draft Email: {sentemail}
        Error: {error}
        Send Results: {send_results}
        """)])

    chain = prompt | llm 
    response = chain.invoke({
        "action": state.get("email_action", "unknown"),
        "query": state["current_query"],
        "emails": state.get("retrieved_emails", []),
        "sentemail": state.get("sent_email", {}),
        "error": state.get("error", ""),
        "send_results": state.get("metadata", {}).get("send_results", {})
    })

    state["messages"].append(AIMessage(content=response.content))
    return state
    
