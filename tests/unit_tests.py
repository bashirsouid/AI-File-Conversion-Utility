import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
from modify import extract_agent_message, extract_content, process_file, main

class TestModifyScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up mock environment variables for API keys
        os.environ["API_KEY_1"] = "test_api_key_1"
        os.environ["API_KEY_2"] = "test_api_key_2"
        os.environ["API_KEY_3"] = "test_api_key_3"

        # Mock shared prompt and reference content
        cls.shared_prompt = "Mock shared prompt"
        cls.reference_content = "Mock reference content"

    def test_extract_agent_message_valid(self):
        # Test extracting agent message from valid API response
        response_text = json.dumps({
            "choices": [
                {"message": {"content": "This is the agent's message."}}
            ]
        })
        result = extract_agent_message(response_text)
        self.assertEqual(result, "This is the agent's message.")

    def test_extract_agent_message_invalid(self):
        # Test extracting agent message from invalid API response
        response_text = json.dumps({"choices": []})
        result = extract_agent_message(response_text)
        self.assertIsNone(result)

    def test_extract_content_with_backticks(self):
        # Test extracting content inside triple backticks
        content = "Here is some text. `````` More text."
        result = extract_content(content)
        self.assertEqual(result, "Extract this content.")

    def test_extract_content_no_backticks(self):
        # Test fallback to full content when no backticks are present
        content = "No backticks here."
        result = extract_content(content)
        self.assertIsNone(result)

    @patch("builtins.open", new_callable=mock_open, read_data="Mock file content")
    @patch("modify.requests.post")
    def test_process_file(self, mock_post, mock_file):
        # Mock API response
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = json.dumps({
            "choices": [
                {"message": {"content": "This is the agent's processed message."}}
            ]
        })

        # Mock file path and call process_file
        file_path = "/mock/directory/mock_file.json"
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: False if path.endswith(".converted.json") else True

            process_file(file_path)

            # Check that the output file was written with the processed message
            mock_file().write.assert_called_with("This is the agent's processed message.\n")

    @patch("os.walk")
    @patch("modify.process_file")
    def test_main(self, mock_process_file, mock_os_walk):
        # Mock directory structure and files
        mock_os_walk.return_value = [
            ("/mock/directory", ("subdir",), ("file1.json", "file2.json"))
        ]

        # Call main function with mocked directory
        main("/mock/directory")

        # Verify that process_file was called for each JSON file in the directory
        mock_process_file.assert_any_call("/mock/directory/file1.json")
        mock_process_file.assert_any_call("/mock/directory/file2.json")

if __name__ == "__main__":
    unittest.main()
