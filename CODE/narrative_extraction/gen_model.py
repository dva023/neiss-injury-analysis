import json
import os

import anthropic
import google.generativeai as genai
from constants import (
    MODEL_CLAUDE,
    MODEL_GEMINI,
    MODEL_GPT_4,
    MODEL_GPT_4_MINI,
    MODEL_LOCAL,
)
from dotenv import load_dotenv
from ollama import Client as OllamaClient
from openai import OpenAI

load_dotenv()


def call_openai_api(model_name, message):
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model=model_name,
        response_format={"type": "json_object"},
    )
    return json.loads(chat_completion.choices[0].message.content)  # pyright:ignore


def call_gemini_api(model_name, message):

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    model = genai.GenerativeModel(
        model_name=model_name, generation_config={"temperature": 0.1}
    )
    response = model.generate_content(
        message, generation_config={"response_mime_type": "application/json"}
    )

    return json.loads(response.text)  # pyright:ignore


def call_claude_api(model_name, message):

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=model_name,
        max_tokens=1000,
        temperature=0.1,
        messages=[
            {"role": "user", "content": message},
            {"role": "assistant", "content": "Here is the JSON requested:"},
        ],
    )
    return json.loads(response.content[0].text)  # pyright:ignore


def call_local_api(model_name, message):
    client = OllamaClient(host="http://localhost:11434")
    response = client.chat(
        model=model_name,
        messages=[{"role": "user", "content": message}],
    )
    return response["message"]["content"]


def send_message(model, message):

    try:
        if model in (MODEL_GPT_4, MODEL_GPT_4_MINI):
            return call_openai_api(model, message)
        elif model == MODEL_GEMINI:
            return call_gemini_api(model, message)
        elif model == MODEL_LOCAL:
            return call_local_api(model, message)
        elif model == MODEL_CLAUDE:
            return call_claude_api(model, message)
        else:
            raise ValueError("Model not supported.")
    except Exception as e:
        # print("Failed to call {}, due to {}".format(model, e))
        raise e


# if __name__ == "__main__":
#     test_message = "Count numbers from 1 to 10. Respond in JSON format."
#
#     models = [
#         MODEL_GPT_4_MINI,
#         MODEL_GEMINI,
#         MODEL_CLAUDE,
#         MODEL_LOCAL,
#     ]
#     for model in models:
#         print(f"\nTesting {model}:")
#         response = send_message(model, test_message)
#         if response:
#             print(f"Response: {response}")
#         else:
#             print("No response received.")
