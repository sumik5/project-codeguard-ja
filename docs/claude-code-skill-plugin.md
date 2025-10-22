# CodeGuard Claude Code プラグイン

## 概要

このドキュメントでは、Project CodeGuardをClaude Codeプラグイン（Agentスキル）としてパッケージ化し、AIアシスト型コーディングワークフローで効果的に使用する方法を説明します。

Project CodeGuardは、**オープンソースでモデル非依存のセキュリティフレームワーク**であり、セキュアバイデフォルトの実践をAIコーディングワークフローに組み込みます。このプラグインにより、これらのセキュリティルールをClaude Codeと簡単に統合できます。

## Agentスキルとは

Agentスキルは、Claudeがタスクのコンテキストに基づいて自律的に使用するモデル呼び出し可能な機能です。CodeGuardセキュリティスキルは、Claudeがコードを書いたり、レビューしたり、変更したりする際に自動的に適用する包括的なセキュリティガイダンスを提供します。

## インストール

### 前提条件

- Claude Codeがインストール済み
- Claude Codeのプラグインシステムに関する基本的な知識

### インストール手順

1. **Project CodeGuardマーケットプレイスを追加:**
   ```bash
   /plugin marketplace add project-codeguard/rules
   ```

2. **セキュリティプラグインをインストール:**
   ```bash
   /plugin install codeguard-security@project-codeguard
   ```

3. **Claude Codeを再起動**（プロンプトが表示された場合）

4. **インストールを確認:**
   スキルは自動的に読み込まれます。コーディングを開始すると、Claudeが自動的にセキュリティルールを適用します。

## 動作原理

CodeGuardスキルは、言語、フレームワーク、テクノロジースタック全体にわたる主要なセキュリティドメインをカバーする**22のセキュリティルールファイル**を統合します。このスキルは、シンプルながら強力なワークフローに従います。

### スキルの有効化

スキルは以下の場合に自動的に有効化されます：
- 任意の言語で新しいコードを記述する
- 既存のコードをレビューまたは変更する
- セキュリティに配慮した機能（認証、暗号化、データ処理）を実装する
- ユーザー入力、データベース、API、または外部サービスを扱う
- クラウドインフラ、CI/CDパイプライン、またはコンテナを設定する
- 機密データ、認証情報、または暗号化操作を処理する

### セキュリティワークフロー

コードを生成またはレビューする際、Claudeは次の3ステップのワークフローに従います：

**1. 初期セキュリティチェック**
- 認証情報を扱うか？ → `codeguard-1-hardcoded-credentials`を適用
- 使用されている言語は？ → 適用可能な言語固有のルールを特定
- 関与するセキュリティドメインは？ → 関連するルールファイルを読み込む

**2. コード生成**
- 関連するCodeGuardルールからセキュアバイデフォルトパターンを適用
- 選択理由を説明するセキュリティ関連のコメントを追加

**3. セキュリティレビュー**
- 各ルールの実装チェックリストに照らしてレビュー
- ハードコードされた認証情報やシークレットがないことを確認
- 適用可能なすべてのルールが遵守されていることを検証
- 適用されたセキュリティルールを説明
- 実装されたセキュリティ機能を強調

### ルールカテゴリ

**常時適用ルール**（すべてのコード操作でチェックされる4つの重要ルール）：
- `codeguard-1-hardcoded-credentials` - シークレットや認証情報をハードコードしない
- `codeguard-1-crypto-algorithms` - 最新の暗号化アルゴリズムを使用
- `codeguard-1-digital-certificates` - 証明書のセキュリティを検証
- `codeguard-1-safe-c-functions` - 安全でないC/C++関数を置き換える

**コンテキスト固有ルール**（技術と機能に基づいて適用される18ルール）：
- 入力検証、認証、認可、API、データストレージ、プライバシー、ロギング、暗号化、ファイル処理、シリアル化、サプライチェーン、DevOps、クラウド、Kubernetes、IaC、フレームワーク、モバイルセキュリティ

