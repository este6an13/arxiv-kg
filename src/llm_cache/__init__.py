import json
import os
from kg_generator.types import KnowledgeGraph
from constants import PROJECT_ROOT

class LLMCache:
    def __init__(self):
        self.cache_folder = os.path.join(PROJECT_ROOT, "cache")
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

    def write(self, article_id, data):

        key_takeaway = data["key_takeaway"]
        knowledge_graph = data["knowledge_graph"]

        key_takeaway_filename = os.path.join(self.cache_folder, f"{article_id}.txt")
        with open(key_takeaway_filename, "w") as key_takeaway_file:
            key_takeaway_file.write(key_takeaway)

        knowledge_graph_filename = os.path.join(self.cache_folder, f"{article_id}.json")
        with open(knowledge_graph_filename, "w") as kg_file:
            json.dump(knowledge_graph.json(), kg_file)

    def read(self, article_id):

        key_takeaway_filename = os.path.join(self.cache_folder, f"{article_id}.txt")
        knowledge_graph_filename = os.path.join(self.cache_folder, f"{article_id}.json")

        if not os.path.exists(key_takeaway_filename) or not os.path.exists(knowledge_graph_filename):
            return None

        with open(key_takeaway_filename, "r") as key_takeaway_file:
            key_takeaway = key_takeaway_file.read()

        with open(knowledge_graph_filename, "r") as kg_file:
            kg_data = json.load(kg_file)
            knowledge_graph = KnowledgeGraph.parse_raw(kg_data)

        return {"key_takeaway": key_takeaway, "knowledge_graph": knowledge_graph}
