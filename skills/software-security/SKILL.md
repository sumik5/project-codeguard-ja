---
name: software-security
description: Project CodeGuardと統合し、AIコーディングエージェントがセキュアなコードを記述し、一般的な脆弱性を防ぐのを支援するソフトウェアセキュリティスキル。コードの記述、レビュー、変更時にこのスキルを使用して、セキュアバイデフォルトの実践に従うことを保証します。**重要：すべての応答、説明、セキュリティレビュー結果は必ず日本語で提供してください。**
metadata:
  codeguard-version: "1.0.0"
  framework: "Project CodeGuard"
  purpose: "AIコーディングワークフローにセキュアバイデフォルトの実践を組み込む"
  language: "ja"
  response-language: "Japanese"
  output-format: "すべての出力は日本語で記述すること"
---

# ソフトウェアセキュリティスキル（Project CodeGuard）

## 🌐 言語設定（最重要）

**このスキルを実行する際の必須要件:**
- **すべての出力を日本語で記述すること**
- **セキュリティレビュー結果は日本語で提供すること**
- **脆弱性の説明は日本語で記述すること**
- **推奨事項は日本語で提示すること**
- **分析結果、タスク説明、完了報告もすべて日本語で記述すること**

英語での応答は禁止です。必ず日本語で応答してください。

---

このスキルは、AIコーディングエージェントがセキュアなコードを生成し、一般的な脆弱性を防ぐのを支援する包括的なセキュリティガイダンスを提供します。これは**Project CodeGuard**に基づいており、AIコーディングワークフローにセキュアバイデフォルトの実践を組み込むオープンソースでモデル非依存のセキュリティフレームワークです。

## このスキルを使用するタイミング
このスキルは以下の場合に有効化されます：
- 任意の言語で新しいコードを記述する
- 既存のコードをレビューまたは変更する
- セキュリティに配慮した機能（認証、暗号化、データ処理など）を実装する
- ユーザー入力、データベース、API、または外部サービスを扱う
- クラウドインフラ、CI/CDパイプライン、またはコンテナを設定する
- 機密データ、認証情報、または暗号化操作を処理する

## このスキルの使用方法
コードを記述またはレビューする際：
1. 常時適用ルール: 一部のルールはすべてのコード操作でチェックする必要があります：
- `codeguard-1-hardcoded-credentials.md` - シークレット、パスワード、APIキー、トークンをハードコードしない
- `codeguard-1-crypto-algorithms.md` - 最新のセキュアな暗号化アルゴリズムのみを使用
- `codeguard-1-digital-certificates.md` - デジタル証明書を安全に検証・管理
- `codeguard-1-safe-c-functions.md` - 安全でないC/C++関数を避け、安全な代替手段を使用
2. コンテキスト固有ルール: 実装される機能の言語に基づいて、以下の表を使用して/rulesディレクトリからルールを適用：


