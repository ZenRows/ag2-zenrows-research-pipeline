# Build a Web Research Multi-Agent System with AG2 and Zenrows

This repository contains the code for an AG2 group chat pipeline with a researcher, analyst, and critic agent, coordinated through a user proxy. It shows what happens when the researcher has no way to fetch a page, and what changes once Zenrows' Fetch API is registered as a typed AG2 tool with `mode=auto`.

## Features

- Four-agent AG2 group chat (user proxy, researcher, analyst, critic) built with the OpenAI client
- A baseline pipeline demonstrating the failure mode when no fetch tool is registered
- A working pipeline with Zenrows' Fetch API registered as a typed AG2 tool using `mode=auto`
- Token usage and cost comparison between both runs using `autogen.gather_usage_summary()`
- Live extraction of real product data (name and price) from a JavaScript-rendered Walmart page

## Prerequisites

- Python 3.10 or higher
- AG2 v0.12.2
- A Zenrows account and API key
- An OpenAI account and API key

## Installation

### 1. Clone the repository

```
git clone https://github.com/ZenRows/ag2-zenrows-research-pipeline.git
cd ag2-zenrows-research-pipeline
```

### 2. Create a virtual environment

```
python -m venv .venv
```

### 3. Activate the environment

```
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 4. Install dependencies

```
pip install "ag2[openai]==0.12.2"
```

AG2 v0.12.2 imports as `autogen`, not `ag2`. AG2 is deprecating the classic framework at v1.0, at which point `import ag2` becomes the correct import.

## Configuration

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
ZENROWS_API_KEY=your_zenrows_api_key
```

## Project structure

```
.
├── baseline.py
├── zenrows_pipeline.py
└── README.md
```

## How it works

```
Task (fetch product listing + extract name and price)
   ↓
Researcher (fetch page content)
   ↓
Analyst (extract structured fields)
   ↓
Critic (validate output, terminate)
```

In the baseline run, the researcher has no fetch tool, so it can't retrieve the page and the pipeline terminates with nothing extracted. In the Zenrows run, the researcher calls the registered `fetch_page_content` tool, which fetches the target page through Zenrows' Fetch API with `mode=auto`, and passes clean Markdown into the shared history for the analyst and critic to work with.

## Running the project

### Baseline (no fetch tool)

```
python baseline.py
```

Demonstrates the failure mode with no fetch tool registered.

### Zenrows pipeline

```
python zenrows_pipeline.py
```

Runs the same group chat with Zenrows' Fetch API registered as a typed tool using `mode=auto`.

## Output

Each script prints the full chat history, the raw cost from `chat_result.cost` (unreliable for group chats), and a usage summary from `autogen.gather_usage_summary()` across all agents.

| Run | Prompt tokens | Completion tokens | Total tokens | Cost |
|---|---|---|---|---|
| Baseline (no fetch tool) | 759 | 231 | 990 | $0.000252 |
| Zenrows (mode=auto) | 7,100 | 136 | 7,236 | $0.001147 |

The baseline terminates cleanly via `TERMINATE` in 4 turns with no product data extracted. The Zenrows run extracts "Apple AirPods Pro 3" at "$189.99 (was $249.00, you save $59.01)" from a live Walmart product page.

## Technologies

- Python
- AG2 (AutoGen)
- OpenAI GPT-4o-mini
- Zenrows

## Related article

This project is part of this article:

**Build a Web Research Multi-Agent System with AG2 and Zenrows**

https://www.zenrows.com/blog/web-research-multi-agent-ag2-zenrows
