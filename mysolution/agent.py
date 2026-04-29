from __future__ import annotations
import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 1. Utility Tool
def now() -> dict:
    """Returns the current date and time."""
    return {
        "status": "success",
        "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# 2. Worker Agent: Booking Specialist (Airbnb)
airbnb_mcp = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        ),
    )
)

booking_agent = Agent(
    name="booking_specialist",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert at finding accommodations on Airbnb. "
        "Search for listings based on the user's location and dates. "
        "Return the raw data including name, price, and key features."
    ),
    tools=[airbnb_mcp],
)

# 3. Worker Agent: Review Specialist (Google Search)
review_agent = Agent(
    name="review_specialist",
    model="gemini-2.5-flash",
    instruction=(
        "You are a hotel review specialist. Use Google Search to find recent guest reviews "
        "for specific hotels. Summarise findings as: ✅ Positives and ❌ Negatives. "
        "Focus on noise levels, pet-friendliness, and floor level if possible."
    ),
    tools=[google_search],
)

# 4. Wrap workers as tools for the Manager
booking_tool = AgentTool(agent=booking_agent)
review_tool = AgentTool(agent=review_agent)
time_tool = FunctionTool(func=now)

# 5. Root Manager Agent
# This agent orchestrates the workers and applies the "Litsa-rating"
root_agent = Agent(
    name="travel_concierge_manager",
    model="gemini-2.5-flash",
    instruction=(
        "You are a luxury travel concierge manager. Your job is to coordinate your specialists "
        "to provide the perfect recommendation.\n\n"
        "STEPS:\n"
        "1. Check the current time using 'now' if needed.\n"
        "2. Ask the booking_specialist to find options at the user's destination.\n"
        "3. For the most promising options, ask the review_specialist for a vibe check.\n"
        "4. PRESENTATION: Return results as a table with: 🏨 Hotel, 💰 Price, and 🌕🌕🌕🌑 ratings.\n"
        "5. RATING LOGIC: Apply the 'Litsa-rating' (1-10 🌟). "
        "Start at 10 and deduct points for: ground floor, noise, no pets, or far from transport.\n"
        "6. Sort by Litsa-rating descending."
    ),
    tools=[time_tool, booking_tool, review_tool],
)
