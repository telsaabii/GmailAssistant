from dotenv import load_dotenv
import os
from graph import email_assistant
from state import EmailState  
from langchain_core.messages import HumanMessage
from typing import List, Dict

load_dotenv()

class GmailAssistant:
    def __init__(self):
        self.graph = email_assistant
        self.conversation_history : List[Dict] = []

    def process_query(self,user_query:str) ->str:


        #create intiial state
        initial_state = EmailState(
            messages=[HumanMessage(content=user_query)],
            current_query=user_query,
            email_action=None,
            retrieved_emails=None,
            sent_email=None,
            metadata={},
            error=None
        )

        # running the graph
        try:
            final_state = self.graph.invoke(initial_state)
            
            # extract responses
            if final_state["messages"]:
                response = final_state["messages"][-1].content
                self.conversation_history.append({
                    "query": user_query,
                    "response": response,
                    "action": final_state.get("email_action")
                })
                return response
            else:
                return "I couldn't process your request. Please try again."
        except Exception as e:
            return f"An error occurred: {str(e)}"

def main():
    """Main interactive loop"""

    print("\nInitializing Gmail Assistant...")
    try:
        assistant = GmailAssistant()
        print("""\nGmail Assistant initialized successfully
              Ask the assistant to search or send an email for you !""")

    except Exception as e:
        print(f"\nFailed to initialize assistant: {str(e)}")
        return
    

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nGoodbye! Thanks for using Gmail Assistant.")
                break
        
        print("\nProcessing your request...")
        response = assistant.process_query(user_input)
        print(f"Assistant response:{response}")

if __name__ == "__main__":
    main()

