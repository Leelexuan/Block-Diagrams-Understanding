from xml.etree import ElementTree as ET
from xml.dom import minidom
from PIL import Image, ImageDraw
from svgpathtools import parse_path
from pathlib import Path
import shutil
import re
import math


def generate_annotations_with_bboxes(svg_path, grapher):
    """Parse the SVG file to extract bounding boxes for all elements."""
    tree = ET.parse(svg_path)
    root = tree.getroot()

    view_box = root.attrib.get("viewBox")
    view_box = view_box.split(" ")
    view_box = [float(x) for x in view_box]

    # Process nodes
    node_label_bboxes, node_bboxes = process_nodes(root)

    # Process edges
    edge_bboxes = process_edges(root)

    # Process edge labels
    edge_label_bboxes = process_edge_labels(root)

    cwd = Path.cwd()

    images_folder = cwd / "output" / "images"
    output_folder_for_images_with_bbox_annotations = (
        cwd / "output" / "images_with_bboxes"
    )
    output_folder_for_images_with_bbox_annotations.mkdir(parents=True, exist_ok=True)

    image_filepath = str(images_folder / (Path(svg_path).stem + ".png"))
    file_name = str(Path(svg_path).stem + ".png")
    save_path = str(output_folder_for_images_with_bbox_annotations / file_name)

    draw_bounding_boxes(
        file_path=images_folder / file_name,
        bounding_boxes=edge_label_bboxes,
        save_path=save_path,
        color="yellow",
        svg_view_box=view_box,
    )
    draw_bounding_boxes(
        file_path=save_path,
        bounding_boxes=node_bboxes,
        save_path=save_path,
        color="red",
        svg_view_box=view_box,
    )
    draw_bounding_boxes(
        file_path=save_path,
        bounding_boxes=node_label_bboxes,
        save_path=save_path,
        color="green",
        svg_view_box=view_box,
    )
    draw_bounding_boxes(
        file_path=save_path,
        bounding_boxes=edge_bboxes,
        save_path=save_path,
        color="blue",
        svg_view_box=view_box,
    )

    # Now we save all annotation as xml file much like the original dataset
    annotation = ET.Element("annotation")
    filename = ET.SubElement(annotation, "filename")
    filename.text = str(Path(svg_path).stem + ".png")

    image = Image.open(image_filepath)
    image = crop_image(image, view_box)
    image.save(image_filepath)

    size = ET.SubElement(annotation, "size")
    width = ET.SubElement(size, "width")
    width.text = str(image.size[0])
    height = ET.SubElement(size, "height")
    height.text = str(image.size[1])
    depth = ET.SubElement(size, "depth")
    depth.text = str(3)

    segmented = ET.SubElement(annotation, "segmented")
    segmented.text = "0"

    for idx, bounding_boxes in enumerate(
        [node_bboxes, edge_bboxes, edge_label_bboxes, node_label_bboxes]
    ):
        for box in bounding_boxes:
            text, ((xmin, ymin), (xmax, ymax)) = box
            obj = ET.SubElement(annotation, "object")

            name = ET.SubElement(obj, "name")
            if idx == 1:
                name.text = "arrow"
            elif idx == 2 or idx == 3:
                name.text = "text"
            else:
                if hasattr(grapher, "vertex_classes"):
                    vertex_id = grapher.vertices[text]
                    vertex_class = grapher.vertex_classes[vertex_id]
                    name.text = vertex_class.lower()
                else:
                    name.text = "process"

            pose = ET.SubElement(obj, "pose")
            pose.text = "Unspecified"
            truncated = ET.SubElement(obj, "truncated")
            truncated.text = "0"
            difficult = ET.SubElement(obj, "difficult")
            difficult.text = "0"

            bndbox = ET.SubElement(obj, "bndbox")
            xmin_element = ET.SubElement(bndbox, "xmin")
            xmin_element.text = str(xmin)
            ymin_element = ET.SubElement(bndbox, "ymin")
            ymin_element.text = str(ymin)
            xmax_element = ET.SubElement(bndbox, "xmax")
            xmax_element.text = str(xmax)
            ymax_element = ET.SubElement(bndbox, "ymax")
            ymax_element.text = str(ymax)

        xml_str = ET.tostring(annotation, encoding="utf-8")
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="\t")

    return pretty_xml