## 使用例

### 例1: データベースコード作成

```python
# Claudeは自動的にパラメータ化クエリを使用
def get_user(email):
    # codeguard-0-input-validation-injectionに従ったセキュアパターン
    query = "SELECT * FROM users WHERE email = ?"
    return cursor.execute(query, (email,))
```

### 例2: APIキーの処理

```javascript
// Claudeはハードコードされた認証情報を防止し、
// 環境変数を提案
const apiKey = process.env.STRIPE_API_KEY;
if (!apiKey) {
  throw new Error("STRIPE_API_KEY not configured");
}
```

### 例3: パスワードハッシュ化

```python
# Claudeは最新のパスワードハッシュ化を提案
from argon2 import PasswordHasher
ph = PasswordHasher()
password_hash = ph.hash(password)
```

### 例4: ファイルアップロードセキュリティ

```javascript
// Claudeはファイル検証を強制
const multer = require('multer');
const upload = multer({
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB制限
  fileFilter: (req, file, cb) => {
    // 拡張子だけでなく、コンテンツでファイルタイプを検証
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only images allowed'));
    }
  }
});
```

## チームへの展開

組織では、すべての開発者に自動的にCodeGuardを展開できます：

1. プロジェクトの`.claude/settings.json`に追加：
   ```json
   {
     "marketplaces": [{"source": "project-codeguard/rules"}],
     "plugins": [
       {
         "name": "codeguard-security",
         "marketplace": "project-codeguard",
         "enabled": true
       }
     ]
   }
   ```

2. チームメンバーがリポジトリフォルダを信頼

3. CodeGuardがすべてのユーザーに自動的にインストール

## すべてのセキュリティルール

プラグインには、2つのカテゴリに分類された22の包括的なセキュリティルールが含まれています：

### 常時適用ルール（4ルール）

これらの重要なルールは、**すべての**コード操作でチェックされます：

| ルール | 説明 |
|------|------|
| `codeguard-1-hardcoded-credentials` | ソースコード内のシークレット、パスワード、APIキー、トークンを防止 |
| `codeguard-1-crypto-algorithms` | 弱いアルゴリズム（MD5、SHA-1、DES）を禁止し、最新の代替手段を使用 |
| `codeguard-1-digital-certificates` | 証明書の有効期限、キー強度、署名アルゴリズムを検証 |
| `codeguard-1-safe-c-functions` | 安全でないC/C++関数（gets、strcpy、strcat、sprintf）を置き換え |

### コンテキスト固有ルール（18ルール）

これらのルールは、実装されているプログラミング言語、フレームワーク、または機能に基づいて適用されます。Claudeはコンテキストに基づいて関連するルールを自動的に選択します：

| セキュリティドメイン | ルール |
|------------------|-------|
| **入力とインジェクション** | `codeguard-0-input-validation-injection` |
| **認証** | `codeguard-0-authentication-mfa` |
| **認可** | `codeguard-0-authorization-access-control` |
| **セッション** | `codeguard-0-session-management-and-cookies` |
| **APIとWeb** | `codeguard-0-api-web-services`, `codeguard-0-client-side-web-security` |
| **データとプライバシー** | `codeguard-0-data-storage`, `codeguard-0-privacy-data-protection`, `codeguard-0-logging` |
| **暗号化** | `codeguard-0-additional-cryptography` |
| **ファイルとシリアル化** | `codeguard-0-file-handling-and-uploads`, `codeguard-0-xml-and-serialization` |
| **インフラ** | `codeguard-0-supply-chain-security`, `codeguard-0-devops-ci-cd-containers`, `codeguard-0-cloud-orchestration-kubernetes`, `codeguard-0-iac-security` |
| **プラットフォーム** | `codeguard-0-framework-and-languages`, `codeguard-0-mobile-apps` |

