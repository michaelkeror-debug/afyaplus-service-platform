 AfyaPlus Multimodal Intake Assistant

## Overview
AI service platform: an AI model wrapped in a secure FastAPI service with JWT authentication, containerised with Docker, plus an MCP server exposing at least two tools and one resource, consumed by an LLM agent.

## Project Structure
- triage_model_call.py:An endpoint wrapping an AI model call, with typed Pydantic request and response models and field constraints
- test_triage.py : test traige_model_call.py
- logisitics_mcp.py : MCP server with at least two tools and one resource built with the Python MCP SDK, with precise docstrings
- test_mcp.py : test loegistics_mcp.py
- Dockerfile : on a slim base image, dependency layers ordered for caching
- auth.py : JWT authentication

## How to Reproduce
1. Environment setup: pip install -r requirements.txt
2. run test_triage.py 
3. run test_mcp.py
4. docker build -t afyaplus-triage:1.0.0 .
5.run agent: uvicorn agent_api:app --reload --port 8000
