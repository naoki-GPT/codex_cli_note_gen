
# Codex CLI 組織エージェント最小構成 生成コマンド

本コマンドは、与えられた YAML 設定をもとに Codex CLI 用の**最小必須ファイル**を自動生成します。  
生成対象は以下の3点のみ（それ以外は作らない）：

1. `.codex/agents/{<roles>.md}` … 重要
2. `CODEX.md` … 重要
3. `.codex/chat/{team-chat.md, chat-participation-template.md}` … 空ファイル（ヘッダのみ）

---

## 入力

- `orggen/project.yaml`（下記スキーマに準拠）

## 出力仕様

- すべてプロジェクトルートに生成
- 既存ファイルがある場合は、差分更新ではなく**安全上書き**（バックアップを `.bak` に作成）
- 文字コード UTF-8、改行 LF

```
/CODEX.md
/.codex/
  agents/
    {role}.md ... 複数
  chat/
    team-chat.md                    # 空（ヘッダのみ）
    chat-participation-template.md  # 空（ヘッダのみ）
```

---

## 役割設計の指針（Codex CLI 向け）

- `project.yaml` を読み、以下を満たす**最小だが十分な**役割集合を提案し、そのままファイル化する。
- 役割数の目安：4〜9。
- 役割は必ず職能の被りを避けた明確な責務境界を持つ。
- 各役割に「人物像（背景/価値観/強み）」「責務」「ツール権限」「評価軸」「報酬レンジ（任意）」を定義。
- セキュリティ・品質・運用の視点を最低1ロールずつ含める（例：Security / QA / DevOps）。
- ドメイン特化ロール（プロダクトや教育等）は `project.domain` を反映。
- 倫理/法令/プライバシーに配慮するガードレールを少なくとも1ロールに明文化。
- ユーザの作業負担を減らすため、具体的な作業手順テンプレ（開始/完了/相談）を `CODEX.md` にまとめ、各エージェントから参照させる。

---

## 生成手順（必ず順守）

1. `project.yaml` を読み取り、候補ロール一覧を起案（4〜9）。
   - 「セキュリティ/品質/運用」観点が入っているか自己チェック。
2. 候補から冗長を削除し、最終ロール集合を決定。
3. `CODEX.md` を生成：
   - プロジェクトの使命/原則
   - 共通オペレーション（開始/完了/相談テンプレ）
   - セキュリティ・プライバシー方針（高レベル）
   - 評価ポリシー（簡易）
   - チャット運用（空ファイル参照にとどめる）
4. 各ロールの `.codex/agents/{role}.md` を生成：
   - Frontmatter（name / description / color / tools）
   - 人物像（背景/価値観/強み）
   - 責務（具体）
   - 使うツールと権限の範囲
   - コミュニケーションスタイル
   - セキュリティ/法令順守の注意点
   - 成功条件とKPI（簡易）
   - 報酬レンジ（任意、相対レンジで良い）
5. `.codex/chat/team-chat.md` と `chat-participation-template.md` を空で作成：
   - 1行目にタイトルのみ（詳細は運用で追記）。

---

## 書式仕様

### エージェントファイル Frontmatter

```markdown
---
name: <role-id>               # 例: backend-manager, qa-lead
description: <1行説明>        # 「Use PROACTIVELY for ...」形式歓迎
color: <named-color|hex>      # 例: blue / indigo / #10b981
tools: <カンマ区切り>         # 例: Read, Write, Shell, Plan
---
```

### エージェント本文セクション（推奨）

```
# 役割要約
# 人物像（背景・価値観・強み）
# 責務（詳細）
# 主要シナリオ（3〜6）
# ツールと権限
# セキュリティと法令
# コミュニケーションスタイル
# 成功条件・KPI
# 報酬レンジ（任意）
```

### CODEX.md 章立て（最小）

```
# プロジェクト概要
# 原則（5〜8項目）
# 共通オペレーション（開始/完了/相談テンプレ）
# セキュリティ・プライバシー方針（高レベル）
# 評価ポリシー（簡易KPI）
# チャット運用（空ファイル参照）
```

---

## 安全上のルール

- 実ファイル生成前に、生成予定一覧を標準出力へ記載（プランニング）
- 上書き前に `.bak` へバックアップ
- 個人情報/秘密情報は出力しない（YAMLに含まれる場合は伏せ字）
- 過度に長文化しない（各ファイル 2,000 行未満）

---

## 成果の要約（Codex CLI 親プロセス向け）

生成完了時、最後に以下のマーカーを付けて1ブロックで出力：

```
### OUTPUT_FOR_CODEX
status: success
roles_count: <数値>
files:
  - path: CODEX.md
  - path: .codex/agents/<role>.md
  - path: .codex/chat/team-chat.md
  - path: .codex/chat/chat-participation-template.md
notes:
  - 重要な判断や不足情報があればここに列挙
```

失敗時：

```
### OUTPUT_FOR_CODEX
status: failed
reason: <理由>
```

以上に厳密に従い、Codex CLI に最適化された最小だが実運用可能な骨格を生成してください。
