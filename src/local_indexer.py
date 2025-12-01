import json
import logging
import os

from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)


class LocalIndexer:
    def __init__(
        self,
        scenes_folder="data/scenes",
        index_file="data/scene_captions.json",
    ):
        self.scenes_folder = scenes_folder
        self.index_file = index_file
        self.model = None
        self.tokenizer = None

    def _load_model(self):
        """
        Lazily load the Moondream model so we only pay the download cost once.
        """
        if self.model is not None:
            return

        logger.info("Loading Moondream model... (this might take a moment)")
        model_id = "vikhyatk/moondream2"
        revision = "2025-01-09"

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
            revision=revision,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            revision=revision,
        )
        # Uncomment to push the model to CUDA if available inside the container:
        # self.model = self.model.to("cuda")

    def index_scenes(self):
        """
        Generate scene captions and persist them to disk.
        """
        if os.path.exists(self.index_file):
            logger.info("Found existing index %s; loading...", self.index_file)
            with open(self.index_file, "r") as f:
                return json.load(f)

        self._load_model()

        captions = {}
        image_files = sorted(
            f
            for f in os.listdir(self.scenes_folder or ".")
            if f.endswith((".jpg", ".png"))
        )

        logger.info("Starting captioning for %s scenes...", len(image_files))

        for filename in image_files:
            try:
                scene_num = str(int(filename.split("_")[1].split(".")[0]))
            except (IndexError, ValueError):
                scene_num = filename

            image_path = os.path.join(self.scenes_folder, filename)
            image = Image.open(image_path)
            logger.info("Processing scene %s (%s)...", scene_num, filename)

            try:
                result = self.model.caption(image, length="normal")
                captions[scene_num] = result["caption"]
            except Exception as exc:
                logger.error("Failed to caption %s: %s", filename, exc, exc_info=True)

        logger.info("Captioning complete. Saving cache to %s...", self.index_file)
        with open(self.index_file, "w") as f:
            json.dump(captions, f, indent=4)

        return captions
import json
import os

from PIL import Image
from transformers import AutoModelForCausalLM


class LocalIndexer:
    def __init__(self, scenes_folder="data/scenes", index_file="data/scene_captions.json"):
        self.scenes_folder = scenes_folder
        self.index_file = index_file
        self.model = None

    def _load_model(self):
        """
        Load Moondream model lazily.
        """
        if self.model is not None:
            return

        print("[LocalIndexer] Loading Moondream model... (this may take a moment)")
        model_id = "vikhyatk/moondream2"
        revision = "2025-01-09"
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            revision=revision,
        )

    def index_scenes(self):
        """
        Generate scene captions and cache the results.
        """
        if os.path.exists(self.index_file):
            print(f"[LocalIndexer] Found existing index: {self.index_file}. Loading...")
            with open(self.index_file, "r") as f:
                return json.load(f)

        self._load_model()
        captions = {}

        image_files = sorted(
            [f for f in os.listdir(self.scenes_folder) if f.endswith((".jpg", ".png"))]
        )

        print(f"[LocalIndexer] Starting captioning for {len(image_files)} scenes...")

        for filename in image_files:
            try:
                scene_num = str(int(filename.split("_")[1].split(".")[0]))
            except (IndexError, ValueError):
                scene_num = filename

            image_path = os.path.join(self.scenes_folder, filename)
            image = Image.open(image_path)

            print(f"  > Processing Scene {scene_num}...", end="\r")
            try:
                result = self.model.caption(image, length="normal")
                captions[scene_num] = result["caption"]
            except Exception as exc:
                print(f"\n[Error] Failed to caption {filename}: {exc}")

        print(f"\n[LocalIndexer] Captioning complete. Saving to {self.index_file}...")
        with open(self.index_file, "w") as f:
            json.dump(captions, f, indent=4)

        return captions

