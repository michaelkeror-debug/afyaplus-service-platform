import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

from auth import check_password, create_token, current_user

# CONFIGURATION
load_dotenv()

MCP_SERVER_PATH = os.getenv(
    "MCP_SERVER_PATH",
    "./logistics_mcp.py"
)
LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "gpt-4.1-mini"
)

# MCP CLIENT
mcp_client = MultiServerMCPClient(
    {
        "logistics": {
            "transport": "stdio",
            "command": "python",
            "args": [MCP_SERVER_PATH],
        }
    }
)

# AGENT LIFECYCLE
@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting AfyaPlus Logistics Agent...")

    try:
        # Load tools from the MCP server
        tools = await mcp_client.get_tools()

        print("MCP tools loaded:")

        for tool in tools:
            print(f"  - {tool.name}")

        # Create the LLM
        model = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0
        )

        # Create LangChain agent
        app.state.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt="""
You are the AfyaPlus Logistics Assistant.

Answer questions using ONLY information returned by the
available MCP logistics tools.

Rules:
- Use MCP tools whenever the answer depends on logistics data.
- Never invent, guess, or assume facts not supported by MCP data.
- Do not use general/world knowledge to fill missing information.
- For multi-step questions, call the necessary tools in sequence.
- If the MCP data is insufficient to answer the question,
  respond exactly: "The data cannot answer this."
- If a tool returns an error or missing data, do not guess.

The MCP tool results are the source of truth.
""",
        )

        print(f"Agent ready using model: {LLM_MODEL}")

    except Exception as exc:
        print(f"Failed to start logistics agent: {exc}")
        raise

    yield

    print("Stopping AfyaPlus Logistics Agent...")


# FASTAPI APPLICATION
app = FastAPI(
    title="AfyaPlus Logistics Agent API",
    version="1.0.0",
    lifespan=lifespan
)


# REQUEST / RESPONSE MODELS
class LoginRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Natural-language logistics question"
    )


class AgentResponse(BaseModel):
    answer: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )

    model_used: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100
    )



# HEALTH CHECK
@app.get("/health")
def health():
    return {
        "service": "afya-plus-logistics-agent",
        "version": "1.0.0",
        "status": "ok"
    }



# LOGIN
@app.post("/token")
def login(body: LoginRequest):

    if not check_password(
        body.username,
        body.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Wrong username or password."
        )

    return {
        "access_token": create_token(body.username),
        "token_type": "bearer"
    }



# AGENT ENDPOINT
@app.post(
    "/agent",
    response_model=AgentResponse
)
async def run_agent(
    request: AgentRequest,
    user: dict = Depends(current_user)
):

    agent = getattr(
        app.state,
        "agent",
        None
    )

    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Logistics agent is not ready."
        )

    try:

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": request.question
                    }
                ]
            }
        )

        # LangChain stores the conversation/tool calls
        # in the messages list. The final message is the
        # agent's answer.
        final_message = result["messages"][-1]

        answer = final_message.content

        # Some models return structured content blocks
        # instead of a simple string.
        if isinstance(answer, list):

            text_parts = []

            for block in answer:

                if isinstance(block, dict):

                    if block.get("type") == "text":
                        text_parts.append(
                            block.get("text", "")
                        )

                elif isinstance(block, str):
                    text_parts.append(block)

            answer = "".join(text_parts)

        # Safety fallback
        if not answer or not answer.strip():

            answer = "The data cannot answer this."

        return AgentResponse(
            answer=answer.strip(),
            model_used=LLM_MODEL,
            user_id=user["sub"]
        )

    except Exception as exc:

        print(f"Agent error: {exc}")

        raise HTTPException(
            status_code=503,
            detail="The logistics agent is temporarily unavailable."
        )