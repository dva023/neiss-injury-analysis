import json
import unittest
from unittest.mock import MagicMock, patch

from libs.constants import (
    CLAUDE_MODEL_NAME,
    GEMINI_MODEL_NAME,
    GPT_4_MINI_MODEL_NAME,
    GPT_4_MODEL_NAME,
    LOCAL_MODEL_NAME,
)
from libs.gen_model import (
    call_claude_api,
    call_gemini_api,
    call_local_api,
    call_openai_api,
    send_message,
)


class TestAPICalls(unittest.TestCase):

    @patch("libs.gen_model.OpenAI")
    def test_call_openai_api(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = '{"response": "Test response"}'
        mock_client.chat.completions.create.return_value = mock_completion

        result = call_openai_api(GPT_4_MINI_MODEL_NAME, "Test message")
        self.assertEqual(result, '{"response": "Test response"}')
        mock_client.chat.completions.create.assert_called_once()

    @patch("libs.gen_model.vertexai")
    @patch("libs.gen_model.GenerativeModel")
    def test_call_gemini_api(self, mock_generative_model, mock_vertexai):
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = '{"response": "Test response"}'
        mock_model.generate_content.return_value = [mock_response]

        result = call_gemini_api(GEMINI_MODEL_NAME, "Test message")
        self.assertEqual(result, '{"response": "Test response"}')
        mock_model.generate_content.assert_called_once()

    @patch("libs.gen_model.anthropic.Anthropic")
    def test_call_claude_api(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = '{"response": "Test response"}'
        mock_client.messages.create.return_value = mock_message

        result = call_claude_api(CLAUDE_MODEL_NAME, "Test message")
        self.assertEqual(result, '{"response": "Test response"}')
        mock_client.messages.create.assert_called_once()

    @patch("libs.gen_model.OllamaClient")
    def test_call_local_api(self, mock_ollama_client):
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat.return_value = {
            "message": {"content": '{"response": "Test response"}'}
        }

        result = call_local_api(LOCAL_MODEL_NAME, "Test message")
        self.assertEqual(result, '{"response": "Test response"}')
        mock_client.chat.assert_called_once()

    @patch("libs.gen_model.call_openai_api")
    @patch("libs.gen_model.call_gemini_api")
    @patch("libs.gen_model.call_claude_api")
    @patch("libs.gen_model.call_local_api")
    def test_send_message(self, mock_local, mock_claude, mock_gemini, mock_openai):
        mock_openai.return_value = '{"response": "OpenAI response"}'
        mock_gemini.return_value = '{"response": "Gemini response"}'
        mock_claude.return_value = '{"response": "Claude response"}'
        mock_local.return_value = '{"response": "Local response"}'

        self.assertEqual(
            send_message(GPT_4_MINI_MODEL_NAME, "Test"),
            '{"response": "OpenAI response"}',
        )
        self.assertEqual(
            send_message(GEMINI_MODEL_NAME, "Test"), '{"response": "Gemini response"}'
        )
        self.assertEqual(
            send_message(CLAUDE_MODEL_NAME, "Test"), '{"response": "Claude response"}'
        )
        self.assertEqual(
            send_message(LOCAL_MODEL_NAME, "Test"), '{"response": "Local response"}'
        )

        with self.assertRaises(ValueError):
            send_message("unsupported_model", "Test")


if __name__ == "__main__":
    unittest.main()
