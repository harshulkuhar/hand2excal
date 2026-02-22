"""
Excalidraw JSON builder: Converts structured flowchart data
(nodes + arrows) into a valid .excalidraw JSON file.
"""

import json
import math
import random
import string
import time


def _generate_id() -> str:
    """Generate a unique Excalidraw element ID."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=20))


def _seed() -> int:
    """Generate a random seed for Excalidraw rendering."""
    return random.randint(1, 2**31 - 1)


def _timestamp() -> int:
    """Current timestamp in milliseconds."""
    return int(time.time() * 1000)


# ---------- Color helpers ----------

_COLOR_MAP = {
    "red": "#e03131",
    "blue": "#1971c2",
    "green": "#2f9e44",
    "yellow": "#f08c00",
    "orange": "#e8590c",
    "purple": "#9c36b5",
    "pink": "#c2255c",
    "black": "#1e1e1e",
    "gray": "#868e96",
    "grey": "#868e96",
    "white": "#ffffff",
    "brown": "#862e09",
    "cyan": "#0c8599",
    "teal": "#099268",
    "navy": "#1864ab",
    "lime": "#66a80f",
}


def _normalize_color(color: str) -> str:
    """Normalize a color string to a hex code."""
    if not color or color == "transparent":
        return "transparent"
    color = color.lower().strip()
    if color.startswith("#"):
        return color
    return _COLOR_MAP.get(color, "#1e1e1e")


# ---------- Element builders ----------

def _base_element(
    element_type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    stroke_color: str = "#1e1e1e",
    bg_color: str = "transparent",
) -> dict:
    """Create a base Excalidraw element with common properties."""
    return {
        "id": _generate_id(),
        "type": element_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": _normalize_color(stroke_color),
        "backgroundColor": _normalize_color(bg_color),
        "fillStyle": "solid" if bg_color and bg_color != "transparent" else "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "index": None,
        "roundness": None,
        "seed": _seed(),
        "version": 1,
        "versionNonce": _seed(),
        "isDeleted": False,
        "boundElements": [],
        "updated": _timestamp(),
        "link": None,
        "locked": False,
    }


def _create_shape(node: dict) -> dict:
    """Create a shape element from a node definition."""
    shape_type = node.get("type", "rectangle")
    element = _base_element(
        element_type=shape_type,
        x=node.get("x", 0),
        y=node.get("y", 0),
        width=node.get("width", 150),
        height=node.get("height", 60),
        stroke_color=node.get("strokeColor", "#1e1e1e"),
        bg_color=node.get("backgroundColor", "transparent"),
    )

    # Roundness settings
    if shape_type == "rectangle":
        if node.get("rounded", False):
            element["roundness"] = {"type": 3}
        else:
            element["roundness"] = {"type": 3}  # Slight rounding looks better
    elif shape_type == "ellipse":
        element["roundness"] = {"type": 2}
    elif shape_type == "diamond":
        element["roundness"] = {"type": 2}

    return element


def _create_text(
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    stroke_color: str = "#1e1e1e",
    font_size: int = 16,
    container_id: str | None = None,
) -> dict:
    """Create a text element, optionally bound to a container."""
    element = _base_element(
        element_type="text",
        x=x,
        y=y,
        width=width,
        height=height,
        stroke_color=stroke_color,
    )
    element["text"] = text
    element["fontSize"] = font_size
    element["fontFamily"] = 5  # Excalidraw default (Excalifont)
    element["textAlign"] = "center"
    element["verticalAlign"] = "middle" if container_id else "top"
    element["containerId"] = container_id
    element["originalText"] = text
    element["autoResize"] = True
    element["lineHeight"] = 1.25
    # Text elements don't have roundness/fill
    element["backgroundColor"] = "transparent"
    element["fillStyle"] = "solid"

    return element


def _create_arrow(
    from_element: dict,
    to_element: dict,
    label: str = "",
    stroke_color: str = "#1e1e1e",
) -> tuple[dict, dict | None]:
    """
    Create an arrow element connecting two shapes.
    Returns (arrow_element, optional_label_text_element).
    """
    GAP = 14  # spacing between arrow endpoints and shape edges

    # Calculate connection points (center of each shape)
    from_cx = from_element["x"] + from_element["width"] / 2
    from_cy = from_element["y"] + from_element["height"] / 2
    to_cx = to_element["x"] + to_element["width"] / 2
    to_cy = to_element["y"] + to_element["height"] / 2

    # Determine edge connection points based on relative positions
    dx = to_cx - from_cx
    dy = to_cy - from_cy

    # Start point: offset OUTSIDE the source shape edge
    if abs(dx) > abs(dy):
        if dx > 0:
            start_x = from_element["x"] + from_element["width"] + GAP
            start_y = from_cy
        else:
            start_x = from_element["x"] - GAP
            start_y = from_cy
    else:
        if dy > 0:
            start_x = from_cx
            start_y = from_element["y"] + from_element["height"] + GAP
        else:
            start_x = from_cx
            start_y = from_element["y"] - GAP

    # End point: offset OUTSIDE the target shape edge
    if abs(dx) > abs(dy):
        if dx > 0:
            end_x = to_element["x"] - GAP
            end_y = to_cy
        else:
            end_x = to_element["x"] + to_element["width"] + GAP
            end_y = to_cy
    else:
        if dy > 0:
            end_x = to_cx
            end_y = to_element["y"] - GAP
        else:
            end_x = to_cx
            end_y = to_element["y"] + to_element["height"] + GAP

    # Arrow points are relative to the arrow's x, y
    arrow_x = start_x
    arrow_y = start_y
    rel_end_x = end_x - start_x
    rel_end_y = end_y - start_y

    arrow = _base_element(
        element_type="arrow",
        x=arrow_x,
        y=arrow_y,
        width=abs(rel_end_x),
        height=abs(rel_end_y),
        stroke_color=stroke_color,
    )
    arrow["points"] = [[0, 0], [rel_end_x, rel_end_y]]
    arrow["lastCommittedPoint"] = None
    arrow["startArrowhead"] = None
    arrow["endArrowhead"] = "arrow"
    arrow["roundness"] = {"type": 2}

    # Bindings: connect arrow to shapes
    arrow["startBinding"] = {
        "elementId": from_element["id"],
        "focus": 0,
        "gap": GAP,
        "fixedPoint": None,
    }
    arrow["endBinding"] = {
        "elementId": to_element["id"],
        "focus": 0,
        "gap": GAP,
        "fixedPoint": None,
    }

    # Create label text if present
    label_element = None
    if label and label.strip():
        mid_x = arrow_x + rel_end_x / 2
        mid_y = arrow_y + rel_end_y / 2
        label_width = max(len(label) * 9, 40)
        label_element = _create_text(
            text=label.strip(),
            x=mid_x - label_width / 2,
            y=mid_y - 10,
            width=label_width,
            height=20,
            stroke_color=stroke_color,
            font_size=14,
            container_id=arrow["id"],
        )
        arrow["boundElements"] = [{"id": label_element["id"], "type": "text"}]

    return arrow, label_element


def build_excalidraw(flowchart_data: dict) -> dict:
    """
    Build a complete Excalidraw JSON structure from flowchart data.

    Args:
        flowchart_data: dict with 'nodes' and 'arrows' as returned by vision module.

    Returns:
        Complete Excalidraw JSON dict ready to be saved as .excalidraw file.
    """
    elements = []
    node_id_to_element = {}  # maps our node id → excalidraw element

    # --- 1. Create shape elements for each node ---
    for node in flowchart_data.get("nodes", []):
        shape = _create_shape(node)
        node_id_to_element[node["id"]] = shape

        # Create bound text label
        label_text = node.get("label", "").strip()
        if label_text:
            # Estimate text dimensions
            font_size = 16
            lines = label_text.split("\n")
            max_line_len = max(len(line) for line in lines)
            text_width = min(max_line_len * 9, shape["width"] - 10)
            text_height = len(lines) * font_size * 1.25

            text_el = _create_text(
                text=label_text,
                x=shape["x"] + (shape["width"] - text_width) / 2,
                y=shape["y"] + (shape["height"] - text_height) / 2,
                width=text_width,
                height=text_height,
                stroke_color=shape["strokeColor"],
                font_size=font_size,
                container_id=shape["id"],
            )

            # Bind text to shape
            shape["boundElements"].append({"id": text_el["id"], "type": "text"})
            elements.append(shape)
            elements.append(text_el)
        else:
            elements.append(shape)

    # --- 2. Create arrow elements ---
    for arrow_def in flowchart_data.get("arrows", []):
        from_el = node_id_to_element.get(arrow_def.get("from_id"))
        to_el = node_id_to_element.get(arrow_def.get("to_id"))

        if not from_el or not to_el:
            continue  # skip arrows with invalid references

        arrow_el, label_el = _create_arrow(
            from_element=from_el,
            to_element=to_el,
            label=arrow_def.get("label", ""),
            stroke_color=arrow_def.get("strokeColor", "#1e1e1e"),
        )

        # Register arrow as bound element on the connected shapes
        from_el["boundElements"].append({"id": arrow_el["id"], "type": "arrow"})
        to_el["boundElements"].append({"id": arrow_el["id"], "type": "arrow"})

        elements.append(arrow_el)
        if label_el:
            elements.append(label_el)

    # --- 3. Assemble the .excalidraw structure ---
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": 20,
            "gridStep": 5,
            "gridModeEnabled": False,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }


def build_excalidraw_json(flowchart_data: dict) -> str:
    """Build Excalidraw JSON and return as formatted string."""
    return json.dumps(build_excalidraw(flowchart_data), indent=2)
