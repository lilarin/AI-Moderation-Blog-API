import os

from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerationConfig


load_dotenv()
SECRET_KEY = os.environ.get("GEMINI_SECRET_KEY")
genai.configure(api_key=SECRET_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_ai_response(prompt: str, bool_answer: bool = False) -> str | None:
    try:
        config = None
        if bool_answer:
            config = GenerationConfig(
                response_schema=bool,
                response_mime_type="application/json"
            )
        ai_response = model.generate_content(contents=prompt, generation_config=config)
        if ai_response.candidates[0].finish_reason.name == "SAFETY":
            return "true"
        return ai_response.candidates[0].content.parts[0].text.strip()
    except Exception:
        return


def block_decision(text: str) -> bool | None:
    instruction = (
        "Answer ONLY True if there are any violations in the text, the presence "
        "of foul language, mentioning of bad words, etc, or False if not: "
        "Please analyze the following text for violations:\n"
    )
    prompt = instruction + text
    response_text = generate_ai_response(prompt, bool_answer=True)
    if response_text:
        return response_text.lower() == "true"
    return False


def response_to_comment(post_text: str, comment_text: str) -> str | None:
    instruction = (
        "You are the author of the post and not an AI, make a RESPONSE to the USER who commented on your post."
        " Determine your tone based on the style of the comment and its text.\n"
        "Post text:\n"
    )
    prompt = f"{instruction}{post_text}\nUser comment:\n{comment_text}"
    response_text = generate_ai_response(prompt)
    if response_text:
        return " ".join(response_text.split())
    return None
