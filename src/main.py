import logging

from video_manager import VideoAssetManager
from scene_processor import SceneProcessor
from local_indexer import LocalIndexer

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the video search engine."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # --- Milestone 1: Download & Split ---
    video_manager = VideoAssetManager()
    video_path = video_manager.download_video("super mario movie trailer")

    scene_processor = SceneProcessor()
    scene_processor.detect_and_save_scenes(video_path, threshold=27.0)

    # --- Milestone 2: The Local Eye ---
    indexer = LocalIndexer()
    captions = indexer.index_scenes()

    logger.info("--- Sample Captions ---")
    for scene_num, text in list(captions.items())[:3]:
        logger.info("Scene %s: %s", scene_num, text)

if __name__ == "__main__":
    main()