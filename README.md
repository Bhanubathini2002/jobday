# Agentic Resume Builder

An AI-powered resume generator that uses a multi-agent system to craft professional LaTeX resumes. Each agent is responsible for a specific section (node), performing a single LLM call to generate `.tex` code. Finally, all sections are combined into a complete resume.

## Project Structure

```text
agents/
  ├── api.py           # Backend API entry point
  ├── graphs/          # LangGraph or workflow definitions
  ├── nodes/           # Individual agent nodes (one call per node)
  ├── tools/           # Custom tools for agents
  ├── rag/             # Retrieval-Augmented Generation logic
  ├── memory/          # Agent memory persistence
  └── settings.py      # Configuration settings
ui/
  ├── app/             # Frontend application source
  └── package.json     # Node.js dependencies
deploy/                # Deployment configurations
```

## Prerequisites

- Python 3.13+
- Node.js 20+
- `uv` (Python package/environment manager)
- npm

## Setup

### 1) Backend (agents)

```bash
cd agents
uv sync
python api.py
```

Create `agents/.env` with the following variables:

**Required - Azure OpenAI**

| Variable | Description |
| --- | --- |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI deployment name |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version |

### 2) Frontend (ui)

```bash
cd ui
npm install
npm run dev
```
