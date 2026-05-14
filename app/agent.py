import os
from groq import Groq
from dotenv import load_dotenv

from app.retrieval import search_assessments
from app.guardrails import is_off_topic, is_prompt_injection
from app.prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Clarification keywords
CLARIFICATION_TRIGGERS = [
    "assessment",
    "developer",
    "engineer",
    "hiring",
    "job"
]


def needs_clarification(user_text: str):

    user_text = user_text.lower()

    short_query = len(user_text.split()) < 6

    vague = any(
        word in user_text
        for word in CLARIFICATION_TRIGGERS
    )

    return short_query and vague


def classify_test_type(name: str):

    name = name.lower()

    if "personality" in name or "opq" in name:
        return "P"

    if (
        "java" in name
        or "python" in name
        or "coding" in name
        or "developer" in name
    ):
        return "K"

    if "cognitive" in name or "ability" in name:
        return "C"

    return "G"


def generate_reply(messages):

    try:

        # Empty message check
        if not messages:
            return {
                "reply": "Please provide hiring requirements.",
                "recommendations": [],
                "end_of_conversation": False
            }

        latest = messages[-1]["content"]

        # Off-topic protection
        if is_off_topic(latest):
            return {
                "reply": "I can only help with SHL assessment recommendations.",
                "recommendations": [],
                "end_of_conversation": False
            }

        # Prompt injection protection
        if is_prompt_injection(latest):
            return {
                "reply": "I cannot comply with prompt manipulation attempts.",
                "recommendations": [],
                "end_of_conversation": False
            }

        # Clarification logic
        if needs_clarification(latest):
            return {
                "reply": (
                    "Could you share the role seniority, "
                    "technical skills, and whether you also "
                    "want personality or cognitive testing?"
                ),
                "recommendations": [],
                "end_of_conversation": False
            }

        # Combine conversation history
        combined_context = " ".join([
            m["content"]
            for m in messages
        ])

        print("Combined Context:", combined_context)

        # Retrieve relevant assessments
        retrieved = search_assessments(
            combined_context,
            top_k=5
        )

        print("Retrieved Assessments:", retrieved)

        # No retrieval fallback
        if not retrieved:
            return {
                "reply": "I could not find matching SHL assessments.",
                "recommendations": [],
                "end_of_conversation": False
            }

        # Build catalog context
        catalog_context = "\n\n".join([
            (
                f"Name: {r['name']}\n"
                f"URL: {r['url']}\n"
                f"Description: {r['description'][:1000]}"
            )
            for r in retrieved
        ])

        # Prompt for LLM
        prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{combined_context}

Catalog:
{catalog_context}

Generate:
1. A helpful conversational reply
2. Recommend suitable SHL assessments
3. Stay grounded in catalog data only
"""

        print("Calling Groq API...")

        # Groq API call
        response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.2,
    max_tokens=500
)
        reply = response.choices[0].message.content.strip()

        # Build structured recommendations
        recommendations = []

        for item in retrieved:

            recommendations.append({
                "name": item["name"],
                "url": item["url"],
                "test_type": classify_test_type(
                    item["name"]
                )
            })

        return {
            "reply": reply,
            "recommendations": recommendations[:10],
            "end_of_conversation": True
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "reply": f"Internal server error: {str(e)}",
            "recommendations": [],
            "end_of_conversation": False
        }