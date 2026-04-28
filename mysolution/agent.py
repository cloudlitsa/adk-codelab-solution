from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# from google.adk.agents import Agent
# from datetime import datetime
# from google.adk.tools import google_search

def now() -> dict:
    """Returns the current date and time."""
    my_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "status": "success",
        "current_time": my_datetime
    }

airbnb_mcp = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        ),
    )
)

root_agent = Agent(
    name="travel_mcp",
    model="gemini-2.5-flash",
    instruction="You are a helpful travel assistant. You can find accommodation using Airbnb, and have access to the current time.",
    tools=[now, airbnb_mcp],
)

# root_agent = Agent(
#     name="travel_basic",
#     model="gemini-2.5-flash",
#     instruction="You are a helpful travel assistant. " +
#     "You can provide the current date and time using your tools.",
#     # tools=[now]
#     tools=[google_search]
# )
