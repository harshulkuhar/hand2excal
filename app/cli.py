"""
CLI interface for hand-to-excalidraw conversion.
Usage: python -m app.cli input.jpg -o output.excalidraw
"""

import argparse
import sys
from pathlib import Path

from .vision import extract_flowchart_from_image
from .excalidraw_builder import build_excalidraw_json


def main():
    parser = argparse.ArgumentParser(
        description="Convert a hand-drawn flowchart image to an Excalidraw file.",
        prog="hand2excalidraw",
    )
    parser.add_argument(
        "image",
        type=str,
        help="Path to the hand-drawn flowchart image (JPG, PNG, WebP)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output .excalidraw file path (default: <input_name>.excalidraw)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print the JSON output (default: True)",
    )

    args = parser.parse_args()

    # Validate input
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    if not image_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".heic"}:
        print(f"Warning: Unusual image extension '{image_path.suffix}'. Proceeding anyway.", file=sys.stderr)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = image_path.with_suffix(".excalidraw")

    print(f"🖼️  Input:  {image_path}")
    print(f"📄 Output: {output_path}")
    print()
    print("🤖 Analyzing flowchart with Qwen2.5-VL...")

    try:
        # Step 1: Extract flowchart data
        flowchart_data = extract_flowchart_from_image(str(image_path))
        nodes_count = len(flowchart_data.get("nodes", []))
        arrows_count = len(flowchart_data.get("arrows", []))
        print(f"   Found {nodes_count} shapes and {arrows_count} connections.")

        # Step 2: Build Excalidraw JSON
        print("🔧 Building Excalidraw file...")
        excalidraw_json = build_excalidraw_json(flowchart_data)

        # Step 3: Write output
        output_path.write_text(excalidraw_json, encoding="utf-8")
        print(f"\n✅ Done! Open the file in Excalidraw:")
        print(f"   https://excalidraw.com → File → Open → {output_path.name}")

    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
