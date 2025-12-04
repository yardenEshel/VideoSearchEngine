import logging
import os
import sys

# Import all modules
from video_manager import VideoAssetManager
from scene_processor import SceneProcessor
from local_indexer import LocalIndexer
from search_engine import LocalSearchEngine
from visualizer import Visualizer
# New Import
from gemini_search import GeminiVideoSearch

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

def main():
    print("========================================")
    print("      AI VIDEO SEARCH ENGINE v2.0       ")
    print("========================================")
    
    # 1. Download Video (Common step)
    vm = VideoAssetManager()
    vid_path = vm.download_video("super mario movie trailer")
    
    # 2. Select Mode
    print("\nSelect Search Mode:")
    print("1. Local Image Model (Moondream/BLIP) - Search by keywords (e.g. 'mario')")
    print("2. Cloud Video Model (Google Gemini)  - Search by understanding (e.g. 'when does he jump?')")
    
    mode = input("\nEnter 1 or 2: ").strip()
    visualizer = Visualizer()

    # --- MODE 1: LOCAL ---
    if mode == "1":
        sp = SceneProcessor()
        sp.detect_and_save_scenes(vid_path)
        
        indexer = LocalIndexer()
        indexer.index_scenes()

        search_engine = LocalSearchEngine()
        vocab = search_engine.get_vocabulary()
        
        session = PromptSession(completer=WordCompleter(vocab))
        print(f"\n[Local] Ready! Index contains {len(vocab)} words.")

        while True:
            try:
                query = session.prompt("\nSearch using a word: ")
                if query.lower() in ['exit', 'quit']: break
                
                matches = search_engine.search(query)
                visualizer.create_collage(matches)
            except KeyboardInterrupt:
                break

    # --- MODE 2: CLOUD ---
    elif mode == "2":
        if not os.getenv("GOOGLE_API_KEY"):
            print("Error: GOOGLE_API_KEY is missing in .env file.")
            return

        gemini = GeminiVideoSearch(video_path=vid_path)
        
        # Upload to Google
        gemini.upload_video()
        
        print("\n[Cloud] Ready. The AI has watched the video.")
        print("Type 'exit' to quit.")

        while True:
            try:
                query = input("\nUsing a video model. What would you like me to find in the video? ")
                if query.lower() in ['exit', 'quit']: break
                
                # 1. Get Timestamps
                timestamps = gemini.search_video(query)
                
                if timestamps:
                    print(f" > Found timestamps: {timestamps}")
                    # 2. Extract Frames
                    files = gemini.extract_frames(timestamps)
                    # 3. Create Collage
                    visualizer.create_collage(files)
                else:
                    print(" > No matching moments found.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()