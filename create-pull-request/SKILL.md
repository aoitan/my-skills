---
name: create-pull-request
description: 現在の作業ブランチの変更差分と関連Issueをもとに、レビュワー向けのPull Request本文を作成し、必要に応じてGitHub CLIでPR作成まで行うスキル。実装や修正が一通り終わり、変更理由・変更点・確認方法を整理してPRにまとめたいときに使う。実装前の計画作成、コードレビュー、単なるコミット作成には使わない。
version: 1.0.0
---

# Pull Request Creator Skill

このスキルは、現在の作業ブランチの変更内容 (`git diff`) と関連するIssue (`gh issue`) を分析し、プロジェクトの規約に沿ったPRを作成します。

## 必須要件 (Prerequisites)

- `git` コマンドが利用可能であること
- `gh` (GitHub CLI) がインストールされ、認証済みであること
- 作業ディレクトリがgitリポジトリ内であること

## 入力コンテキスト (Input Context)

このスキルを実行する際は、以下の情報を収集・確認してください。

1.  **変更内容**: `git diff main...HEAD` (または `git diff --cached`)
2.  **コミットログ**: `git log --oneline -n 5`
3.  **関連Issue**: `gh issue view {issue_id}` (Issue番号が明示されている場合)

## 思考プロセス (Thinking Process)

PRを作成する前に、以下のステップで情報を整理してください。

1.  **変更の意図を特定する**
    - 新機能 (feat) か、バグ修正 (fix) か、リファクタリング (refactor) か？
    - 変更は破壊的か？ (Breaking Changeの有無)
2.  **コンテキストの整合性を確認する**
    - 実装内容はIssueの要件を満たしているか？
    - `diff` に不要なファイル（デバッグプリントや一時ファイル）が含まれていないか？
3.  **文章の構成**
    - 専門用語は正確か？
    - 読む人（レビュワー）にとって「なぜ変更したか」が伝わるか？

## PRテンプレート (PR Template)

PRの本文（Body）は以下の構造で生成してください。

```markdown
## 概要 (Summary)
## 関連Issue (Related Issues)
Closes #{issue_id}

## 変更の種類 (Type of Change)
- [ ] 新機能 (New feature)
- [ ] バグ修正 (Bug fix)
- [ ] リファクタリング (Refactoring)
- [ ] ドキュメント更新 (Documentation)

## 詳細な変更点 (Detailed Changes)
- `{filename}`: {変更理由}

## 動作確認手順 (Verification Steps)
1. `make test` がパスすること
2. {具体的な確認コマンド}

## 自己チェック (Self Check)
- [ ] 既存のテストを壊していないか
- [ ] 機密情報（API Key等）が含まれていないか
