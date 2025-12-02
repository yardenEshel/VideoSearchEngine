import logging
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

from video_manager import VideoAssetManager
from scene_processor import SceneProcessor
from local_indexer import LocalIndexer
from search_engine import LocalSearchEngine
from visualizer import Visualizer


logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")

def main():
    print("========================================")
    print("   LOCAL VIDEO SEARCH ENGINE (v1.0)   ")
    print("========================================")

    vm = VideoAssetManager()
    vid_path = vm.download_video("super mario movie trailer")

    sp = SceneProcessor()
    sp.detect_and_save_scenes(vid_path)

    indexer = LocalIndexer()
    indexer.index_scenes()

    print("\n[System] Initializing Search Engine...")
    search_engine = LocalSearchEngine()
    visualizer = Visualizer()

    vocab = search_engine.get_vocabulary()
    completer = WordCompleter(vocab, ignore_case=True)

    style = Style.from_dict({"prompt": "#00aa00 bold"})
    session = PromptSession(completer=completer, style=style)

    print(f"\n[System] Ready! Index contains {len(vocab)} unique words.")
    print("Type a word to search (e.g., 'mario', 'fire'). Type 'exit' to quit.")

    while True:
        try:
            user_input = session.prompt("\nSearch the video using a word: ")

            if user_input.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input.strip():
                continue

            matches = search_engine.search(user_input, threshold=50)

            if matches:
                visualizer.create_collage(matches)
            else:
                print("No matches found. Try a different word.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as exc:
            print(f"An error occurred: {exc}", file=sys.stderr)

if __name__ == "__main__":
    main()