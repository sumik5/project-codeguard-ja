---
description: HTTPセキュリティヘッダーベストプラクティス
languages:
- c
- go
- java
- javascript
- php
- python
- ruby
- typescript
- xml
alwaysApply: false
---

## HTTPセキュリティヘッダーガイドライン

このルールは、XSS、クリックジャッキング、情報漏洩、MIMEタイプ攻撃を含む一般的なWeb脆弱性から保護するため、HTTPレスポンスヘッダーの安全な設定を強制します。

### 必須セキュリティヘッダー

1. Content Security Policy (CSP)
   - default-srcディレクティブを含める必要があります
   - 適切な制限を伴うscript-srcディレクティブを含める必要があります
   - クリックジャッキング保護のためframe-ancestorsディレクティブを含める必要があります
   - 例：`Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; frame-ancestors 'none'`

2. Cookie Security
   - すべてのセッション/機密クッキーにSecureフラグが必要です
   - すべてのセッション/機密クッキーにHttpOnlyフラグが必要です
   - すべてのクッキーにSameSite属性（StrictまたはLax）が必要です
   - 例：`Set-Cookie: session=123; Secure; HttpOnly; SameSite=Strict`

3. Cross-Origin Isolation
   - Cross-Origin-Embedder-Policy (COEP)を設定する必要があります
   - Cross-Origin-Resource-Policy (CORP)を設定する必要があります
   - Cross-Origin-Opener-Policy (COOP)を設定する必要があります
   - 例：
     ```
     Cross-Origin-Embedder-Policy: require-corp
     Cross-Origin-Resource-Policy: same-origin
     Cross-Origin-Opener-Policy: same-origin
     ```

4. Transport Security
   - Strict-Transport-Security (HSTS)を設定する必要があります
   - 適切なmax-age（最低1年）を含める必要があります
   - 例：`Strict-Transport-Security: max-age=31536000; includeSubDomains`

5. Cache Control
   - 機密データには適切なCache-Controlを設定する必要があります
   - 例：`Cache-Control: no-store, max-age=0`

6. Content Type Protection
   - X-Content-Type-Optionsを設定する必要があります
   - 例：`X-Content-Type-Options: nosniff`

### 禁止されているヘッダー

以下のヘッダーは存在してはならない、または削除する必要があります：
- X-Powered-By
- Server（または情報を明かさない値を含める必要があります）
- X-AspNet-Version
- X-AspNetMvc-Version

### 必須のヘッダー組み合わせ

特定のセキュリティ機能は複数のヘッダーが効果的に機能するために必要です：

1. クリックジャッキング保護：
   - CSP frame-ancestorsを使用する、または
   - X-Frame-Options: DENYを使用する必要があります

2. XSS保護：
   - 適切なscript-srcを伴うCSPを使用する必要があります
   - X-XSS-Protectionのみに依存してはなりません

3. CORSセキュリティ：
   - Access-Control-Allow-Origin: *を使用してはなりません
   - 許可されたオリジンを明示的にリストアップする必要があります

### 実装例

PHP:
```php
header("X-Frame-Options: DENY");
```

Apache (.htaccess):
```apache
<IfModule mod_headers.c>
Header always set X-Frame-Options "DENY"
</IfModule>
```

IIS (Web.config):
```xml
<system.webServer>
...
 <httpProtocol>
   <customHeaders>
     <add name="X-Frame-Options" value="DENY" />
   </customHeaders>
 </httpProtocol>
...
</system.webServer>
```

HAProxy:
```
http-response set-header X-Frame-Options DENY
```

Nginx:
```nginx
add_header "X-Frame-Options" "DENY" always;
```

Express.js:
```javascript
const helmet = require('helmet');
const app = express();
// Sets "X-Frame-Options: SAMEORIGIN"
app.use(
 helmet.frameguard({
   action: "sameorigin",
 })
);
```

### テストツール

Mozilla Observatoryは、Webサイトのヘッダー状態を確認できるオンラインツールです。

SmartScannerには、HTTPヘッダーのセキュリティをテストするための専用テストプロファイルがあります。オンラインツールは通常、指定されたアドレスのホームページをテストしますが、SmartScannerはWebサイト全体をスキャンし、すべてのWebページに適切なHTTPヘッダーが設定されていることを確認します。