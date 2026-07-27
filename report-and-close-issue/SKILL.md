---
name: report-and-close-issue
description: GitHub Issueの作業が完了した後に、規定フォーマットの最終報告コメントを投稿し、Issueを completed としてクローズする終了処理用スキル。実装、確認、必要な報告がすべて終わり、Issueを正式に閉じたいときに使う。途中報告、作業継続中の記録、実装、レビュー、PR作成には使わない。
---

# Report and Close Issue

## 概要
アサインされたGitHub Issueのタスクを完了した際、規定のフォーマットで最終報告のコメントを投稿し、Issueをクローズするためのスキルです。エージェントはこのスキルを用いて、自律的にタスクを完結させなければなりません。

## 前提条件
- GitHub CLI (`gh`) が実行可能であり、対象リポジトリへのアクセス権限があること。

## 実行手順

### Step 1: 情報の整理
このスキルを実行する前に、自身の作業履歴から以下の情報を収集・整理してください。
1. `issue_number`: 対象となるIssueの番号（例: 123）
2. `action_summary`: 実装内容や修正したバグの簡潔な概要
3. `changed_files_or_commits`: 変更した主要なファイル名、Commitハッシュ、または作成したPRのURL
4. `remaining_tasks_or_notes`: 備考や残課題（なければ「特になし」とする）

### Step 2: 報告フォーマットの作成
以下のMarkdownテンプレートに Step 1 で整理した情報を埋め込み、報告用のテキストを作成してください。
※ 末尾の `[STATUS: DONE]` は外部スクリプトによる進捗収集で使用するため、**絶対に省略・変更しないでください**。

```markdown
### 完了報告
- **対応内容:** {action_summary}
- **変更箇所:** {changed_files_or_commits}
- **備考/残課題:** {remaining_tasks_or_notes}

[STATUS: DONE]
```

### Step 3: コメントの投稿
作成したテキストを本文として、以下のコマンドを実行しIssueにコメントを投稿してください。

```bash
gh issue comment {issue_number} --body "作成したテキスト"
```

### Step 4: Issueのクローズ
コメントの投稿が成功したら、以下のコマンドを実行してIssueを完了状態としてクローズしてください。

```bash
gh issue close {issue_number} --reason "completed"
```

## 期待される動作
- 指定されたフォーマット通りにIssueにコメントが追加されること。
- 対象のIssueが `completed` としてクローズされること。
- 人間からの追加の指示や承認を待たずに、自律的に一連の処理を終わらせること。