def validate_diamond(points: list[tuple[float, float]]):
    """Check if the points form a diamond shape."""
    # Check if the points form a diamond shape
    if len(points) != 4:
        return False

    sides = [math.dist(points[i], points[(i + 1) % 4]) for i in range(4)]

    if not all(math.isclose(sides[i], sides[0], rel_tol=1e-6) for i in range(4)):
        return False

    mid_diag1 = ((points[0][0] + points[2][0]) / 2, (points[0][1] + points[2][1]) / 2)
    mid_diag2 = ((points[1][0] + points[3][0]) / 2, (points[1][1] + points[3][1]) / 2)

    if not (
        math.isclose(mid_diag1[0], mid_diag2[0], rel_tol=1e-6)
        and math.isclose(mid_diag1[1], mid_diag2[1], rel_tol=1e-6)
    ):
        return False

    return True


def process_nodes(root):
    """
    Node have 1 transformation and 1 rect, so we can just apply the transformation to the rect.
    """
    ns = {"svg": "http://www.w3.org/2000/svg"}
    node_bboxes = []
    node_label_bboxes = []
    root_transform = None
    child_transform = None
    rect_dimensions = None
    node_label_text = None

    for element in root.findall(".//svg:g", ns):
        element_class = element.attrib.get("class")
        if element_class and element_class.startswith("nodes"):
            for node in element:
                root_transform = node.attrib.get("transform")
                for children in node:
                    if "polygon" in children.tag:

                        # child_transform = children.attrib.get("transform")
                        points = children.attrib.get("points", "")
                        if points:
                            all_points = []
                            pairs = points.split(" ")
                            for pair in pairs:
                                x, y = pair.split(",")
                                x, y = float(x), float(y)
                                all_points.append((x, y))

                                min_x = min(point[0] for point in all_points)
                                max_x = max(point[0] for point in all_points)
                                min_y = min(point[1] for point in all_points)
                                max_y = max(point[1] for point in all_points)

                                rect_dimensions = (max_x - min_x, max_y - min_y)

                            transform_str = children.attrib.get("transform")
                            match = re.match(
                                r"translate\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)",
                                transform_str,
                            )
                            if match:
                                dx, dy = float(match.group(1)), float(match.group(2))
                                if validate_diamond(all_points):
                                    child_transform = f"translate({dx}, {-dy})"
                                else:
                                    child_transform = f"translate({dx-11.3333}, {-dy})"

                    elif "circle" in children.tag:
                        radius = float(children.attrib.get("r"))
                        cx, cy = float(children.attrib.get("width")), float(
                            children.attrib.get("height")
                        )
                        xmin, xmax, ymin, ymax = (
                            cx - radius,
                            cx + radius,
                            cy - radius,
                            cy + radius,
                        )
                        rect_dimensions = (xmax - xmin, ymax - ymin)
                        child_transform = f"translate({-radius}, {-radius})"

                    elif "rect" in children.tag:
                        rect_transform = children.attrib.get("x"), children.attrib.get(
                            "y"
                        )
                        child_transform = (
                            f"translate({rect_transform[0]}, {rect_transform[1]})"
                        )
                        rect_dimensions = float(children.attrib.get("width")), float(
                            children.attrib.get("height")
                        )

                    if children.attrib.get("class") == "label":
                        node_label_child_transform = children.attrib.get("transform")
                        for label in children:
                            if label.get("height") and label.get("width"):
                                node_label_height = float(label.get("height"))
                                node_label_width = float(label.get("width"))
                            for div in label:
                                for span in div:
                                    node_label_text = span.text
                                    if not node_label_text:
                                        for p in span:
                                            node_label_text = p.text

                bbox = calculate_bounding_box(
                    root_transform,
                    child_transform,
                    rect_dimensions[0],
                    rect_dimensions[1],
                )

                node_label_bbox = calculate_bounding_box(
                    root_transform,
                    node_label_child_transform,
                    node_label_width,
                    node_label_height,
                )

                if node_label_text:
                    node_label_bboxes.append((node_label_text, node_label_bbox))
                if bbox:
                    node_bboxes.append((node_label_text, bbox))

    return node_label_bboxes, node_bboxes


