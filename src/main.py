from video_manager import VideoAssetManager
from scene_processor import SceneProcessor

def main():
    # 1. Download Video
    video_manager = VideoAssetManager()
    video_path = video_manager.download_video("super mario movie trailer")
    
    # 2. Process Scenes
    # EXERCISE GOAL: Tweaking the threshold.
    # Start with 27.0. If you get > 80 scenes, increase it (e.g., 35.0).
    # If you get < 50 scenes, decrease it (e.g., 20.0).
    current_threshold = 10.0 
    
    scene_processor = SceneProcessor()
    scene_processor.detect_and_save_scenes(video_path, threshold=current_threshold)

if __name__ == "__main__":
    main()