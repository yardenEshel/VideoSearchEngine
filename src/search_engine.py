import json
import logging
import re
from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)


class LocalSearchEngine:
    def __init__(self, captions_file="data/scene_captions.json"):
        self.captions_file = captions_file
        self.data = {}

        try:
            with open(self.captions_file, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            logger.warning("Index file %s not found. Search will be empty.", self.captions_file)

        self.corpus = list(self.data.items())

    def search(self, query, threshold=45, limit=5):
        if not self.data:
            return []

        choices = [text for _, text in self.corpus]

        results = process.extract(
            query,
            choices,
            scorer=fuzz.partial_token_sort_ratio,
            limit=limit,
        )

        matched_scenes = []
        print(f"\n--- Search Results for '{query}' ---")

        for text, score, index in results:
            if score >= threshold:
                scene_num = self.corpus[index][0]
                print(f" > Scene {scene_num} [Score: {score:.0f}]: {text[:80]}...")
                matched_scenes.append(scene_num)

        return matched_scenes

    def get_vocabulary(self):
        words = set()
        for text in self.data.values():
            tokens = re.findall(r"\b\w+\b", text.lower())
            for token in tokens:
                if len(token) > 2:
                    words.add(token)

        return sorted(words)

