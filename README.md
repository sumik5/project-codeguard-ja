# Project CodeGuard: AIコーディングエージェント向けセキュリティルール
![Securing](https://img.shields.io/badge/Securing%20AI%20Generated%20Code-green)
![Open Source](https://img.shields.io/badge/Now-Open%20Source-brightgreen)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

このプロジェクトは、AIモデルに依存しないセキュリティフレームワークおよびルールセット（Ciscoで開発時、内部的に「Project CodeGuard」と呼ばれていました）であり、AIコーディングワークフロー（生成とレビュー）にセキュアバイデフォルトの実践を組み込みます。コアセキュリティルール、人気のコーディングエージェント向けトランスレーター、およびルール準拠をテストするバリデーターを提供します。


## なぜProject CodeGuardが必要なのか？

AIコーディングエージェントはソフトウェアエンジニアリングを変革していますが、このスピードはセキュリティ脆弱性を引き起こす可能性があります。あなたのAIコーディングエージェント実装はセキュリティ脆弱性を生み出していませんか？

- ❌ 入力検証のスキップ
- ❌ シークレットと認証情報のハードコーディング
- ❌ 弱い暗号化アルゴリズムの使用
- ❌ 安全でない関数への依存
- ❌ 認証/認可チェックの欠落
- ❌ その他のセキュリティベストプラクティスの欠落

Project CodeGuardは、セキュリティベストプラクティスをAIコーディングエージェントワークフローに直接組み込むことで、この問題を解決します。

**コード生成中および生成後に。**

Project CodeGuardは、AIコーディングのライフサイクル全体にシームレスに統合できるよう設計されています。
- **コード生成前**: ルールを製品設計や仕様駆動開発に活用できます。AIコーディングエージェントの「計画フェーズ」でルールを使用し、最初からセキュアなパターンへとモデルを導きます。
- **コード生成中**: ルールがAIエージェントによるコード記述中のセキュリティ問題を防止します。
- **コード生成後**: Cursor、GitHub Copilot、Codex、Windsurf、Claude Codeなどのエージェントが、コードレビューにルールを活用できます。


## セキュリティカバレッジ

当プロジェクトのルールは、以下の重要なセキュリティドメインをカバーしています：

- **🔐 暗号化**: 安全なアルゴリズム（ポスト量子暗号を含む）、安全な鍵管理、証明書検証
- **🛡️ 入力検証**: SQLインジェクション防止、XSS保護、コマンドインジェクション防御
- **🔑 認証**: MFAベストプラクティス、OAuth/OIDC、安全なセッション管理
- **⚡ 認可**: RBAC/ABAC、アクセス制御、IDOR防止
- **📦 サプライチェーン**: 依存関係のセキュリティ、SBOM生成、脆弱性管理
- **☁️ クラウドセキュリティ**: IaCの強化、コンテナセキュリティ、Kubernetesベストプラクティス
- **📱 プラットフォームセキュリティ**: モバイルアプリ、Webサービス、APIセキュリティ
- **🔍 データ保護**: プライバシー、保存時/転送時の暗号化、安全なストレージ

## クイックスタート

数分で始められます：

1. **ルールのダウンロード**: [リリースページ](https://github.com/project-codeguard/rules/releases)からダウンロード
2. **プロジェクトへコピー**: AIエージェントおよびIDE固有のルールをリポジトリに配置
3. **コーディング開始**: AIアシスタントが自動的にセキュリティベストプラクティスに従います

- 詳細は [Get Started →](https://project-codeguard.org/getting-started/) を参照してください


## 仕組み

1. **セキュリティルール**を統一されたMarkdown形式で記述
2. **変換ツール**がルールをIDEおよびAIエージェント形式に変換
3. **AIアシスタント**がコード生成またはレビュー時にこれらのルールを参照
4. **セキュアなコード**が開発者の介入なしに自動的に生成されます

## コミュニティ

- **📋 Issues**: [バグ報告や機能リクエスト](https://github.com/project-codeguard/rules/issues)
- **💬 Discussions**: [会話に参加](https://github.com/project-codeguard/rules/discussions)
- **🤝 Contributing**: [コントリビュート方法を学ぶ](https://github.com/project-codeguard/rules/blob/main/CONTRIBUTING.md)


## 📄 ライセンス

このプロジェクトはデュアルライセンスを採用しています：

- **セキュリティルールおよびドキュメント**: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)でライセンス - すべてのルールファイル、ドキュメント、プロジェクトコンテンツが含まれます
- **ソースコードおよびツール**: `src/`ディレクトリは[Apache License 2.0](src/LICENSE.md)でライセンス - 変換ツール、バリデーター、その他のソフトウェアコンポーネントが含まれます

このライセンスアプローチにより、セキュリティルールは自由にアクセス可能かつ再利用可能であり続け、ソフトウェアコンポーネントには適切な条件が提供されます。


Copyright © 2025 Cisco Systems, Inc.
