---
description: HTTP Strict Transport Securityのベストプラクティス
languages:
- c
- go
- java
- javascript
- php
- python
- ruby
- typescript
alwaysApply: false
---

## HTTP Strict Transport Securityガイドライン

このルールは、すべての通信がHTTPS経由で行われることを保証することでユーザーを保護するため、HTTP Strict Transport Security（HSTS）ヘッダーの安全な設定を強制します。

### 導入

HTTP Strict Transport Security（HSTS）は、特別なレスポンスヘッダーを通じてWebアプリケーションによって指定されるオプトインのセキュリティ強化です。サポートされているブラウザがこのヘッダーを受信すると、指定されたドメインへのHTTP経由での通信の送信を防ぎ、代わりにすべての通信をHTTPS経由で送信します。また、ブラウザでのHTTPSクリックスループロンプトも防ぎます。

重要な要件：Strict-Transport-SecurityヘッダーはHTTPS接続経由でのみ尊重され、RFC 6797に従い、HTTP経由で送信された場合は完全に無視されます。

### 対処される脅威

HSTSは以下から保護します：
- ユーザーが`http://example.com`をブックマークまたは手動で入力した場合の中間者攻撃
- WebアプリケーションがHTTPリンクを誤って含むか、HTTP経由でコンテンツを提供する場合
- 無効な証明書を使用する中間者攻撃者（HSTSはユーザーが不正な証明書を受け入れることを防ぎます）

### 必須設定

1. 基本HSTSヘッダー（テストフェーズ）：
   ```
   Strict-Transport-Security: max-age=86400; includeSubDomains
   ```

2. 本番HSTSヘッダー（最小1年）：
   ```
   Strict-Transport-Security: max-age=31536000; includeSubDomains
   ```

3. プリロード対応HSTSヘッダー：
   ```
   Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
   ```

### 段階的ロールアウト要件

1. フェーズ1 - テスト（推奨される最初のステップ）：
   - 初期テストには短いmax-age（600-86400秒）を使用
   - HTTPコンテンツまたは機能の問題を監視

2. フェーズ2 - 本番：
   - max-ageを最小1年（31536000秒）に増加
   - すべてのサブドメインがHTTPSをサポートする場合のみ`includeSubDomains`を追加

3. フェーズ3 - プリロード（オプション）：
   - 徹底的なテスト後にのみ`preload`ディレクティブを追加
   - hstspreload.orgでドメインをHSTSプリロードリストに提出
   - 警告：プリロードは事実上永続的であり、すべてのサブドメインに影響します

### 実装例

1年のmax-ageを使用したシンプルな例（includeSubDomainsなしでは危険）：
```
Strict-Transport-Security: max-age=31536000
```

サブドメイン保護を伴う安全な例：
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

初期ロールアウトテスト用の短いmax-age：
```
Strict-Transport-Security: max-age=86400; includeSubDomains
```

### 監視と検証

デプロイ後に必要なアクション：
- すべてのHTTPSレスポンスでHSTSヘッダーの存在を検証
- 混在コンテンツ警告についてブラウザコンソールを監視
- HTTPリファレンスについてすべての内部リンクとリダイレクトを監査
- includeSubDomainsを有効化する前にサブドメインHTTPS可用性をテスト
- 設定を検証するためMozilla ObservatoryやSecurity Headersのようなツールを使用

### ブラウザサポート

HSTSはすべての最新ブラウザでサポートされています。唯一の注目すべき例外はOpera Miniです。
