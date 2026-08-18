import os
from typing import Annotated

import requests
from dotenv import load_dotenv

import autogen
from autogen import AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent
from autogen.tools import Tool

load_dotenv()

ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")
ZENROWS_ENDPOINT = "https://api.zenrows.com/v1/"

llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    ],
    "temperature": 0,
}

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=lambda msg: "TERMINATE" in (msg.get("content") or ""),
)

researcher = AssistantAgent(
    name="researcher",
    system_message=(
        "You are a research agent. When given a URL, use the fetch_page_content "
        "tool to retrieve its web content, then summarize what you find. Be "
        "factual and note anything that looks incomplete or missing from the "
        "page. Pass your summary to the analyst."
    ),
    llm_config=llm_config,
)

analyst = AssistantAgent(
    name="analyst",
    system_message=(
        "You are a data analyst. Extract structured fields, such as plan names "
        "and prices, from the content the researcher provides. Present the "
        "result as a clean list. If the researcher's content has no usable "
        "data, say so explicitly instead of guessing."
    ),
    llm_config=llm_config,
)

critic = AssistantAgent(
    name="critic",
    system_message=(
        "You are a critic. Validate the analyst's structured output against "
        "the researcher's original content. Flag any gaps, missing fields, or "
        "inconsistencies. When the output checks out or no further progress is "
        "possible, say so and end your message with TERMINATE."
    ),
    llm_config=llm_config,
)


def fetch_page_content(
    url: Annotated[str, "The target URL to fetch through Zenrows using adaptive stealth mode."],
) -> str:
    """Fetch a URL through Zenrows' Fetch API and return clean Markdown."""
    params = {
        "url": url,
        "apikey": ZENROWS_API_KEY,
        "mode": "auto",
        "response_type": "markdown",
    }
    response = requests.get(ZENROWS_ENDPOINT, params=params, timeout=60)
    response.raise_for_status()
    return response.text


fetch_tool = Tool(
    name="fetch_page_content",
    description=(
        "Fetch a URL through Zenrows and return clean Markdown content from "
        "JavaScript-rendered and anti-bot-protected pages."
    ),
    func_or_tool=fetch_page_content,
)

fetch_tool.register_for_llm(researcher)
fetch_tool.register_for_execution(user_proxy)

group_chat = GroupChat(
    agents=[user_proxy, researcher, analyst, critic],
    messages=[],
    max_round=6,
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
)

chat_result = user_proxy.initiate_chat(
    manager,
    message=(
        "Fetch the product listing from this page and extract the "
        "product name and price: https://www.walmart.com/ip/AirPods-Pro-3/17835006350"
    ),
)

print("\n===== FULL CHAT HISTORY =====")
for msg in chat_result.chat_history:
    speaker = msg.get("name") or msg.get("role")
    print(f"[{speaker}]: {msg.get('content')}\n")

print("\n===== TOKEN USAGE =====")
print(chat_result.cost)

print("\n===== USAGE SUMMARY (ALL AGENTS) =====")
usage_summary = autogen.gather_usage_summary([user_proxy, researcher, analyst, critic, manager])
print(usage_summary)
