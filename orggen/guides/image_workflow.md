# 画像生成ワークフロー（note アイキャッチ）

## 目的
- 記事のペルソナ/タイトル/要約に最適化された高品質アイキャッチを安定生成する。

## 役割と責務
- editor-in-chief: 最終承認、ブランド適合性の確認。
- content-strategist: ペルソナ/タイトル/要約/キーワードのブリーフ作成。
- typographer: タイポ設計（行長/行数/サイズ/コントラスト、セーフエリア）を定義。
- visual-designer: 背景生成（`orggen/image_base.yaml` を用いる）。
- copy-editor + fact-checker: 文言/権利の最終確認、altテキスト整備。

## 手順
1) ブリーフ作成（content-strategist）
   - ペルソナ、想定読者行動、記事タイトル/要約、主要キーワード。
2) タイポ設計（typographer）
   - 行長・行数・サイズ・コントラスト、セーフエリア方針。
3) 生成（visual-designer）
   - `python scripts/image_generate_preset.py --out assets/images/cover.png --var article_title="..." --var article_summary="..." --var primary_keywords="kw1,kw2" --var tone="..." --var brand_name="..." --var brand_color_hex="#2563EB" --var theme_preset="calendar_sync"`
4) 検証（copy-editor + fact-checker）
   - 語調/誤字/権利、altテキスト。
5) 承認（editor-in-chief）
   - ブランド適合と最終GO。

## ガードレール
- セーフエリア: 左右6%、上8%、下10% を内側に確保。
- コントラスト: WCAG 4.5:1 以上（足りない場合は下地/反転）。
- 権利: 商標/肖像/著作権配慮、センシティブ回避。

