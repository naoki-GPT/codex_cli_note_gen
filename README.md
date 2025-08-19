# NoteWorks（叩き台）

あなたが与える「テーマ＋コンテキスト」から、読まれるnote記事を量産するための組織スケルトンです。`orggen/project.yaml`をジェネレータに渡して、`CODEX.md`と`.codex/agents/*.md`などを生成することを想定しています。

## ディレクトリ
- `orggen/project.yaml`: 組織メタ（原則/運用/ポリシー）とインデクサ設定（agents_dir/agents_index、guides_dir）
- `orggen/agents/<role>/*.yaml`: 1人=1ファイルの人物エージェント定義（名前/趣味/口調/権限/KPI/voice/bio/availability等）
- `orggen/agents/_template.yaml`: 人物エージェントの推奨テンプレート（必須/任意フィールドの目安）
- `orggen/guides/*.yaml`: トンマナ/運用ガイドなど（例: `note-tone-manner.yaml`）。インデクサからは除外推奨。
- `scripts/image_generate.py`: gpt-image-1で画像/図解を生成するミニCLI
- `.env`: `OPENAI_API_KEY` を格納（.gitignore済み）
- `assets/`: 画像出力先（.gitignore対象）

## 画像生成（gpt-image-1）
1) 依存インストール（ローカル環境にて）
```
pip install 'openai>=1.0.0'
```
2) APIキー設定（`.env`または環境変数）
```
OPENAI_API_KEY=...  # .envに記載済み
```
3) 実行例
```
python scripts/image_generate.py \
  --prompt "A children's book drawing of a veterinarian using a stethoscope to listen to the heartbeat of a baby otter." \
  --out assets/images/otter.png \
  --size 1024x1024
```

### noteアイキャッチ（メタプロンプト）
- ベース: `orggen/image_base.yaml`（品質high, 1536x1024）
- 推奨手順: ブリーフ → タイポ設計 → 生成 → 検証 → 承認（詳細は `orggen/guides/image_workflow.md`）
```
python scripts/image_generate_preset.py \
  --out assets/images/cover.png \
  --var article_title="タイトル" \
  --var article_summary="要約" \
  --var primary_keywords="kw1,kw2" \
  --var audience="想定読者" \
  --var tone="信頼・モダン" \
  --var brand_name="NoteWorks" \
  --var brand_color_hex="#2563EB" \
  --var theme_preset="calendar_sync" \
  --var export_format="PNG" \
  --var cjk_language="ja"
```

docs: `gpt-image-1-docs.md`（このリポ内）を参照。Responses APIは不要、Image APIの基本機能のみ使用。

## 運用の流れ（要約）
- 企画: editor-in-chief + content-strategist がブリーフ作成
- 制作: researcher → lead-writer → copy-editor → fact-checker
- 画像: visual-designer が `scripts/image_generate.py` で作成（代替テキスト/クレジット付）
- 配信: seo-distribution + community-manager
- セーフティ: legal-ethics が最終確認
- グロース: analytics-growth が1/7/30日で振り返り

## 注意事項
- `.env`は公開しない（.gitignore済み）。CIや共有時は安全なシークレット管理を使用。
- 画像生成は商標/肖像/著作権、センシティブ用途に配慮。医療/金融/法律は助言ではなく一般情報＋免責文。
- `orggen/project.yaml`はジェネレータ仕様に合わせて拡張/修正可能です。
  - 本リポは「1人=1YAML、agentsのみ（roleは各YAMLのroleで自動グループ化）」に統合。
  - 走査設定：`agents_index.glob: orggen/agents/**/*.yaml`、除外：`agents_index.exclude: [orggen/agents/_template.yaml]`
