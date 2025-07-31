from langchain_google_community import GmailToolkit
from langchain_core.tools import Tool
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
import json
import logging

#logger = logging.getLogger(__name__)
class GmailManager:
    def __init__(self):
        self.tool_kit = GmailToolkit()
        self.tools = self.tool_kit.get_tools()
        self.tools_dict = {tool.name: tool for tool in self.tools}#allows us to access all the API tools 

    def search_emails(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for emails based on the query"""  
        #logger.debug(f"Searching emails with query: {query}")
        
        search_tool = self.tools_dict.get("search_gmail")
        if not search_tool:
            available_tools = list(self.tools_dict.keys())
            #logger.error(f"Gmail search tool not found. Available tools: {available_tools}")
            raise ValueError(f"Gmail search tool not found. Available tools: {available_tools}")
        
        try:
            results = search_tool.invoke({"query": query, "max_results": max_results})
            #logger.debug(f"Search results type: {type(results)}")
            #logger.debug(f"Search results content: {str(results)[:500]}...")
            
            emails = []
            
            if isinstance(results, str):
                # Parse string responses and get the actual email data
                lines = results.split('\n')
                email_ids = []
                
                for line in lines:
                    if 'Email ID:' in line or 'Message ID:' in line:
                        # Extract email ID from various formats
                        if 'Email ID:' in line:
                            email_id = line.split('Email ID:')[1].strip()
                        else:
                            email_id = line.split('Message ID:')[1].strip()
                        
                        # Clean up the email ID
                        email_id = email_id.replace('"', '').replace("'", "")
                        email_ids.append(email_id)
                
                #logger.debug(f"Found {len(email_ids)} email IDs: {email_ids}")
                
                # Get detailed email content for each ID
                get_tool = self.tools_dict.get("get_gmail_message")
                if get_tool:
                    for email_id in email_ids:
                        try:
                            email_data = get_tool.invoke({"message_id": email_id})
                            parsed_email = self.parse_email(email_data, email_id)
                            emails.append(parsed_email)
                            #logger.debug(f"Successfully parsed email: {parsed_email.get('subject', 'No subject')}")
                        except Exception as e:
                            #logger.error(f"Failed to get email {email_id}: {e}")
                            emails.append({
                                "id": email_id,
                                "error": str(e),
                                "subject": "Failed to retrieve",
                                "from": "Unknown",
                                "date": "Unknown",
                                "body": f"Error retrieving email: {e}"
                            })
                else:
                    #logger.warning("get_gmail_message tool not found")
                    # If we can't get details, at least return the IDs
                    for email_id in email_ids:
                        emails.append({
                            "id": email_id,
                            "subject": "Email found (details unavailable)",
                            "from": "Unknown",
                            "date": "Unknown", 
                            "body": "Email found but details could not be retrieved"
                        })
                        
            elif isinstance(results, list):
                # Handle list format results
                for email in results[:max_results]:
                    emails.append(self.parse_email(email))
            elif isinstance(results, dict):
                # Handle single email dict
                emails.append(self.parse_email(results))
            else:
                # Handle other formats
                #logger.warning(f"Unexpected result format: {type(results)}")
                emails = [{
                    "id": "unknown",
                    "subject": "Search completed",
                    "from": "Gmail API",
                    "date": "Unknown",
                    "body": f"Search results in unexpected format: {str(results)[:200]}..."
                }]
                
            #logger.debug(f"Final processed emails count: {len(emails)}")
            return emails
            
        except Exception as e:
            #logger.error(f"Email search error: {e}")
            return [{"error": str(e), "subject": "Search failed", "from": "Error", "date": "Unknown", "body": f"Search failed: {e}"}]
                                

        
    def send_emails(self,to:str,subject:str,body:str,cc:str = None) -> Dict:
        """Sends the parameters to the recipient email address

            Parameters: 
            to (str) : recipient email address
            subject (str): Email subject line.
            body (str): Email body content.
            cc (Optional[List[str]]): Optional CC addresses...Can be a single email or comma-separated emails.

            Returns:
            Dict[str,Any]: {
            "email details":{ full gmail message object(from,to,subject,body,cc,date)}
            "sent": True / False (True if the email was successfully sent)
            }
        """
        send_tool = self.tools_dict.get("send_gmail_message")
        if not send_tool:
            raise ValueError("Gmail send tool not found")
        
        try:
            cc_list = []
            if cc:
                cc_list = [email.strip() for email in cc.split(',') if email.strip()]
            payload = send_tool.invoke({
                "to": [to],
                "subject":subject,
                "message":body,
                "cc":cc_list#pass empty list if no CC, or list of CC emails
            })
            return {"success": True,"result":payload}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def parse_email(self,email_data:str) -> Dict:
        """Parse email data into structured format"""
        return {
            "id": "parsed_id",
            "subject": "parsed_subject",
            "from": "parsed_from",
            "date": "parsed_date",
            "body": email_data
        }

