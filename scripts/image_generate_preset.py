#!/usr/bin/env python3
import os
import sys
import re
import argparse
from pathlib import Path


def load_env_file(dotenv_path: Path):
    if not dotenv_path.exists():
        return
    try:
        for line in dotenv_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception as e:
        print(f"[warn] .env parse failed: {e}", file=sys.stderr)


def load_yaml(path: Path):
    try:
        import yaml  # type: ignore
    except Exception:
        print("[error] Python package 'pyyaml' is not installed.\n"
              "Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[\s/]+", "_", s)
    s = re.sub(r"[^a-z0-9_\-]+", "", s)
    return s


def render_template(tmpl: str, vars_map: dict[str, str]) -> str:
    # Support {{var}}, {var}, {{slugified var}}, and {{var | default('x')}}
    out = tmpl

    # slugified filter
    def _repl_slug(m):
        key = m.group(1)
        val = vars_map.get(key, "")
        return _slugify(str(val)) if val else ""

    out = re.sub(r"\{\{\s*slugified\s+([a-zA-Z0-9_]+)\s*\}\}", _repl_slug, out)

    # default filter with single quotes
    def _repl_default(m):
        key = m.group(1)
        default = m.group(2)
        val = vars_map.get(key)
        return str(val) if val is not None else default

    out = re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\|\s*default\('([^']*)'\)\s*\}\}", _repl_default, out)

    # plain double-curly
    def _repl_plain(m):
        key = m.group(1)
        val = vars_map.get(key, "")
        return str(val)

    out = re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", _repl_plain, out)

    # single-brace placeholders
    for k, v in vars_map.items():
        out = out.replace("{" + k + "}", str(v))

    # remove any remaining placeholders
    out = re.sub(r"\{\{[^}]+\}\}", "", out)
    out = re.sub(r"\{[A-Za-z0-9_\-]+\}", "", out)
    return out


def generate_image(prompt: str, out_path: Path, size: str, quality: str | None, model: str):
    try:
        from openai import OpenAI
    except Exception:
        print("[error] Python package 'openai' is not installed.\n"
              "Install with: pip install openai>=1.0.0", file=sys.stderr)
        sys.exit(2)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[error] OPENAI_API_KEY is not set. Put it in .env or export it.", file=sys.stderr)
        sys.exit(2)

    client = OpenAI(api_key=api_key)
    params = dict(model=model, prompt=prompt, size=size)
    if quality:
        params["quality"] = quality
    print(f"[info] Requesting image: model={model} size={size} quality={quality or 'default'}")
    result = client.images.generate(**params)

    import base64
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        f.write(image_bytes)
    print(f"[ok] Saved: {out_path}")


def main():
    p = argparse.ArgumentParser(description="Generate images from a YAML preset/meta prompt")
    p.add_argument("--preset", default="orggen/image_base.yaml")
    p.add_argument("--template", default=None, help="Legacy template name in YAML (e.g., eyecatch, inline)")
    p.add_argument("--out", required=True, help="Output image path")
    p.add_argument("--var", action="append", default=[], help="Vars like key=value (repeatable)")
    p.add_argument("--size", default=None, help="Override size (e.g., 1536x1024)")
    p.add_argument("--quality", default=None, help="Override quality (e.g., high)")
    args = p.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    load_env_file(project_root / ".env")

    cfg = load_yaml(Path(args.preset))
    model = "gpt-image-1"

    # Collect vars
    vars_map: dict[str, str] = {}
    for item in args.var:
        if "=" in item:
            k, v = item.split("=", 1)
            vars_map[k.strip()] = v.strip()

    prompt = ""
    size = args.size
    quality = args.quality or "high"

    if args.template and isinstance(cfg.get("presets"), dict):
        # Legacy schema support
        tcfg = cfg["presets"].get(args.template)
        if not tcfg:
            print(f"[error] template '{args.template}' not found in {args.preset}", file=sys.stderr)
            sys.exit(2)
        size = size or tcfg.get("size", "1024x1024")
        prompt_template = tcfg.get("prompt_template", "")
        header = []
        if tcfg.get("style_notes"):
            header.append("Style notes: " + ", ".join(tcfg["style_notes"]))
        body = render_template(prompt_template, vars_map)
        prompt = ("\n".join(header) + "\n\n" + body).strip()
    else:
        # New meta-prompt schema
        size = size or cfg.get("size", "1024x1024")
        prompt_template = cfg.get("prompt_template", "")
        # Also surface key meta as a header
        header = [
            f"Platform: {cfg.get('platform','')}",
            f"Meta version: {cfg.get('meta_version','')}",
            "Guidance: auto layout & typography; respect safe area and crop guards.",
        ]
        body = render_template(prompt_template, vars_map)
        prompt = ("\n".join([h for h in header if h.strip()]) + "\n\n" + body).strip()

    generate_image(prompt=prompt, out_path=Path(args.out), size=size, quality=quality, model=model)


if __name__ == "__main__":
    main()
