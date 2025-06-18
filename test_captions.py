import unittest
import subprocess
import os
import time

VIDEO_PATH = "griffin.mp4"  # make sure this exists in the working dir
EXPECTED_FILES = ["temp.mp3", "output.srt", "output.mp4"]
SCRIPT_PATH = "caption.py"  # name of your script

class TestCaptionPipeline(unittest.TestCase):

    def test_output_files_generated(self):
        # Run the captions script
        result = subprocess.run(
            ["python", SCRIPT_PATH, VIDEO_PATH],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(result.stderr)
        time.sleep(2)

        for file in EXPECTED_FILES:
            self.assertTrue(os.path.exists(file), f"{file} was not generated.")

        print("All expected files were generated.")
        # Clean up
        for file in EXPECTED_FILES:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Could not delete {file}: {e}")

if __name__ == "__main__":
    unittest.main()
