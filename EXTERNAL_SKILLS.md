# Repository-external Skill Catalog

このファイルは、この作業ディレクトリに配置されているものの、`my-skills` リポジトリでは公開・管理しないSkillの一覧です。

- `.gitignore` はデフォルト拒否の許可リスト方式です。
- この一覧は参照用のスナップショットであり、Gitの除外判定には使いません。
- Skillをこのリポジトリの公開対象へ移す場合は、出自と管理責任を確認してから `.gitignore` の許可リストへ追加します。

最終確認日: 2026-11-24

## Codex管理

| Skill | 配置場所 | 用途 | Git管理外の理由 |
| --- | --- | --- | --- |
| `hatch-pet` | `hatch-pet/` | Codex互換のアニメーションPetを作成・検証・パッケージ化する | Codexが配置・管理するため |
| `imagegen` | `.system/imagegen/` | ラスター画像の生成・編集を行う | CodexのシステムSkillであるため |
| `openai-docs` | `.system/openai-docs/` | OpenAI製品・APIの公式情報を調査する | CodexのシステムSkillであるため |
| `plugin-creator` | `.system/plugin-creator/` | Codexプラグインを作成・更新する | CodexのシステムSkillであるため |
| `review-agent` | `.system/review-agent/` | 指定されたコード変更を読み取り専用でレビューする | CodexのシステムSkillであるため |
| `skill-creator` | `.system/skill-creator/` | Codex Skillを作成・更新する | CodexのシステムSkillであるため |
| `skill-installer` | `.system/skill-installer/` | Codex Skillをインストールする | CodexのシステムSkillであるため |

## 自作・他ツール管理
### kelpie

| Skill | 配置場所 | 用途 | Git管理外の理由 |
| --- | --- | --- | --- |
| `implementation` | `implementation/` | 計画済みの変更を小さな差分で実装する | 他ツールのワークフローから配置・管理するため |
| `plan-comprehension-check` | `plan-comprehension-check/` | 根拠とともに計画を再構成し、解釈差を報告する | 他ツールのワークフローから配置・管理するため |
| `prototype-planning` | `prototype-planning/` | 検証する不確実性、成功条件、非目標を定義する | 他ツールのワークフローから配置・管理するため |
| `prototyping` | `prototyping/` | 少数の仮説を検証する使い捨てプロトタイプを作る | 他ツールのワークフローから配置・管理するため |
| `red-team-review` | `red-team-review/` | 設計・試作・計画を失敗観点からレビューする | 他ツールのワークフローから配置・管理するため |
| `review-fix-loop` | `review-fix-loop/` | 重大な指摘を優先してレビューと修正を反復する | 他ツールのワークフローから配置・管理するため |
| `solution-design` | `solution-design/` | プロトタイプ結果をもとに堅牢な解決策を設計する | 他ツールのワークフローから配置・管理するため |
| `work-breakdown` | `work-breakdown/` | 設計を依存関係付きの実行可能な作業へ分解する | 他ツールのワークフローから配置・管理するため |
### llm-veil

| Skill | 配置場所 | 用途 | Git管理外の理由 |
| --- | --- | --- | --- |
| `llm-veil` | `llm-veil/` | ローカル読取時のシークレット漏洩やプロンプトインジェクションを軽減する | 他ツールのワークフローから配置・管理するため |

## 外部配布

### UI/UXデザイン系

| Skill | 配置場所 | 用途 | Git管理外の理由 |
| --- | --- | --- | --- |
| `banner-design` | `banner-design/` | SNS・広告・Web・印刷向けのバナーをデザインする | 外部配布のSkillであるため |
| `brand` | `brand/` | ブランドボイス、ビジュアルアイデンティティ、アセットの一貫性を管理する | 外部配布のSkillであるため |
| `design` | `design/` | ロゴ、CIP、スライド、アイコンなどのデザイン作業を包括的に扱う | 外部配布のSkillであるため |
| `design-system` | `design-system/` | デザイントークン、コンポーネント仕様、スライドを設計する | 外部配布のSkillであるため |
| `ui-styling` | `ui-styling/` | shadcn/uiとTailwind CSSでUIを構築・スタイリングする | 外部配布のSkillであるため |
| `ui-ux-pro-max` | `ui-ux-pro-max/` | 検索可能なデータをもとにUI/UXを設計・レビュー・改善する | 外部配布のSkillであるため |

### difit

| Skill | 配置場所 | 用途 | Git管理外の理由 |
| --- | --- | --- | --- |
| `difit` | `difit/` | コード変更後にdifitでユーザーへレビューを依頼する | 外部配布のSkillであるため |
| `difit-review` | `difit-review/` | 差分をレビューし、指摘をdifit上のコメントとして表示する | 外部配布のSkillであるため |

### Herdr

| Skill | 配置場所 | 用途 | Git管理外の理由 |
| --- | --- | --- | --- |
| `herdr` | `herdr/` | コーディングエージェント向け端末マルチプレクサHerdrを操作する | 外部配布のSkillであるため |

### abagames/agentic-gamedev-skills

| Skill | 配置場所 | 用途 | Git管理外の理由 |
| --- | --- | --- | --- |
| `exploring-game-design-space` | `exploring-game-design-space/` | ゲームデザイン案を幅広く生成し、検証可能な仮説に絞る | 外部配布のSkillであるため |
| `stress-testing-game-concepts` | `stress-testing-game-concepts/` | ゲーム案やルールの破綻を敵対的に検証する | 外部配布のSkillであるため |

## 出自未確認

| Skill | 配置場所 | 用途 | Git管理外の理由 |
| --- | --- | --- | --- |
| `whywhy` | `whywhy/` | 問題を因果ツリーで分析し、根本原因と打ち手を導く | Xで流れていたものに手を加えて使っているので出どころ不明 |


## Skill以外の管理対象外ディレクトリ

| 配置場所 | 内容 | Git管理外の理由 |
| --- | --- | --- |
| `.serena/` | Serenaのプロジェクトメタデータ | ローカルツールが生成・管理するため |
