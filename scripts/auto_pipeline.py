#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
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


def slugify(s: str) -> str:
    import re
    s = s.strip().lower()
    s = re.sub(r"[\s/]+", "_", s)
    s = re.sub(r"[^a-z0-9_\-]+", "", s)
    return s


def generate_article_md(title: str, summary: str, audience: str, tone: str,
                        keywords: list[str]) -> str:
    try:
        from openai import OpenAI
    except Exception:
        print("[error] openai package missing. pip install openai>=1.0.0", file=sys.stderr)
        sys.exit(2)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[error] OPENAI_API_KEY is not set.", file=sys.stderr)
        sys.exit(2)
    client = OpenAI(api_key=api_key)

    sys_prompt = (
        "You are a senior Japanese editor and writer. Write clear, structured, factual Markdown articles for note. "
        "Prioritize readability, ethics, and citations when necessary. Avoid clickbait."
    )
    user_prompt = f"""
目的: 読まれるnote記事を執筆する。

タイトル: {title}
要約: {summary}
想定読者: {audience}
キーワード: {', '.join(keywords)}
トーン: {tone}

要件:
- 見出しと小見出しで論理構成（導入→課題→解決→手順→落とし穴→まとめ）
- 具体例と手順は箇条書き中心。専門語は噛み砕く。
- 700–1400字目安。冗長にしない。
- 禁止: 扇情表現/断定、確証なき数値。必要なら「参考リンク:」節で出典URLを列挙。
出力: 純粋なMarkdown本文のみ。フロントマター不要。
"""

    resp = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    # Extract text
    parts = []
    for out in resp.output:
        if getattr(out, "type", "") == "message":
            for c in getattr(out, "content", []):
                if getattr(c, "type", "") == "output_text":
                    parts.append(getattr(c, "text", ""))
    text = "\n".join(parts).strip()
    if not text:
        # Fallback for alternative structures
        try:
            text = resp.output_text.strip()
        except Exception:
            pass
    return text or ""


def run_image_generation(out_image: Path, vars_map: dict):
    cmd = [
        sys.executable,
        str(Path(__file__).parents[0] / "image_generate_preset.py"),
        "--out", str(out_image),
    ]
    for k, v in vars_map.items():
        cmd += ["--var", f"{k}={v}"]
    print("[info] Running:", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    p = argparse.ArgumentParser(description="Auto-generate article + eyecatch end-to-end (non-interactive)")
    p.add_argument("--title", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--audience", required=True)
    p.add_argument("--tone", default="信頼・モダン")
    p.add_argument("--keywords", default="", help=",区切りキーワード")
    p.add_argument("--brand-name", dest="brand_name", default="")
    p.add_argument("--brand-color", dest="brand_color", default="#2563EB")
    p.add_argument("--theme", default="calendar_sync")
    p.add_argument("--out-dir", default="articles")
    p.add_argument("--images-dir", default="assets/images")
    p.add_argument("--no-image", action="store_true")
    args = p.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    load_env_file(project_root / ".env")

    slug = slugify(args.title)[:80]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    article_path = out_dir / f"{slug}.md"

    # 1) Write article
    md = generate_article_md(
        title=args.title,
        summary=args.summary,
        audience=args.audience,
        tone=args.tone,
        keywords=[s.strip() for s in args.keywords.split(',') if s.strip()],
    )
    if not md:
        print("[error] Article generation returned empty text", file=sys.stderr)
        sys.exit(3)
    article_path.write_text(md, encoding="utf-8")
    print(f"[ok] Article saved: {article_path}")

    # 2) Eyecatch
    if not args.no_image:
        images_dir = Path(args.images_dir)
        images_dir.mkdir(parents=True, exist_ok=True)
        out_image = images_dir / f"{slug}_cover.png"
        vars_map = {
            "article_title": args.title,
            "article_summary": args.summary,
            "primary_keywords": args.keywords,
            "audience": args.audience,
            "tone": args.tone,
            "brand_name": args.brand_name,
            "brand_color_hex": args.brand_color,
            "theme_preset": args.theme,
            "export_format": "PNG",
            "cjk_language": "ja",
        }
        run_image_generation(out_image, vars_map)
        print(f"[ok] Eyecatch saved: {out_image}")

    print("[done] auto_pipeline completed.")


if __name__ == "__main__":
    main()

