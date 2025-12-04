import os
import time
import json
import logging
import cv2
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

logger = logging.getLogger(__name__)

class GeminiVideoSearch:
    def __init__(self, video_path="data/downloaded_video.mp4"):
        self.video_path = video_path
        self.uploaded_file = None

    def upload_video(self):
        """Uploads video to Google Cloud and waits for processing to finish."""
        if not os.path.exists(self.video_path):
            logger.error("Video file not found!")
            return None

        print(f"\n[Gemini] Uploading {self.video_path}...")
        
        # 1. Upload
        video_file = genai.upload_file(path=self.video_path)
        print(f"[Gemini] Upload complete. Name: {video_file.name}")

        # 2. Wait for Processing (Active State)
        while video_file.state.name == "PROCESSING":
            print("[Gemini] Cloud processing in progress...", end="\r")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError("Video processing failed on Google side.")

        print(f"\n[Gemini] Video is Ready! (State: {video_file.state.name})")
        self.uploaded_file = video_file

    def search_video(self, user_query):
        """
        Asks Gemini to find timestamps. Returns a list of strings ['00:12', '01:05'].
        """
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
        
        # We force JSON output to make it easy to parse
        sys_prompt = (
            "You are a video search engine. Find all timestamps relevant to the user query. "
            "Return ONLY a JSON list of timestamps in 'MM:SS' format. "
            "Example: [\"00:12\", \"01:45\"]. Do not write any other text."
        )
        
        print(f"[Gemini] Analyzing video with query: '{user_query}'...")
        
        # Measure Token Count (roughly)
        start_time = time.time()
        response = model.generate_content(
            [self.uploaded_file, sys_prompt, user_query],
            request_options={"timeout": 600}
        )
        duration = time.time() - start_time

        # Token Usage Logging
        if response.usage_metadata:
            tokens = response.usage_metadata.prompt_token_count
            print(f"[Gemini] Analysis done in {duration:.1f}s. Tokens used: {tokens}")

        # Parse JSON
        try:
            # Clean up markdown if Gemini adds it (```json ... ```)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            timestamps = json.loads(clean_text)
            return timestamps
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {response.text}")
            return []

    def extract_frames(self, timestamps, output_folder="data/gemini_results"):
        """
        Extracts the exact frames at the given timestamps using OpenCV.
        """
        os.makedirs(output_folder, exist_ok=True)
        # Clear old results
        for f in os.listdir(output_folder):
            os.remove(os.path.join(output_folder, f))

        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        extracted_paths = []
        print(f"\n[Gemini] Extracting {len(timestamps)} frames...")

        for ts in timestamps:
            try:
                # Convert MM:SS to seconds
                parts = ts.split(':')
                seconds = int(parts[0]) * 60 + int(parts[1])
                
                # Calculate frame index
                frame_id = int(seconds * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
                ret, frame = cap.read()
                
                if ret:
                    filename = f"frame_{ts.replace(':','-')}.jpg"
                    path = os.path.join(output_folder, filename)
                    cv2.imwrite(path, frame)
                    extracted_paths.append(path)
                    print(f" > Saved {ts} -> {path}")
            except Exception as e:
                logger.warning(f"Could not extract {ts}: {e}")

        cap.release()
        return extracted_paths