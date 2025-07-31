from typing import TypedDict,List,Optional,Annotated#annotated attaches metadata to a type without changing what the type is 
from langchain_core.messages import BaseMessage#Basemessage used to identify ai message vs user message
import operator

#we need to define messages (between ai and user), current user query, emailaction (search,send,...), retrieved emails,draft email
class EmailState(TypedDict):
    """State schema for our email assistant which will be shared between LangGraph nodes"""
    messages: Annotated[List[BaseMessage],operator.add]#operator.add concatenates the messages instead of replacing them
    current_query: str
    email_action: Optional[str] #optional meaning it can be search,send,summarize or none...
    retrieved_emails: Optional[List[str]]#list of emails we're retrieving
    sent_email:Optional[dict]
    metadata:dict
    error:Optional[str]