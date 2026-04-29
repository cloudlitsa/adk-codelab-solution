from __future__ import annotations
import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

def now() -> dict:
    """Returns the current date and time."""
    return {
        "status": "success",
        "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

airbnb_mcp = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        ),
    )
)

# Subagent: wraps google_search so it can be mixed with other tools in the root agent
review_agent = Agent(
    name="review_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a hotel review specialist. When given a hotel name and location, "
        "use Google Search to find recent guest reviews. "
        "Summarise as: ✅ Positives (up to 3 bullets) and ❌ Negatives (up to 3 bullets). "
        "Be concise and factual."
    ),
    tools=[google_search],
)

review_tool = AgentTool(agent=review_agent)
time_tool = FunctionTool(func=now)

root_agent = Agent(
    name="travel_mcp",
    model="gemini-2.5-flash",
    instruction=(
        "You are a helpful travel assistant. You can find accommodation using Airbnb, get reviews, and check the current time. "
        "Return search results as a table with: hotel emoji 🏨, price 💰, and moon-phase star ratings 🌕🌕🌗🌑 (use 🌑 for empty, 🌗 for half). "
        "Prioritise listings that are: pet-friendly 🐾, close to public transport 🚇, quiet 🔇, and not on the ground floor. "
        "For each result, add a 'Litsa-rating' from 1-10 🌟 based on how well it matches those preferences — "
        "deduct points for ground floor, noise, distance from transport, or no pets allowed. "
        "Sort results by Litsa-rating descending. "
        "If the user asks for reviews of a specific hotel, use the review_agent tool."
    ),
    tools=[time_tool, airbnb_mcp, review_tool],
)