> **注意:** 各ルールファイルには、詳細なガイダンス、チェックリスト、例が含まれています。Claudeはコードのコンテキストに基づいてこれらを自動的に参照します。

## 更新

最新のセキュリティルールに更新するには：

```bash
/plugin update codeguard-security@project-codeguard
```

## カスタマイズ

### プラグインの無効化

必要に応じて一時的に無効化：

```bash
/plugin disable codeguard-security@project-codeguard
```

再有効化：

```bash
/plugin enable codeguard-security@project-codeguard
```

### 特定のルールファイルの使用

すべてのルールファイルは、プラグイン内の`skills/software-security/rules/`ディレクトリにあります。プロンプトで特定のルールを参照できます：

```
Claude、この認証コードをcodeguard-0-authentication-mfa.mdガイドラインに
照らしてレビューしてください
```

### カスタムワークフローの作成

カスタムセキュリティレビューワークフローを作成できます：

```
Claude、このコードに対して以下のセキュリティチェックを実施してください：
1. ハードコードされた認証情報をチェック
2. 入力のサニタイゼーションを検証
3. 認証実装を確認
4. 認可ロジックをレビュー
各チェックには関連するCodeGuardルールを使用してください。
```

## トラブルシューティング

### プラグインが読み込まれない

1. インストールを確認: `/plugin` → "プラグインの管理"
2. `codeguard-security`がリストされ、有効になっていることを確認
3. Claude Codeを再起動

### ルールが適用されない

1. プラグインが有効になっていることを確認
2. プロンプトでセキュリティについて明示的に言及してみる
3. サポートされている言語で作業していることを確認

### プラグインバージョンの確認

```bash
/plugin list
```

`codeguard-security@project-codeguard`を探し、バージョン番号を確認します。

## ベストプラクティス

### 開発時

1. **自動化を信頼**: Claudeがセキュリティルールを自動的に適用するのを許可
2. **提案から学ぶ**: Claudeがセキュアな代替案を提案したら、その理由を理解
3. **説明を求める**: Claudeにセキュリティ推奨事項の説明を要求
4. **プロアクティブなセキュリティ**: 機能実装前にClaude にセキュリティガイダンスを求める

### コードレビュー時

1. **明示的なセキュリティレビュー**: Claudeに包括的なセキュリティ分析を依頼
2. **特定ルールの参照**: 集中レビューのためにルール名を言及（例：「codeguard-0-authentication-mfaに照らしてレビュー」）
3. **常時適用ルールをチェック**: 認証情報、暗号化アルゴリズム、証明書、C関数が安全に処理されていることを確認
4. **ワークフローを検証**: Claudeが3ステップのセキュリティワークフローに従ったことを確認

### チーム向け

1. **インストールの標準化**: チーム全体で一貫したセットアップのために`.claude/settings.json`を使用
2. **バージョン管理**: チームが使用するプラグインバージョンを追跡
3. **定期的な更新**: 最新のセキュリティガイダンスでルールを最新の状態に保つ
4. **学びを共有**: スタック固有のセキュリティパターンを文書化
5. **開発者のトレーニング**: チームメンバーがAIアシスト型セキュリティの使い方を理解していることを確認

## プラグインのビルド

Project CodeGuardに貢献している場合、またはプラグインを再ビルドする必要がある場合：

```bash
cd /path/to/project-codeguard/rules
./src/prepare-claude-code-plugin.sh
```

このスクリプトは：
- すべてのルールファイルを`rules/`から`skills/software-security/rules/`にコピー
- プラグイン構造を検証
- 配布またはローカルテスト用にプラグインを準備

## 高度な使用法

### 言語固有のセキュリティレビュー

特定の言語に焦点を当てたレビューを要求：

```
Claude、このPythonコードのセキュリティレビューを以下に重点を置いて実施してください：
- SQLインジェクション防止
- 入力検証
- 認証のベストプラクティス
```

