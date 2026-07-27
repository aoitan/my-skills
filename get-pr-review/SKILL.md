---
name: get-pr-review
description: 指定したPull Requestのレビューコメントを取得し、整理しやすいJSON形式で出力する取得専用スキル。PRのレビュー指摘一覧を確認したいとき、レビュー状況を要約したいとき、再レビュー前に前回コメントを参照したいときに使う。PR本文の作成、コード差分のレビュー実行、指摘への修正そのものには使わない。
---

# 手順
以下のコマンドを実行して、Pull Requestのコメントを取得してください。

```bash
gh api "repos/:owner/:repo/pulls/<pr number>/comments" | jq '.[] | { login: .user.login, update_date: .updated_at, body, diff_hunk }'
```

制約事項

*   <pr number> はユーザーの要求またはコンテキストから推測される番号に置換すること。
*   出力が長すぎる場合は直近の10件に絞ること。
