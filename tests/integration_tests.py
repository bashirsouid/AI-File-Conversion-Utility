import unittest
import tempfile
import os
import json
from modify import main

class TestModifyIntegration(unittest.TestCase):
    def setUp(self):
        """
        Set up a temporary directory with test files and mock environment variables.
        """
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()

        # Mock environment variables for API keys
        os.environ["API_KEY_1"] = "test_api_key_1"
        os.environ["API_KEY_2"] = "test_api_key_2"
        os.environ["API_KEY_3"] = "test_api_key_3"

        # Create mock input JSON files
        self.file1_path = os.path.join(self.test_dir.name, "file1.json")
        self.file2_path = os.path.join(self.test_dir.name, "file2.json")

        file1_content = {"data": "This is file 1 content."}
        file2_content = {"data": "This is file 2 content."}

        with open(self.file1_path, "w") as f:
            json.dump(file1_content, f)

        with open(self.file2_path, "w") as f:
            json.dump(file2_content, f)

    def tearDown(self):
        """
        Clean up the temporary directory.
        """
        self.test_dir.cleanup()

    def test_integration_file_processing(self):
        """
        Test that the script processes files in the directory and generates output files.
        """
        # Run the main function on the temporary directory
        main(self.test_dir.name)

        # Check if output files are created
        output_file1_path = os.path.splitext(self.file1_path)[0] + ".testOriginal"
        output_file2_path = os.path.splitext(self.file2_path)[0] + ".testOriginal"

        self.assertTrue(os.path.exists(output_file1_path), "Output file for file1.json was not created.")
        self.assertTrue(os.path.exists(output_file2_path), "Output file for file2.json was not created.")

        # Validate the contents of the output files (mocked response)
        with open(output_file1_path, "r") as f:
            output_content1 = f.read().strip()
            self.assertIn("This is file 1 content", output_content1)

        with open(output_file2_path, "r") as f:
            output_content2 = f.read().strip()
            self.assertIn("This is file 2 content", output_content2)

    def test_skipping_existing_files(self):
        """
        Test that existing `.testOriginal` files are skipped during processing.
        """
        # Pre-create an output file to simulate skipping
        output_file1_path = os.path.splitext(self.file1_path)[0] + ".testOriginal"
        
        with open(output_file1_path, "w") as f:
            f.write("Pre-existing content")

        # Run the main function again
        main(self.test_dir.name)

        # Ensure the pre-existing file was not overwritten
        with open(output_file1_path, "r") as f:
            content = f.read().strip()
            self.assertEqual(content, "Pre-existing content", "Existing .testOriginal file was overwritten.")

if __name__ == "__main__":
    unittest.main()