| 言語 | 適用するルールファイル |
|----------|---------------------|
| c | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authentication-mfa.md, codeguard-0-authorization-access-control.md, codeguard-0-client-side-web-security.md, codeguard-0-data-storage.md, codeguard-0-file-handling-and-uploads.md, codeguard-0-framework-and-languages.md, codeguard-0-iac-security.md, codeguard-0-input-validation-injection.md, codeguard-0-logging.md, codeguard-0-session-management-and-cookies.md, codeguard-0-xml-and-serialization.md |
| d | codeguard-0-iac-security.md |
| docker | codeguard-0-devops-ci-cd-containers.md, codeguard-0-supply-chain-security.md |
| go | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authentication-mfa.md, codeguard-0-authorization-access-control.md, codeguard-0-file-handling-and-uploads.md, codeguard-0-input-validation-injection.md, codeguard-0-session-management-and-cookies.md, codeguard-0-xml-and-serialization.md |
| html | codeguard-0-client-side-web-security.md, codeguard-0-input-validation-injection.md, codeguard-0-session-management-and-cookies.md |
| java | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authentication-mfa.md, codeguard-0-authorization-access-control.md, codeguard-0-file-handling-and-uploads.md, codeguard-0-framework-and-languages.md, codeguard-0-input-validation-injection.md, codeguard-0-mobile-apps.md, codeguard-0-session-management-and-cookies.md, codeguard-0-xml-and-serialization.md |
| javascript | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authentication-mfa.md, codeguard-0-authorization-access-control.md, codeguard-0-client-side-web-security.md, codeguard-0-cloud-orchestration-kubernetes.md, codeguard-0-data-storage.md, codeguard-0-devops-ci-cd-containers.md, codeguard-0-file-handling-and-uploads.md, codeguard-0-framework-and-languages.md, codeguard-0-iac-security.md, codeguard-0-input-validation-injection.md, codeguard-0-logging.md, codeguard-0-mobile-apps.md, codeguard-0-privacy-data-protection.md, codeguard-0-session-management-and-cookies.md, codeguard-0-supply-chain-security.md |
| kotlin | codeguard-0-additional-cryptography.md, codeguard-0-authentication-mfa.md, codeguard-0-framework-and-languages.md, codeguard-0-mobile-apps.md |
| matlab | codeguard-0-additional-cryptography.md, codeguard-0-authentication-mfa.md, codeguard-0-mobile-apps.md, codeguard-0-privacy-data-protection.md |
| perl | codeguard-0-mobile-apps.md |
| php | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authentication-mfa.md, codeguard-0-authorization-access-control.md, codeguard-0-client-side-web-security.md, codeguard-0-file-handling-and-uploads.md, codeguard-0-framework-and-languages.md, codeguard-0-input-validation-injection.md, codeguard-0-session-management-and-cookies.md, codeguard-0-xml-and-serialization.md |
| powershell | codeguard-0-devops-ci-cd-containers.md, codeguard-0-iac-security.md, codeguard-0-input-validation-injection.md |
| python | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authentication-mfa.md, codeguard-0-authorization-access-control.md, codeguard-0-file-handling-and-uploads.md, codeguard-0-framework-and-languages.md, codeguard-0-input-validation-injection.md, codeguard-0-session-management-and-cookies.md, codeguard-0-xml-and-serialization.md |
| ruby | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authentication-mfa.md, codeguard-0-authorization-access-control.md, codeguard-0-file-handling-and-uploads.md, codeguard-0-framework-and-languages.md, codeguard-0-iac-security.md, codeguard-0-input-validation-injection.md, codeguard-0-session-management-and-cookies.md, codeguard-0-xml-and-serialization.md |
| shell | codeguard-0-devops-ci-cd-containers.md, codeguard-0-iac-security.md, codeguard-0-input-validation-injection.md |
| sql | codeguard-0-data-storage.md, codeguard-0-input-validation-injection.md |
| swift | codeguard-0-additional-cryptography.md, codeguard-0-authentication-mfa.md, codeguard-0-mobile-apps.md |
| typescript | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authentication-mfa.md, codeguard-0-authorization-access-control.md, codeguard-0-client-side-web-security.md, codeguard-0-file-handling-and-uploads.md, codeguard-0-framework-and-languages.md, codeguard-0-input-validation-injection.md, codeguard-0-session-management-and-cookies.md |
| vlang | codeguard-0-client-side-web-security.md |
| xml | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-devops-ci-cd-containers.md, codeguard-0-framework-and-languages.md, codeguard-0-mobile-apps.md, codeguard-0-xml-and-serialization.md |
| yaml | codeguard-0-additional-cryptography.md, codeguard-0-api-web-services.md, codeguard-0-authorization-access-control.md, codeguard-0-cloud-orchestration-kubernetes.md, codeguard-0-data-storage.md, codeguard-0-devops-ci-cd-containers.md, codeguard-0-framework-and-languages.md, codeguard-0-iac-security.md, codeguard-0-logging.md, codeguard-0-privacy-data-protection.md, codeguard-0-supply-chain-security.md |


3. プロアクティブなセキュリティ: 脆弱性を避けるだけでなく、セキュアなパターンを積極的に実装：
- データベースアクセスにはパラメータ化クエリを使用
- すべてのユーザー入力を検証・サニタイズ
- 最小権限の原則を適用
- 最新の暗号化アルゴリズムとライブラリを使用
- 多層防御戦略を実装

## CodeGuardセキュリティルール
セキュリティルールは`rules/`ディレクトリにあります。

### 使用ワークフロー
コードを生成またはレビューする際、次のワークフローに従います：

### 1. 初期セキュリティチェック
コードを記述する前に：
- チェック: 認証情報を扱うか？ → codeguard-1-hardcoded-credentialsを適用
- チェック: 使用している言語は？ → 適用可能な言語固有のルールを特定
- チェック: 関与するセキュリティドメインは？ → 関連するルールファイルを読み込む

### 2. コード生成
コード記述中：
- 関連するProject CodeGuardルールからセキュアバイデフォルトパターンを適用
- 選択理由を説明するセキュリティ関連のコメントを追加

### 3. セキュリティレビュー
コード記述後：
- 各ルールの実装チェックリストに照らしてレビュー
- ハードコードされた認証情報やシークレットがないことを確認
- 該当する場合、すべてのルールが正しく遵守されていることを検証
- 適用されたセキュリティルールを説明
- 実装されたセキュリティ機能を強調

**セキュリティレビューの出力形式:**
- すべてのセキュリティレビュー結果は**日本語**で提供すること
- 脆弱性の説明、推奨事項、コード例の説明はすべて日本語で記述すること
- 技術用語は日本語化し、必要に応じて英語を併記すること（例: SQLインジェクション、クロスサイトスクリプティング（XSS））
