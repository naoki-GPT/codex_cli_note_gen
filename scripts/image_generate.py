#!/usr/bin/env python3
import os
import sys
import base64
import argparse
from pathlib import Path


def load_env_file(dotenv_path: Path):
    if not dotenv_path.exists():
        return
    try:
        for line in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # Do not override if already set in env
            if key and key not in os.environ:
                os.environ[key] = val
    except Exception as e:
        print(f"[warn] .env parse failed: {e}", file=sys.stderr)


def generate_image(prompt: str, out_path: Path, size: str = "1024x1024", quality: str | None = None):
    try:
        # Lazy import so the script can still show helpful errors if not installed
        from openai import OpenAI
    except Exception as e:
        print("[error] Python package 'openai' is not installed.\n"
              "Install with: pip install openai>=1.0.0", file=sys.stderr)
        sys.exit(2)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[error] OPENAI_API_KEY is not set. Put it in .env or export it.", file=sys.stderr)
        sys.exit(2)

    client = OpenAI(api_key=api_key)

    print(f"[info] Requesting image: size={size} quality={quality or 'default'}")
    params = dict(model="gpt-image-1", prompt=prompt, size=size)
    if quality:
        params["quality"] = quality
    result = client.images.generate(**params)

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        f.write(image_bytes)
    print(f"[ok] Saved: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate an image with gpt-image-1")
    parser.add_argument("--prompt", required=True, help="Prompt describing the image")
    parser.add_argument("--out", required=True, help="Output image path (e.g., assets/images/cover.png)")
    parser.add_argument("--size", default="1024x1024", help="Image size, e.g., 1024x1024, 512x512")
    parser.add_argument("--quality", default=None, help="Image quality (e.g., high)")
    args = parser.parse_args()

    # Load .env from project root if present
    project_root = Path(__file__).resolve().parents[1]
    load_env_file(project_root / ".env")

    generate_image(args.prompt, Path(args.out), size=args.size, quality=args.quality)


if __name__ == "__main__":
    main()
