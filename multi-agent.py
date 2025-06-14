import httpx
from pathlib import Path
from agno.agent import Agent
from agno.tools.csv_toolkit import CsvTools
from agno.tools.duckduckgo import DuckDuckGoTools
import os
from agno.playground import Playground, serve_playground_app

from dotenv import load_dotenv

load_dotenv()

### SEARCH MOVIE DATABASE AGENT ####################################################

imdb_csv = Path(__file__).parent.joinpath("wip").joinpath("IMDB-Movie-Data.csv")

if not os.path.exists(imdb_csv):
    url = "https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv"

    response = httpx.get(url)

    imdb_csv.parent.mkdir(parents=True, exist_ok=True)
    imdb_csv.write_bytes(response.content)



imdb_csv_agent = Agent(
    name="IMDB CSV Agent",
    tools=[CsvTools(csvs=[imdb_csv])],
    markdown=True,
    show_tool_calls=True,
    instructions=[
        "First always get the list of files",
        "Then check the columns in the file",
        "Then run the query to answer the question",
    ],
)

### SEARCH THE WEB ##################################################################

web_search_agent = Agent(
    name="Web Search Agent",
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True,
)

### MAIN AGENT #####################################################################

agent_team = Agent(
    name="Agent Team",
    team=[web_search_agent, imdb_csv_agent],
    instructions=[
        "You are an AI agent which knows everything about movies",
        "You can refer questions to two different agents: Web Search Agent and IMDB CSV Agent",
        "First you always use the IMDB agent, if it cannot answer your question you use the Web Search Agent",
    ],
    show_tool_calls=False,
    markdown=True,
)


app = Playground(agents=[agent_team]).get_app()

if __name__ == "__main__":
    serve_playground_app("multi-agent:app", reload=True)