import os
import json
import logging
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)

class LocalIndexer:
    def __init__(self, scenes_folder="data/scenes", index_file="data/scene_captions.json"):
        self.scenes_folder = scenes_folder
        self.index_file = index_file
        self.model = None
        self.tokenizer = None

    def _load_model(self):
        if self.model is None:
            logger.info("Loading Moondream (Classic Revision 2024-04-02)...")
            # We pin the revision to the version that DOES NOT use pyvips
            model_id = "vikhyatk/moondream2"
            revision = "2024-04-02" 
            
            # Trust remote code is required for Moondream
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                trust_remote_code=True, 
                revision=revision
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)

    def index_scenes(self):
        # 1. Check Cache
        if os.path.exists(self.index_file):
            logger.info(f"Found existing index: {self.index_file}. Loading...")
            with open(self.index_file, "r") as f:
                return json.load(f)

        # 2. Load Model
        self._load_model()
        
        captions = {}
        image_files = sorted(
            [f for f in os.listdir(self.scenes_folder) if f.endswith(('.jpg', '.png'))]
        )
        
        logger.info(f"Starting captioning for {len(image_files)} scenes...")

        for filename in image_files:
            try:
                # Extract Scene Number
                try:
                    scene_num = str(int(filename.split('_')[1].split('.')[0]))
                except:
                    scene_num = filename

                image_path = os.path.join(self.scenes_folder, filename)
                
                try:
                    image = Image.open(image_path)
                    
                    logger.info(f"Processing Scene {scene_num}...")
                    
                    # --- CLASSIC API (Pure PyTorch, No PyVips) ---
                    enc_image = self.model.encode_image(image)
                    caption = self.model.answer_question(
                        enc_image, 
                        "Describe this image.", 
                        self.tokenizer
                    )
                    
                    logger.info(f" > {caption}")
                    captions[scene_num] = caption
                    
                except Exception as e:
                    logger.error(f"Failed to caption {filename}: {e}")

            except Exception as outer_e:
                logger.error(f"Error processing file {filename}: {outer_e}")

        # 3. Save
        with open(self.index_file, "w") as f:
            json.dump(captions, f, indent=4)
            
        return captions