def process_edges(root):
    ns = {"svg": "http://www.w3.org/2000/svg"}
    bboxes = []

    for element in root.findall(".//svg:g", ns):
        element_class = element.attrib.get("class")
        if element_class and element_class.startswith("edgePaths"):
            for edge in element:
                id = edge.attrib.get("id")
                path = edge.attrib.get("d")
                if path:
                    # xmin, xmax, ymin, ymax
                    xmin, xmax, ymin, ymax = parse_path(path).bbox()
                    if xmin == xmax:
                        xmax += 1
                    if ymin == ymax:
                        ymax += 1

                bboxes.append((id, ((xmin, ymin), (xmax, ymax))))

    return bboxes


def process_edge_labels(root):
    ns = {"svg": "http://www.w3.org/2000/svg"}
    bboxes = []
    edge_label_text = None

    for element in root.findall(".//svg:g", ns):
        element_class = element.attrib.get("class")
        if element_class and element_class.startswith("edgeLabels"):
            for edge_label in element:
                root_transform = edge_label.attrib.get("transform")
                for label in edge_label:
                    child_transform = label.attrib.get("transform")
                    for foreignObject in label:
                        child_dimensions = float(
                            foreignObject.attrib.get("width")
                        ), float(foreignObject.attrib.get("height"))
                        for div in foreignObject:
                            for span in div:
                                edge_label_text = span.text
                                if not edge_label_text:
                                    for p in span:
                                        edge_label_text = p.text

                bbox = calculate_bounding_box(
                    root_transform,
                    child_transform,
                    child_dimensions[0],
                    child_dimensions[1],
                )

                if edge_label_text:
                    bboxes.append((edge_label_text, bbox))

    return bboxes


def apply_transformations(transform_str, initial_x=0, initial_y=0):
    """Apply the transformation string (like 'translate(x, y)') to the given coordinates."""
    # Parse the transform string for translate(x, y)
    match = re.match(r"translate\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)", transform_str)
    if match:
        dx, dy = float(match.group(1)), float(match.group(2))
        return initial_x + dx, initial_y + dy
    else:
        raise ValueError(f"Unsupported transformation string: {transform_str}")


def calculate_bounding_box(root_transform, child_transform, child_width, child_height):
    """Calculate the final bounding box given transformations and child dimensions."""
    # Apply root transformation
    root_x, root_y = apply_transformations(root_transform)

    # Apply child transformation relative to root
    child_x, child_y = apply_transformations(child_transform, root_x, root_y)

    # Calculate the bounding box of the child element
    top_left_x = child_x
    top_left_y = child_y
    bottom_right_x = child_x + child_width
    bottom_right_y = child_y + child_height

    return (top_left_x, top_left_y), (bottom_right_x, bottom_right_y)


def add_bboxes_to_svg(svg_path, bboxes, output_path, colour):
    """
    Adds bounding boxes (rectangles) to the SVG and saves it.

    :param svg_path: The path to the input SVG file.
    :param bboxes: A list of bounding boxes in the form of (xmin, ymin, xmax, ymax).
    :param output_path: The path where the modified SVG file will be saved.
    """
    # Parse the SVG file
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Add each bounding box as a <rect> element
    for bbox in bboxes:
        text, ((xmin, ymin), (xmax, ymax)) = bbox

        # Create a <rect> element for the bounding box
        rect = ET.Element(
            "{http://www.w3.org/2000/svg}rect",
            {
                "x": str(xmin),
                "y": str(ymin),
                "width": str(xmax - xmin),
                "height": str(ymax - ymin),
                "stroke": colour,
                "fill": "none",  # No fill, just the border
                "stroke-width": "0.5",  # Border width
            },
        )

        # Append the rectangle to the root of the SVG
        root.append(rect)

    # Write the modified SVG to a new file
    tree.write(output_path)


