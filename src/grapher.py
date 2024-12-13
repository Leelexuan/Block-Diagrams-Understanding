from lib import get_direct_descendents, get_label
from pathlib import Path
from annotations import generate_annotations_with_bboxes
import numpy as np
import requests
import validators
import subprocess
import random


class Grapher:
    def __init__(self, entity_code):
        self.graph = "graph TD"
        self.root_entity_code = entity_code
        self.root = get_label(entity_code)
        self.vertices = {self.root: 0}
        self.count = 0
        self.img_template = "<img src='{entity_label}' width='50' height='50'>"
        # triplets are related (head, relation, tail)
        self.triplets = set()
        self.explored = set()
        self.edges = set()

    def reset(self):
        self.graph = "graph TD"
        self.vertices = {self.root: 0}
        self.root = self.root
        self.count = 0
        self.triplets = set()
        self.explored = set()
        self.edges = set()

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
        return validators.url(entity_label)

    def is_image_url(self, url: str) -> bool:
        """Checks if a given URL points to a valid image."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                content_type = response.headers.get("content-type")
                return content_type.startswith("image/")
        except requests.RequestException:
            return False
        return False

    def format_entity_label(self, entity_label: str):
        """
        Converts an entity label into the appropriate Mermaid Markdown format.
        If the label is an image URL, it formats it as an <img> tag.
        Otherwise, it formats it as text.
        """
        if self.is_image_url(entity_label):
            return f"A{self.vertices[entity_label]}({self.img_template.format(entity_label=entity_label)})"
        return f'A{self.vertices[entity_label]}("{entity_label}")'

    def add_triplet_to_graph(self, triplet):
        parent, relation, child = triplet
        parent_node = self.format_entity_label(parent)
        child_node = self.format_entity_label(child)

        self.graph += f'\n    {parent_node} -- "{relation}" --> {child_node}'

    # TODO: Change way to sample children. Issues currently: Possible for children to be resampled i.e. duplicates may be present and fixed children to sample results in similar looking tree structures.
    def sample_children(
        self, parent, children, max_children_per_parent=3, accept_images=False
    ) -> list:
        num_children_to_sample = np.random.randint(1, max_children_per_parent)

        num_children = len(children)
        children_sampled = []
        explored = set()
        limit = max_children_per_parent * 5

        while (
            num_children_to_sample > 0
            and num_children_to_sample <= len(children)
            and limit > 0
            and num_children > 0
        ):
            idx = np.random.randint(num_children)
            if idx in explored:
                continue

            explored.add(idx)
            subject = children[idx]
            child = subject["value"]
            relation = subject["property"]

            # if descendent is a URL that is not an image, continue because we don't want to add it to the graph
            if self.is_image_url(child) and not accept_images:
                continue
            elif self.validate_url(child):
                continue

            # sometimes the nodes connect to themselves, so we don't want to add them to the graph
            if child == parent:
                continue

            if self.vertices.get(parent) is None:
                self.count += 1
                self.vertices[parent] = self.count
            if self.vertices.get(child) is None:
                self.count += 1
                self.vertices[child] = self.count

            triplet = (parent, relation, child)

            if triplet not in self.triplets:
                self.triplets.add(triplet)
                self.edges.add((self.vertices[parent], self.vertices[child]))

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
        explored_entities = set()
        depth = 0

        while queue != [] and depth < max_depth:
            parent = queue.pop(0)
            explored_entities.add(parent)
            if parent in explored_entities:
                continue
            children = get_direct_descendents(parent)
            if not children or len(children) == 0:
                continue

            parent_label = get_label(parent)
            if not parent_label or not parent:
                continue

            children_sampled = self.sample_children(parent_label, children)
            queue += children_sampled
            depth += 1

        self.triplets = sorted(
            self.triplets, key=lambda x: (self.vertices[x[0]], self.vertices[x[2]])
        )

        for triplet in self.triplets:
            self.add_triplet_to_graph(triplet)

    def export(self):
        output_folder = Path.cwd() / "output"
        output_folder.mkdir(parents=True, exist_ok=True)

        images_folder = output_folder / "images"
        images_folder.mkdir(parents=True, exist_ok=True)

        svgs_folder = output_folder / "svgs"
        svgs_folder.mkdir(parents=True, exist_ok=True)

        markdown_folder = output_folder / "markdown"
        markdown_folder.mkdir(parents=True, exist_ok=True)

        annotations_folder = output_folder / "annotations"
        annotations_folder.mkdir(parents=True, exist_ok=True)

        md_file = f"{self.root_entity_code}.md"
        img_file = f"{self.root_entity_code}.png"
        svg_file = f"{self.root_entity_code}.svg"
        annotations_file = f"{self.root_entity_code}.xml"

        file_path = markdown_folder / md_file
        image_path = images_folder / img_file
        svg_path = svgs_folder / svg_file
        annotations_path = annotations_folder / annotations_file

        content = f"```mermaid\n{self.graph}\n```"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        command = ["mmdc.cmd", "-i", file_path, "-o", svg_path]
        subprocess.run(command, encoding="utf-8")

        command = ["mmdc.cmd", "-i", file_path, "-o", image_path, "--scale", "4"]
        subprocess.run(command, encoding="utf-8")

        output_svg_path = svgs_folder / (Path(svg_path).stem + "-1.svg")
        xml_annotations = generate_annotations_with_bboxes(output_svg_path, self)

        with open(annotations_path, "w") as f:
            f.write(xml_annotations)


class BlockTransformer(Grapher):
    def __init__(self, entity_code):
        super().__init__(entity_code)
        self.block_types = ["Process", "Decision", "Data", "Connection", "Terminator"]

    def has_children(self, node):
        vertex = self.vertices[node]
        children = [edge[1] for edge in self.edges if edge[0] == vertex]
        return len(children) > 0

    def transform_block(self, node):
        """Transform node based on its type (leaf or non-leaf)."""
        if self.root == node:
            return random.choices(["Terminator", "Process"], weights=[0.8, 0.2], k=1)[0]
        if not self.has_children(node):
            # Randomize leaf nodes: 50/50 chance of being Terminator or Process
            return random.choice(["Terminator", "Process"])
        else:
            # Non-leaf nodes: probabilities for Process, Data, Decision, and Connection
            return random.choices(
                ["Process", "Data", "Decision", "Connection"],
                weights=[0.4, 0.2, 0.2, 0.2],
                k=1,
            )[0]

    def transform_graph(self):
        """Apply transformations to all nodes in the graph and check connections."""
        transformed_graph = {}

        for node, id in self.vertices.items():
            node_class = self.transform_block(node)
            transformed_graph[id] = node_class

        self.vertex_classes = transformed_graph

    def format_entity_label(self, entity_label: str):
        """
        Converts an entity label into the appropriate Mermaid Markdown format.
        If the label is an image URL, it formats it as an <img> tag.
        Otherwise, it formats it as text.
        """
        node_id = self.vertices[entity_label]
        node_class = self.vertex_classes[node_id]

        if self.is_image_url(entity_label):
            label = self.img_template.format(entity_label=entity_label)
        else:
            label = f'"{entity_label}"'

        if node_class == "Terminator":  # Eclipse
            node = f"([{label}])"
        elif node_class == "Process":  # Rectangle
            node = f"[{label}]"
        elif node_class == "Decision":  # Diamond
            node = f"{{{label}}}"
        elif node_class == "Data":  # Parallelogram
            node = f"[/{label}/]"
        elif node_class == "Connection":  # Circle
            node = f"(({label}))"

        return f"A{self.vertices[entity_label]}{node}"

    def add_triplet_to_graph(self, triplet):
        parent, relation, child = triplet
        parent_node = self.format_entity_label(parent)
        child_node = self.format_entity_label(child)

        self.graph += f'\n    {parent_node} -- "{relation}" --> {child_node}'

    def randomize_graph(self, max_depth=10):
        self.reset()
        queue = [self.root_entity_code]
        explored_entities = set()
        depth = 0

        while queue != [] and depth < max_depth:
            parent = queue.pop(0)
            if parent in explored_entities:
                continue
            explored_entities.add(parent)

            children = get_direct_descendents(parent)
            if not children or len(children) == 0:
                continue

            parent_label = get_label(parent)
            print(parent, parent_label)

            children_sampled = self.sample_children(parent_label, children)
            queue += children_sampled
            depth += 1

        self.triplets = sorted(
            self.triplets, key=lambda x: (self.vertices[x[0]], self.vertices[x[2]])
        )

        self.transform_graph()

        for triplet in self.triplets:
            self.add_triplet_to_graph(triplet)

        return self.root_entity_code
