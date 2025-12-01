import contextlib
import logging
import os
import sys

from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.scene_manager import save_images

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def suppress_ffmpeg_output():
    """Temporarily redirect file descriptor 2 (stderr) to /dev/null."""
    with open(os.devnull, "w") as devnull:
        saved_stderr = os.dup(sys.stderr.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())
        try:
            yield
        finally:
            os.dup2(saved_stderr, sys.stderr.fileno())
            os.close(saved_stderr)

class SceneProcessor:
    def __init__(self, output_folder="data/scenes"):
        self.output_folder = output_folder
        # Ensure the output directory is clean/ready
        os.makedirs(self.output_folder, exist_ok=True)

    def detect_and_save_scenes(self, video_path, threshold=27.0):
        """
        Detects scenes and saves the middle frame of each scene as an image.
        threshold: Lower = more sensitive (more scenes). Higher = less sensitive (fewer scenes).
        """
        logger.info("Processing %s with threshold %s...", video_path, threshold)
        
        # Open video and create a scene manager
        video = open_video(video_path)
        scene_manager = SceneManager()
        
        # Add the ContentDetector algorithm
        scene_manager.add_detector(ContentDetector(threshold=threshold))
        
        # Detect scenes
        with suppress_ffmpeg_output():
            scene_manager.detect_scenes(video, show_progress=True)
        scene_list = scene_manager.get_scene_list()
        
        count = len(scene_list)
        logger.info("Found %s scenes.", count)
        
        if count == 0:
            logger.warning("No scenes found. Try lowering the threshold.")
            return 0

        # Save images
        logger.info("Saving scene images...")
        with suppress_ffmpeg_output():
            save_images(
                scene_list,
                video,
                num_images=1,
                image_name_template="scene_$SCENE_NUMBER",
                output_dir=self.output_folder,
            )
        
        return count