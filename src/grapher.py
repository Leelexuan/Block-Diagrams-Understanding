from lib import get_direct_descendents, get_label
import numpy as np
import requests
import subprocess
import os


class Grapher:
    def __init__(self, entity_code):
        self.graph = "graph TD"
        self.root_entity_code = entity_code
        self.root = get_label(entity_code)
        self.vertices = {self.root: 0}
        self.edges = {}
        self.count = 0
        self.img_template = "<img src='{entity_label}' width='50' height='50'>"
        # triplets are related (head, relation, tail)
        self.triplets = set()
        self.explored = set()

    def reset(self):
        self.graph = "graph TD"
        self.vertices = {self.root: 0}
        self.edges = {}
        self.root = self.root
        self.count = 0
        self.triplets = set()
        self.explored = set()

    def is_image_url(self, string: str):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url=string, headers=headers)
            if response.status_code == 200:
                content_type = response.headers.get("content-type")
                return content_type.startswith("image/")
        except requests.RequestException:
            return False

    def validate_url(self, entity_label: str):
        if self.is_image_url(entity_label):
            return f"A{self.vertices[entity_label]}({self.img_template.format(entity_label=entity_label)})"
        return f'A{self.vertices[entity_label]}("{entity_label}")'

    # TODO: Change way to sample children. Issues currently: Possible for children to be resampled i.e. duplicates may be present and fixed children to sample results in similar looking tree structures.
    def sample_children(self, parent, children, max_children_per_parent=3) -> list:
        num_children_to_sample = np.random.randint(1, max_children_per_parent)

        num_children = len(children)
        children_sampled = []
        explored = set()
        limit = max_children_per_parent * 5

        while (
            num_children_to_sample <= len(children)
            and num_children_to_sample != 0
            and limit != 0
        ):
            idx = np.random.randint(num_children)
            if idx in explored:
                continue

            explored.add(idx)
            subject = children[idx]
            child = subject["value"]
            relation = subject["property"]

            if self.vertices.get(child) is None:
                self.count += 1
                self.vertices[child] = self.count

            triplet = (parent, relation, child)

            if triplet not in self.triplets:
                self.triplets.add(triplet)
                parent_node = self.validate_url(parent)
                child_node = self.validate_url(child)

                self.graph += f'\n    {parent_node} -- "{relation}" --> {child_node}'

            # if descendent is not a passable entity, then do not add to sample list
            child_entity_code = subject["qid"]
            if child_entity_code:
                children_sampled.append(child_entity_code)
                num_children_to_sample -= 1
            limit -= 1

        return children_sampled

    def randomize_graph(self, max_depth=10):
        self.reset()
        queue = [self.root_entity_code]
        depth = 0

        while queue != [] and depth < max_depth:
            parent = queue.pop(0)
            children = get_direct_descendents(parent)

            parent_label = get_label(parent)
            print(parent, parent_label)

            children_sampled = self.sample_children(parent_label, children)
            queue += children_sampled
            depth += 1

    def export(self):
        cwd = os.getcwd()
        output_folder = "output"
        md_file = "file.md"
        img_file = "img.png"

        file_path = os.path.join(cwd, output_folder, md_file)
        image_path = os.path.join(cwd, output_folder, img_file)

        content = f"```mermaid\n{self.graph}\n```"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        command = ["mmdc.cmd", "-i", file_path, "-o", image_path, "--scale", "10"]

        subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
