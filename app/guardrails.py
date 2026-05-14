OFF_TOPIC = [
    "salary",
    "legal",
    "lawsuit",
    "politics",
    "relationship",
    "medical"
]

PROMPT_INJECTION = [
    "ignore previous instructions",
    "reveal system prompt",
    "bypass"
]


def is_off_topic(text: str):
    text = text.lower()

    for word in OFF_TOPIC:
        if word in text:
            return True

    return False


def is_prompt_injection(text: str):
    text = text.lower()

    for word in PROMPT_INJECTION:
        if word in text:
            return True

    return False