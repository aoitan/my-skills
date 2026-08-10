# my-skills

個人で作成し、このリポジトリから公開・管理するSkillを置くリポジトリです。

この作業ディレクトリには、リポジトリ管理の自作Skillだけでなく、Codexや他ツールがインストール・同期するSkillも共存します。ツール管理のSkillを誤って公開しないよう、`.gitignore` はルート直下をデフォルトで除外し、公開対象だけを明示的に許可する方式にしています。

## 管理区分

### リポジトリ管理の自作Skill

このリポジトリで直接作成し、公開・保守するSkillです。

- Skillのディレクトリを `.gitignore` の `Skills published from this repository` に追加します。
- [EXTERNAL_SKILLS.md](./EXTERNAL_SKILLS.md) には追加しません。
- 既存の管理対象外Skillをリポジトリ管理へ移す場合は、カタログから該当項目を削除します。

### インストール・ツール管理のSkill

他ツールがインストール、生成、同期、更新するSkillです。ユーザー自身が作成したSkillでも、別のツールが配置・管理するものはこちらに含めます。

- `.gitignore` の許可リストには追加しません。
- [EXTERNAL_SKILLS.md](./EXTERNAL_SKILLS.md) に管理元、配置場所、用途、Git管理外の理由を記録します。
- ツールによる更新を、このリポジトリから上書き・公開しません。

出自や管理責任が分からないSkillは、確認できるまでインストール・ツール管理として扱います。

## エージェントがSkillを追加・検出したときのルール

1. Skillの作成者だけでなく、誰が配置・更新を管理するかを確認する。
2. このリポジトリで直接管理する自作Skillなら、`.gitignore` の許可リストへディレクトリを追加する。
3. 他ツールが管理するSkillなら、許可リストへ追加せず、`EXTERNAL_SKILLS.md` の該当区分を追加または更新する。
4. 配置済みSkillの管理区分が変わる場合は、`.gitignore` と `EXTERNAL_SKILLS.md` を同じ変更で整合させる。
5. `git status --short --ignored` と `git check-ignore` で、公開対象だけが追跡可能であることを確認する。
6. 管理対象外Skillを `git add -f` で強制追加しない。

新しいルートファイルを追加する場合も、必要性を確認したうえで `.gitignore` の `Repository files` に明示的に追加します。

## 関連ファイル

- [`.gitignore`](./.gitignore): 公開対象Skillとリポジトリファイルの許可リスト
- [`EXTERNAL_SKILLS.md`](./EXTERNAL_SKILLS.md): このディレクトリに共存する管理対象外Skillのカタログ
