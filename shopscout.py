"""ShopScout — product research agent.

Uses Claude with web_search_20260209 to compare prices across UK retailers.

Standalone usage:
    python3 shopscout.py "Sony WH-1000XM5 headphones"

Module usage:
    from shopscout import research_product
    result = research_product("Sony WH-1000XM5 headphones")
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

SYSTEM_PROMPT = """You are ShopScout, a personal shopping research assistant for a UK buyer.

When asked to research a product, search Amazon.co.uk, Currys, John Lewis, and Argos.
Compare current prices, ratings, and availability across these retailers.

Format your response as a plain-text email summary (no markdown, no asterisks, no bold/italic).
Use only plain text with the exact structure below:

SHOPSCOUT RESULTS
=================
Query: [query]

OVERVIEW
--------
[2-3 sentences covering price range, where deals are, and whether now is a good time to buy]

TOP PICK
--------
[Product name] at [Retailer] for £[Price]
Link: [direct product URL]
Reason: [one sentence explaining why this is the best choice]

OTHER OPTIONS
-------------
1. [Product Name]
   Price:  £XXX at [Retailer]
   Rating: X.X/5 (N reviews)
   Link:   [URL]
   Note:   [one-line highlight or caveat]

2. [Product Name]
   ...

FULL PRICE COMPARISON
---------------------
[Product model]: Amazon.co.uk £XXX | Currys £XXX | John Lewis £XXX | Argos £XXX

NOTES
-----
- [Availability, shipping, warranty, or deal caveats]
- [Any additional relevant info]

Keep URLs as plain https:// links — no markdown formatting."""


def research_product(query: str) -> str:
    """Research a product across UK retailers using Claude web search."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "Error: ANTHROPIC_API_KEY not set"

    if not query or not query.strip():
        return (
            "ShopScout: No query provided.\n\n"
            "Usage: python3 shopscout.py 'Sony WH-1000XM5 headphones'"
        )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=[
                {
                    "type": "web_search_20260209",
                    "name": "web_search",
                    "user_location": {
                        "type": "approximate",
                        "country": "GB",
                        "city": "London",
                        "timezone": "Europe/London",
                    },
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"Research and compare prices for: {query.strip()}",
                }
            ],
        )

        # web_search_20260209 is server-side — API handles execution, returns end_turn directly
        text_parts = [
            block.text
            for block in response.content
            if hasattr(block, "text") and block.type == "text"
        ]
        return "\n".join(text_parts) if text_parts else "(No results returned)"

    except Exception as e:
        return f"ShopScout error: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print(
            "ShopScout: No query provided.\n\n"
            "Usage: python3 shopscout.py 'Sony WH-1000XM5 headphones'"
        )
        sys.exit(0)

    print(research_product(sys.argv[1]))