def scale_and_map_bounding_box(bounding_box, svg_viewbox, png_size):
    """
    Scale SVG bounding box coordinates to fit a PNG image.

    Args:
        bounding_box (tuple): Bounding box coordinates ((xmin, ymin), (xmax, ymax)).
        svg_viewbox (tuple): SVG viewBox dimensions (min_x, min_y, width, height).
        png_size (tuple): Target PNG dimensions (width, height).

    Returns:
        tuple: Scaled bounding box coordinates for the PNG space.
    """
    # Unpack bounding box and SVG viewbox values
    (xmin, ymin), (xmax, ymax) = bounding_box
    viewbox_min_x, viewbox_min_y, viewbox_width, viewbox_height = svg_viewbox
    png_width, png_height = png_size

    # Normalize bounding box coordinates relative to the SVG viewBox
    normalized_xmin = (xmin - viewbox_min_x) / viewbox_width
    normalized_xmax = (xmax - viewbox_min_x) / viewbox_width
    normalized_ymin = (ymin - viewbox_min_y) / viewbox_height
    normalized_ymax = (ymax - viewbox_min_y) / viewbox_height

    # Map normalized coordinates to actual PNG dimensions
    scaled_xmin = normalized_xmin * png_width
    scaled_xmax = normalized_xmax * png_width
    scaled_ymin = normalized_ymin * png_height
    scaled_ymax = normalized_ymax * png_height

    # Return mapped bounding box
    return (scaled_xmin, scaled_ymin), (scaled_xmax, scaled_ymax)


def crop_image(img, viewbox):
    """
    Crop extra padding from the exported PNG based on the viewBox offsets.

    Args:
        image_path (str): Path to the image file to crop.
        viewbox (tuple): SVG viewBox offsets and dimensions.
        save_path (str): Path to save the cropped image.
    """
    # Calculate how much to crop based on offsets (-8) and scale
    viewbox_min_x, viewbox_min_y, viewbox_width, viewbox_height = viewbox
    # Determine scale ratios
    scale_x = img.width / viewbox_width
    scale_y = img.height / viewbox_height

    # Map the offsets to pixel space
    offset_x = -viewbox_min_x * scale_x
    offset_y = -viewbox_min_y * scale_y / 2

    # Perform cropping calculations
    crop_box = (0, 0, img.width - offset_x, img.height - offset_y)

    # Crop the image to remove the extra padding
    cropped_img = img.crop(crop_box)

    return cropped_img


def draw_bounding_boxes(file_path, bounding_boxes, save_path, color, svg_view_box=None):
    """
    Draw bounding boxes on the given PNG file.

    Args:
        file_path (str): Path to the input image file (PNG).
        bounding_boxes (list): List of bounding boxes defined as ((xmin, ymin), (xmax, ymax)).
        save_path (str): Path to save the resulting PNG with bounding boxes.
        svg_view_box (tuple): Optional SVG viewBox dimensions for correct scaling offsets.
    """
    try:
        image = Image.open(file_path).convert("RGB")
        """Mermaid CLI Export to PNG seems to add some right and bottom padding to the image, so we need to crop it to retain the original SVG viewbox dimensions..."""

        image = crop_image(image, svg_view_box)

        draw = ImageDraw.Draw(image)

        # Iterate over bounding boxes
        for bbox in bounding_boxes:
            text, ((xmin, ymin), (xmax, ymax)) = bbox
            if svg_view_box:
                # Scale bounding boxes with the given svg_view_box
                mapped_box = scale_and_map_bounding_box(
                    bounding_box=[(xmin, ymin), (xmax, ymax)],
                    svg_viewbox=svg_view_box,
                    png_size=image.size,
                )
                (xmin, ymin), (xmax, ymax) = mapped_box

            # Draw the bounding box
            draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=3)

        # Save the image
        image.save(save_path)

    except Exception as e:
        print(f"An error occurred: {e}")


def sync_images_and_labels(base_folder):
    base_folder = Path(base_folder)
    images_folder = base_folder / "images"
    labels_folder = base_folder / "annotations"

    isolated_folder = base_folder / "isolated"
    isolated_folder.mkdir(exist_ok=True)

    image_files = {Path(f).stem.replace('-1', '') for f in images_folder.glob("*.png")}
    labels_files = {Path(f).stem for f in labels_folder.glob("*.xml")}

    unmatched_images = image_files - labels_files
    unamtched_labels = labels_files - image_files

    for image in unmatched_images:
        shutil.move(images_folder / (image + "-1.png"), isolated_folder)

    for label in unamtched_labels:
        shutil.move(labels_folder / (label + ".xml"), isolated_folder)
