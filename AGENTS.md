# Repository Guidelines

## プロジェクト構成とモジュール
- `orggen/project.yaml`: 役割/方針/KPI など中核設定。
- `orggen/agents/<role>/*.yaml`: 各エージェントのプロファイル（例: `lead-writer/kazuki-tech.yaml`）。
- `orggen/guides/*.yaml`: トンマナ/運用ガイド（例: `note-tone-manner.yaml`）。
- `scripts/image_generate.py`: `gpt-image-1` で画像を生成する CLI。
- `assets/`: 生成画像の出力先（gitignore 済み）。必要に応じて `assets/images/` を作成。
- `README.md`, `gpt-image-1-docs.md`: 使い方とモデルの参照。

## ビルド・テスト・開発コマンド
- 仮想環境: `python -m venv .venv && source .venv/bin/activate`
- 依存導入: `pip install "openai>=1.0.0" yamllint`
- YAML Lint: `yamllint orggen`
- 画像スモークテスト:
  `python scripts/image_generate.py --prompt "ワークフロー図" --out assets/images/sample.png --size 512x512`
- `.env` の自動読込: ルートの `.env` の `OPENAI_API_KEY` をスクリプトが読み込みます。
- プリセット生成（推奨）: `pip install pyyaml` 後、
  `python scripts/image_generate_preset.py --template eyecatch --out assets/images/cover.png --var title="○○" --var topic="△△" --var tone="neutral"`
 - タイトル合成（推奨）: `pip install Pillow` 後、
   `python scripts/eyecatch_overlay.py --in assets/images/cover.png --out assets/images/cover_title.png --title "タイトル" --position center`

## コーディング規約と命名
- YAML: インデント 2 スペース、キーは小文字、コレクションは配列で表現。
- ファイル名: kebab-case（例: `content-strategist.yaml`, `sae-finance.yaml`）。
- ID: `id` は短い小文字ハンドル（例: `akina`）。
- Python: PEP 8、`snake_case`、スクリプトは `scripts/` 配下に配置。
- プロンプト: 記事ブリーフの要件を端的に反映し、具体的に。

## テスト方針
- 構造検証: `yamllint orggen` と YAML 差分の目視確認。
- 画像出力確認: コスト最小化のため `--size 256x256` で生成し、`assets/images/` に保存されることを確認。
- ポリシー確認: 代替テキスト/クレジットの記載、権利配慮、`project.yaml` の制約順守。

## コミットとプルリクエスト
- コミット: Conventional Commits を推奨。
- 例: `feat(agents): add analytics-growth person`, `chore(yaml): lint orggen/agents`, `docs: update README for image flow`
- PR: 目的/背景、変更点の要約、関連 Issue、生成物のパスやスクリーンショット、ポリシー影響を明記。
- シークレットは除外: `.env` や `assets/` をコミットしない。

## セキュリティと設定
- シークレット: `OPENAI_API_KEY` は `.env`（gitignore 済み）に保存し最小権限で運用。
- データ境界: PII を扱わない。出典 URL を明記。公開前に法務/倫理チェック。
