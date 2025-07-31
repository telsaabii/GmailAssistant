# Gmail Assistant with LangGraph

An intelligent Gmail assistant built using LangGraph and LangChain that can search emails and send emails based on natural language queries.

## Features

- **Email Search**: Search for emails using natural language queries
- **Email Sending**: Compose and send emails with natural language instructions
- **Intelligent Routing**: Automatically determines whether to search or send emails based on user intent
- **Conversational Interface**: Interactive command-line interface for seamless communication

## Architecture

The assistant uses a graph-based architecture with LangGraph:

- **Router Node**: Analyzes user queries to determine the appropriate action (search/send/unclear)
- **Email Retrieval Node**: Searches Gmail for emails matching the query
- **Email Send Node**: Composes and sends emails based on user instructions
- **Final Response Node**: Generates user-friendly responses summarizing the actions taken

## Prerequisites

- Python 3.8+
- Gmail API credentials
- OpenAI API key
- Google Cloud Project with Gmail API enabled

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gmail-assistant
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Gmail API Setup

### 1. Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project

### 2. Create Credentials

1. In the Google Cloud Console, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure the OAuth consent screen if prompted
4. Choose "Desktop application" as the application type
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the project root

### 3. Generate Token

Run the authentication script to generate your token:
```bash
python test.py
```

This will:
- Open a browser window for Google OAuth authorization
- Generate a `token.json` file with your access credentials
- **Important**: Keep both `credentials.json` and `token.json` private and never commit them to version control

## Usage

### Starting the Assistant

Run the main application:
```bash
python main.py
```

### Example Queries

**Email Search:**
- "Find emails from John"
- "Show me emails about the project meeting"
- "Search for emails from last week"
- "Find emails with subject containing 'invoice'"

**Email Sending:**
- "Send an email to john@example.com about the meeting tomorrow"
- "Compose an email to team@company.com with subject 'Project Update' and tell them about our progress"
- "Send a follow-up email to client@example.com regarding our last discussion"

**Exiting:**
- Type `exit`, `quit`, or `bye` to close the assistant

## File Structure

```
gmail-assistant/
├── main.py              # Main application entry point
├── graph.py             # LangGraph workflow definition
├── nodes.py             # Individual node implementations
├── state.py             # State schema definition
├── utils.py             # Gmail API utilities
├── test.py              # Gmail toolkit testing script
├── requirements.txt     # Python dependencies
├── credentials.json     # Gmail API credentials (create yourself)
├── token.json          # OAuth token (generated automatically)
└── README.md           # This file
```

## Security Notes

⚠️ **Important Security Information:**

- **Never commit `credentials.json` or `token.json` to version control**
- These files contain sensitive authentication information
- Add them to your `.gitignore` file
- Each user must create their own credentials through the Google Cloud Console
- Tokens expire and may need to be refreshed periodically

## Troubleshooting

### Common Issues

1. **Authentication Errors:**
   - Ensure `credentials.json` is properly configured
   - Check that Gmail API is enabled in your Google Cloud project
   - Verify OAuth consent screen is configured

2. **Token Expiration:**
   - Delete `token.json` and run the authentication process again
   - Check token expiry in the token file

3. **API Quota Exceeded:**
   - Check your Gmail API usage in Google Cloud Console
   - Consider implementing rate limiting if needed

4. **Permission Errors:**
   - Ensure your OAuth scope includes Gmail access
   - Verify the consent screen approval status

### Debugging

Uncomment logging lines in `nodes.py` and `utils.py` for detailed debugging information:
```python
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

## Customization

### Modifying Search Parameters

Edit the `email_retrieval_node` in `nodes.py` to customize search query formatting:
```python
# Add custom search parameters
prompt = ChatPromptTemplate.from_messages([
    ("system", """Your custom search parameter extraction logic here"""),
    ("human", "{query}")
])
```

### Adding New Actions

1. Add new action types in the `router_node`
2. Create corresponding node functions
3. Update the graph routing logic in `graph.py`
4. Add new state fields in `state.py` if needed

## Dependencies

Key packages used:
- `langgraph`: Graph-based workflow orchestration
- `langchain`: LLM framework and tools
- `langchain-google-community`: Gmail integration
- `langchain-openai`: OpenAI LLM integration
- `google-api-python-client`: Google API client
- `python-dotenv`: Environment variable management


---

**Note**: This project requires valid Gmail API credentials and OpenAI API access. Make sure to follow Google's API usage policies and OpenAI's terms of service.
