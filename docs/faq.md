# よくある質問

## 目的

このFAQドキュメントは、開発者がProject CodeGuardセキュリティルールをAI支援コーディングワークフローにスムーズに統合できるよう、明確で簡潔な回答を提供します。AIが生成するコードが、生産性を妨げることなく安全な開発プラクティスに従うことを目指しています。

---

## Q: ルールはどこで入手できますか？

**A:** [Project CodeGuard GitHubリポジトリ](https://github.com/project-codeguard/rules)でルールを入手できます。最新の安定版リリースは[リリースページ](https://github.com/project-codeguard/rules/releases)から入手できます。

---

## Q: Windsurf、Cursor、GitHub Copilotでルールを使うには？

**A:** 詳しいインストール手順は[はじめにガイド](getting-started.md)をご覧ください。要約すると：

1. [リリースページ](https://github.com/project-codeguard/rules/releases)から最新リリースをダウンロード
2. アーカイブを展開し、IDE用のルールをプロジェクトにコピー：
   - **Cursor**: `.cursor/`ディレクトリをプロジェクトルートにコピー
   - **Windsurf**: `.windsurf/`ディレクトリをプロジェクトルートにコピー
   - **GitHub Copilot**: `.github/instructions/`ディレクトリをプロジェクトルートにコピー
3. IDEを再起動してコーディング開始 - AIアシスタントが自動的にセキュリティルールに従います

---
## Q: これらのルールはAIエージェントの**コンテキストウィンドウ**を大量に消費しますか？

**A:** いいえ。常時有効ルールは軽量で効率的に設計されており、AIエージェントのコンテキストウィンドウを大量に消費しません。「glob」ルールは、ルールで指定された関連ファイルタイプにのみ適用されるよう設計されています。

---
## Q: `additional_rules`フォルダとは何ですか？

**A:** `additional_rules`フォルダには、Project CodeGuardコアルールを補完するルールが含まれています。これらのルールは常時有効ではなく、ダウンロードリリースには含まれません。コード生成後のコードレビューやセキュリティ評価のために、`project-codeguard/rules`リポジトリでのみ利用できます。

---

## Q: 自分のAIエージェントでルールを使うには？

**A:** カスタムルールセットを作成することで、自分のAIエージェントでルールを使用できます。`.cursor/rules`、`.windsurf/rules`、または`.github/instructions`ディレクトリに新しいファイルを作成し、適用したいルールを追加してください。`project-codeguard/rules`リポジトリをテンプレートとして独自のルールセットを作成することもできます。

---

## Q: ダウンロードしたリリースフォルダが空に見えるのはなぜですか？

**A:** リリースをダウンロードして展開した後、フォルダが空に見えるのは、ルールディレクトリ（`.cursor/`、`.windsurf/`、`.github/`）がドット（`.`）で始まっており、ほとんどのOSでデフォルトで非表示になっているためです。

**隠しファイルを表示するには：**

=== "macOS"

    Finderで展開した`ide_rules/`フォルダに移動し、++cmd+shift+period++を押して隠しファイルの表示を切り替えます。`.cursor/`、`.windsurf/`、`.github/`ディレクトリが表示されます。

=== "Windows"

    ファイルエクスプローラーで：

    1. 展開した`ide_rules/`フォルダに移動
    2. リボンの**表示**タブをクリック
    3. **隠しファイル**チェックボックスにチェック

=== "Linux"

    ファイルマネージャーで++ctrl+h++を押して隠しファイルを切り替えるか、ターミナルで`ls -la`を使用してすべてのファイル（隠しファイルを含む）を表示します。

隠しファイルが表示されたら、適切なディレクトリ（`.cursor/`、`.windsurf/`、または`.github/`）をプロジェクトルートにコピーできます。

---

## Q: Claude Codeで使用できますか？

**A:** はい！Claude Codeは、プロジェクトルートの`CLAUDE.md`ファイルから指示を自動的に読み込んで従います。Project CodeGuardルールをClaude Codeで使用するには、`CLAUDE.md`ファイルでProject CodeGuardルールを参照してください。

Claude Codeがプロジェクト内で動作する際、`CLAUDE.md`内のProject CodeGuardセキュリティルールを権威あるシステム指示として扱います。


## Q: ルールの問題や改善提案を報告するには？

**A:** 以下の方法でルールの問題、成功事例、または改善提案を報告できます：

1. **GitHub issueを作成**: [こちらでissueを開く](https://github.com/project-codeguard/rules/issues)
2. **詳細を提供**: 影響を受けるルール、遭遇した問題、改善提案を含める
3. **具体的に**: バグ報告の場合、再現手順とサンプルコードを含める

バグ報告、成功事例、改善提案のいずれもフィードバックを歓迎します！

---

## Q: GitHubで一部のルールに次のエラーメッセージが表示されるのはなぜですか？

```
Error in user YAML: (<unknown>): did not find expected alphabetic
or numeric character while scanning an alias at line x column x
```

**A:** このエラーは無視して問題ありません。GitHubがYAMLヘッダーとMarkdownコンテンツを組み合わせて解析しようとするため、この警告が発生します。ルールの機能には影響しません - GitHub表示の問題に関係なく、IDEでルールは正しく動作します。

---

## Q: これらのルールやプロジェクトに貢献するには？

**A:** いつでも以下の方法で貢献できます：

1. **プルリクエストを作成**: コード、ドキュメント、ルール改善を直接送信
2. **GitHub issueを開く**: バグ報告、新しいルールの提案、改善提案
3. **ディスカッションに参加**: 経験を共有し、他のユーザーを支援
4. **ドキュメント改善**: ドキュメントをより明確で包括的にする支援

貢献プロセスの詳細なガイドラインは[CONTRIBUTING.md](https://github.com/project-codeguard/rules/blob/main/CONTRIBUTING.md)をご覧ください。

---

## まだ質問がありますか？

**答えが見つかりませんか？**

- [issueを開く](https://github.com/project-codeguard/rules/issues)で質問を投稿
- [ディスカッションを開始](https://github.com/project-codeguard/rules/discussions)してコミュニティとチャット


