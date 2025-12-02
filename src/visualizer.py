import logging
import math
import os
from PIL import Image

logger = logging.getLogger(__name__)


class Visualizer:
    def __init__(self, scenes_folder="data/scenes"):
        self.scenes_folder = scenes_folder

    def create_collage(self, scene_numbers, output_filename="collage.png"):
        if not scene_numbers:
            print("No scenes to visualize.")
            return

        images = []

        for num in scene_numbers:
            found = False
            for filename in os.listdir(self.scenes_folder):
                if not (filename.endswith(".jpg") or filename.endswith(".png")):
                    continue

                try:
                    file_num = str(int(filename.split("_")[1].split(".")[0]))
                except Exception:
                    continue

                if file_num == str(num):
                    path = os.path.join(self.scenes_folder, filename)
                    images.append(Image.open(path))
                    found = True
                    break

            if not found:
                logger.warning("Could not find image for Scene %s", num)

        if not images:
            return

        count = len(images)
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)

        w, h = images[0].size
        w, h = min(w, 512), min(h, 512)

        collage = Image.new("RGB", (cols * w, rows * h), color=(0, 0, 0))

        for idx, img in enumerate(images):
            img = img.resize((w, h))
            row = idx // cols
            col = idx % cols
            collage.paste(img, (col * w, row * h))

        output_path = os.path.join("data", output_filename)
        collage.save(output_path)
        print(f" [Visualizer] Collage saved to: {output_path}")

        try:
            os.system(f"open {output_path}")
        except Exception:
            pass