### 機能固有のガイダンス

機能を構築する際にプロアクティブなセキュリティガイダンスを取得：

```
Claude、ファイルアップロード機能を実装しようとしています。
CodeGuardルールに従って、どのようなセキュリティ上の考慮事項を
念頭に置くべきですか？
```

### セキュリティファーストの開発

計画段階からCodeGuardを使用：

```
Claude、Webアプリのセキュアな認証システムの設計を手伝ってください。
CodeGuardルールを使用してアーキテクチャを導いてください。
```

## プラグインアーキテクチャ

### ファイル構造

```
project-codeguard/rules/
├── .claude-plugin/
│   ├── plugin.json                  # プラグインメタデータ
│   └── marketplace.json             # マーケットプレイスカタログ
│
├── skills/
│   └── software-security/
│       ├── SKILL.md                 # スキル定義とワークフロー
│       └── rules/                   # 全22のCodeGuardセキュリティルール
│           ├── codeguard-1-*.md     # 4つの常時適用ルール
│           └── codeguard-0-*.md     # 18のコンテキスト固有ルール
│
└── src/
    └── prepare-claude-code-plugin.sh  # ビルドスクリプト
```

### Claudeによるスキルの使用方法

コードを書いたりレビューしたりする際、Claudeは次のワークフローに従います：

1. **SKILL.mdを読む** - スキルをいつ有効化するか、どのようなワークフローに従うかを理解
2. **初期セキュリティチェック** - 以下に基づいて適用するルールを特定：
   - 認証情報が関与しているか（常時適用ルール）
   - 使用されているプログラミング言語
   - 関与するセキュリティドメイン（認証、暗号化、API等）
3. **セキュリティルールを適用** - 関連するルールファイルを参照して：
   - セキュアバイデフォルトパターンを使用
   - 実装チェックリストに従う
   - 言語固有のガイダンスを適用
4. **セキュアなコードを生成** - 以下のコードを生成：
   - 認証情報をハードコードしない
   - 最新の暗号化アルゴリズムを使用
   - 入力検証を実装
   - セキュリティのベストプラクティスに従う
5. **説明を提供** - 適用されたセキュリティルールを文書化し、実装されたセキュリティ機能を強調

## コントリビューション

プラグインに関する問題を見つけた場合、または改善したい場合：

1. **問題を報告**: [GitHub Issues](https://github.com/project-codeguard/rules/issues)
2. **ルールを提案**: [GitHub Discussions](https://github.com/project-codeguard/rules/discussions)
3. **貢献**: [コントリビューションガイド](https://github.com/project-codeguard/rules/blob/main/CONTRIBUTING.md)

## バージョン履歴

### バージョン1.0.0
- 初回リリース
- 22の包括的なセキュリティルール
- 4つの常時適用ルール
- 18のコンテキスト固有ルール
- すべての主要プログラミング言語をサポート
- 完全なテクノロジースタックカバレッジ

## リソース

- **プロジェクトWebサイト**: [https://project-codeguard.org](https://project-codeguard.org)
- **GitHubリポジトリ**: [https://github.com/project-codeguard/rules](https://github.com/project-codeguard/rules)
- **ドキュメント**: [https://project-codeguard.org/getting-started/](https://project-codeguard.org/getting-started/)
- **イシュートラッカー**: [https://github.com/project-codeguard/rules/issues](https://github.com/project-codeguard/rules/issues)

## ライセンス

- **ルール**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **ツール**: Apache License 2.0

## サポート

サポートが必要ですか？私たちがお手伝いします：

1. **ドキュメント**: [スタートガイド](https://project-codeguard.org/getting-started/)から始めてください
2. **コミュニティ**: [GitHub Discussions](https://github.com/project-codeguard/rules/discussions)に参加
3. **問題報告**: [GitHub Issues](https://github.com/project-codeguard/rules/issues)経由でバグを報告

