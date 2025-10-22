# はじめに

Project CodeGuardを数ステップで導入できます。

## 前提条件

開始する前に、各IDEでのルール設定方法を確認してください。

=== "Cursor"

    Cursorは`.cursor/rules`でルールを設定します。

    :material-book-open-page-variant: [Cursorルールのドキュメント](https://docs.cursor.com/en/context/rules)

=== "Windsurf"

    Windsurfは`.windsurf/rules`でルールを設定します。

    :material-book-open-page-variant: [Windsurfルールのドキュメント](https://docs.windsurf.com/windsurf/cascade/memories#rules)

=== "GitHub Copilot"

    GitHub Copilotは`.github/instructions`でルールを設定します。

    :material-book-open-page-variant: [GitHub Copilot Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)

## インストール

### 方法1: ビルド済みルールのダウンロード（推奨）

1. **ダウンロード**: [リリースページ](https://github.com/project-codeguard/rules/releases)から最新のリリースアーカイブをダウンロード
2. **展開**: ダウンロードしたファイルを解凍
3. **インストール**: 各IDE用のルールをプロジェクトルートにコピー：
    - **Cursor用**: `.cursor/`ディレクトリをコピー
    - **Windsurf用**: `.windsurf/`ディレクトリをコピー
    - **GitHub Copilot用**: `.github/instructions/`ディレクトリをコピー

!!! tip "リポジトリレベルでのインストール"
    リポジトリレベルでインストールすると、チームメンバー全員がリポジトリをクローンした時点でセキュリティルールの恩恵を受けられます。

!!! note "macOS/Linuxでの隠しファイル表示"
    macOS/Linuxでは、隠しファイルを表示する必要があります：

    - **macOS Finder**: ++cmd+shift+period++を押して表示を切り替え
    - **Linux**: ターミナルで`ls -la`を実行、またはファイルマネージャーで「隠しファイルを表示」を有効化

### 方法2: ソースからビルド

ルールをカスタマイズまたは貢献したい場合：

```bash
# リポジトリをクローン
git clone https://github.com/project-codeguard/rules.git
cd rules

# 依存関係をインストール（Python 3.11以上が必要）
uv sync

# 統合ルールを各IDE形式に変換
uv run python src/unified_to_all.py rules/ .

# 生成されたルールをプロジェクトにコピー
cp -r ./ide_rules/.cursor/ /path/to/your/project/
cp -r ./ide_rules/.windsurf/ /path/to/your/project/
cp -r ./ide_rules/.github/ /path/to/your/project/
```

## インストールの確認

インストール後、プロジェクト構造は以下のようになります：

```
your-project/
├── .cursor/
│   └── rules/
├── .windsurf/
│   └── rules/
├── .github/
│   └── instructions/
└── ... (プロジェクトファイル)
```

## 含まれる内容

セキュリティルールは主要な領域をカバーしています：

### コアセキュリティルール

- **🔐 暗号化**: 安全なアルゴリズム、鍵管理、TLS設定
- **🛡️ 入力検証**: SQLインジェクション、XSS防御、コマンドインジェクション対策
- **🔑 認証**: MFA、OAuth/OIDC、パスワードセキュリティ、セッション管理
- **⚡ 認可**: RBAC/ABAC、アクセス制御、権限昇格防止

### プラットフォーム別ルール

- **📱 モバイルアプリ**: iOS/Androidセキュリティ、安全なストレージ、通信セキュリティ
- **🌐 APIセキュリティ**: REST/GraphQL/SOAPセキュリティ、レート制限、SSRF防止
- **☁️ クラウド・コンテナ**: Docker/Kubernetes強化、IaCセキュリティ
- **🗄️ データストレージ**: データベースセキュリティ、暗号化、バックアップ保護

### DevOps・サプライチェーン

- **📦 依存関係**: サプライチェーンセキュリティ、SBOM、脆弱性管理
- **🔄 CI/CD**: パイプラインセキュリティ、アーティファクト署名、シークレット管理
- **📝 ログ**: 安全なログ記録、モニタリング、プライバシー配慮のテレメトリー

## 統合のテスト

ルールが正しく動作するか確認するには：

1. **IDEを起動** - Project CodeGuardルールがインストールされたIDE
2. **新規ファイルを作成** - サポート言語（Python、JavaScript、Java、C/C++など）
3. **AIアシスタントに質問** - セキュリティ影響のあるコード生成を依頼：
   - 「パスワードをハッシュ化する関数を作成」
   - 「データベースに接続するコードを書いて」
   - 「認証機能付きAPIエンドポイントを生成」

4. **出力を確認** - AIが自動的にセキュリティベストプラクティスを適用：
   - 強力な暗号化アルゴリズム（パスワードはbcrypt/Argon2）
   - SQLインジェクション防止のパラメータ化クエリ
   - 適切な認証・認可チェック

## 次のステップ

- **ルールを確認**: IDEのルールディレクトリでセキュリティルールを確認
- **統合をテスト**: コードを生成してセキュリティガイダンスを実際に体験
- **フィードバック共有**: [issue](https://github.com/project-codeguard/rules/issues)で改善提案を送信
- **貢献**: [CONTRIBUTING.md](https://github.com/project-codeguard/rules/CONTRIBUTING.md)で新しいルールや改善方法を確認

!!! success "準備完了！"
    Project CodeGuardが開発ワークフローを保護します。セキュリティルールがAIアシスタントによるより安全なコード生成を自動的にガイドします。

## トラブルシューティング

### ルールが機能しない

AIアシスタントがルールに従わない場合：

1. **IDEを再起動** - ルールが読み込まれるよう確認
2. **ファイルの場所を確認** - IDE用の正しいディレクトリにルールがあるか確認
3. **ファイル形式を確認** - ルールはMarkdownファイルである必要があります
4. **明示的にリクエスト** - AIに直接指示：「このコードを生成する際はセキュリティルールに従ってください」

### パフォーマンスへの影響

ルールのパフォーマンス影響は最小限ですが、問題が発生した場合：

- **ルール数を削減**: コアルール（暗号化、入力検証、認証）から開始
- **ルールを結合**: 関連ルールを少数のファイルに統合
- **問題を報告**: [GitHub Issues](https://github.com/project-codeguard/rules/issues)で報告

## サポート

- **ドキュメント**: 今お読みのドキュメントです！よくある質問は[FAQ](faq.md)を確認
- **GitHub Issues**: [バグ報告や質問](https://github.com/project-codeguard/rules/issues)
- **ディスカッション**: [コミュニティディスカッションに参加](https://github.com/project-codeguard/rules/discussions)
