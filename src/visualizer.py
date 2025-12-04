import os
import math
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class Visualizer:
    def __init__(self, scenes_folder="data/scenes"):
        self.default_folder = scenes_folder

    def create_collage(self, items, source_folder=None, output_filename="collage.png"):
        """
        Accepts a list of items. 
        - If items are file paths (strings containing '/'), it loads them directly.
        - If items are scene numbers (strings/ints), it looks in self.default_folder.
        """
        if not items:
            print("[Visualizer] No images to visualize.")
            return

        images = []
        folder = source_folder if source_folder else self.default_folder

        for item in items:
            try:
                # Logic A: It is a direct file path (Gemini Mode)
                if isinstance(item, str) and os.path.exists(item):
                    images.append(Image.open(item))
                
                # Logic B: It is a Scene ID (Local Mode)
                else:
                    # Find matching scene_X.jpg
                    found = False
                    for f in os.listdir(folder):
                        # Match scene_1.jpg or scene_001.jpg
                        if f"scene_{str(item).zfill(3)}" in f or f"scene_{item}.jpg" in f:
                            images.append(Image.open(os.path.join(folder, f)))
                            found = True
                            break
            except Exception as e:
                logger.warning(f"Error loading {item}: {e}")

        if not images:
            return

        # Grid Logic
        count = len(images)
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)
        
        # Normalize size (using first image as ref, cap at 512px)
        w, h = images[0].size
        w, h = min(w, 512), min(h, 512)
        
        collage = Image.new('RGB', (cols * w, rows * h))

        for i, img in enumerate(images):
            img = img.resize((w, h))
            r = i // cols
            c = i % cols
            collage.paste(img, (c * w, r * h))

        out_path = os.path.join("data", output_filename)
        collage.save(out_path)
        print(f" [Visualizer] Collage saved to: {out_path}")
        
        # Try to open on Mac
        try:
            os.system(f"open {out_path}")
        except:
            pass