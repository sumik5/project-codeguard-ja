---
description: Cross-Site Request Forgery (CSRF) Prevention Best Practices
languages:
- c
- go
- html
- java
- javascript
- php
- python
- ruby
- typescript
alwaysApply: false
---

## はじめに

クロスサイトリクエストフォージェリ（CSRF）攻撃は、悪意のあるWebサイト、メール、ブログ、インスタントメッセージ、またはプログラムが、認証されたユーザーのWebブラウザを騙して、信頼されたサイト上で望まない操作を実行させる攻撃です。対象ユーザーがサイトに認証されている場合、保護されていない対象サイトは、正当な認可されたリクエストと偽造された認証済みリクエストを区別できません。

**重要：クロスサイトスクリプティング（XSS）はすべてのCSRF軽減技術を無効化できることを忘れないでください！** アプリケーションでのCSRF保護の最適なアプローチを決定するため、クライアントと認証方法を考慮してください。

## クロスサイトリクエストフォージェリ（CSRF）攻撃の防止

### 実装のベストプラクティス

#### 1. まずXSS脆弱性を修正

クロスサイトスクリプティング（XSS）脆弱性はCSRF保護をバイパスできます。CSRF軽減策と並行して、常にXSS問題に対処してください。

#### 2. フレームワークネイティブのCSRF保護を使用

フレームワーク組み込みのCSRF保護を正しい実装で使用：

* **Angular**: HttpClientをXSRF保護で設定：
  ```typescript
  // app.config.ts
  provideHttpClient(withXsrfConfiguration({
    cookieName: 'XSRF-TOKEN',
    headerName: 'X-XSRF-TOKEN'
  }))
  ```

* **Next.js**: APIルートでcsrfミドルウェアを使用：
  ```javascript
  // pages/api/protected.js
  import { csrf } from 'csrf';
  export default csrf(async (req, res) => {
    // 保護されたエンドポイントのロジック
  });
  ```

* **Spring Security**: CSRF保護を適切に有効化：
  ```java
  @Configuration
  @EnableWebSecurity
  public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
      return http.csrf(Customizer.withDefaults()).build(); // CSRFはデフォルトで有効
    }
  }
  ```

* **Django**: CSRFミドルウェアとテンプレートタグを使用：
  ```python
  # settings.py - CsrfViewMiddlewareが有効であることを確認
  MIDDLEWARE = ['django.middleware.csrf.CsrfViewMiddleware', ...]
  ```

#### 3. シンクロナイザートークンパターンの実装

セッションごとに一意で予測不可能なトークンを生成：

```javascript
// トークン生成: セッションID + シークレットでHMACを使用
const csrfToken = crypto.createHmac('sha256', process.env.CSRF_SECRET)
  .update(req.session.id).digest('hex');
```

**フォーム送信**: トークンを隠しフィールドとして含める：
```html
<input type="hidden" name="_csrf" value="{{csrfToken}}">
```

**AJAXリクエスト**: カスタムヘッダーでトークンを送信：
```javascript
headers: { 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content }
```

#### 4. すべての状態変更リクエストを保護

* **状態変更にGETを決して使用しない**: 状態を変更するすべての操作はPOST、PUT、DELETE、またはPATCHを使用すべきです。
* **すべての安全でないメソッドでトークンを検証**: すべての状態変更リクエストでCSRFトークンを検証してください。

#### 5. トークンの安全な送信と保存

**必須のHTTPS**: CSRFトークン送信には常にHTTPSを強制：
```javascript
// HTTPをHTTPSにリダイレクト
app.use((req, res, next) => {
  if (!req.secure && process.env.NODE_ENV === 'production') {
    return res.redirect(`https://${req.headers.host}${req.url}`);
  }
  next();
});
```

**安全なCookie設定**: CSRFトークンとセッションに適切なCookie属性を使用：
```http
Set-Cookie: __Host-XSRF-TOKEN=abc123; Path=/; Secure; SameSite=Lax
Set-Cookie: __Host-sessionid=xyz789; Path=/; Secure; HttpOnly; SameSite=Lax
```

Cookie属性の要件：
* **Secure**: 必須 - HTTP経由の送信を防止
* **SameSite=Lax**: セキュリティと使いやすさのバランス；高セキュリティアプリケーションには`Strict`を使用
* **__Host-プレフィックス**: サブドメインCookieインジェクション攻撃を防止
* **HttpOnly**: セッションCookieのみに使用（CSRFトークンはJavaScriptアクセスが必要）

#### 6. 多層防御戦略

**複数の保護を組み合わせ**: CSRFトークンをオリジン検証とレート制限と組み合わせる：

```javascript
// 包括的なCSRF保護ミドルウェア
function csrfProtection(req, res, next) {
  // 1. Origin/Refererヘッダーを検証
  const origin = req.headers.origin || req.headers.referer;
  if (!origin || !isValidOrigin(origin)) {
    return res.status(403).json({error: '無効なオリジン'});
  }

  // 2. CSRFトークンを検証
  const token = req.headers['x-csrf-token'] || req.body._csrf;
  if (!isValidCsrfToken(token, req.session.id)) {
    return res.status(403).json({error: '無効なCSRFトークン'});
  }

  // 3. セッションごとのレート制限
  if (exceedsRateLimit(req.session.id)) {
    return res.status(429).json({error: 'レート制限超過'});
  }

  next();
}

function isValidOrigin(origin) {
  const allowedOrigins = ['https://yourdomain.com', 'https://app.yourdomain.com'];
  return allowedOrigins.includes(new URL(origin).origin);
}
```

**トークンベース認証（SPA）**: JWT/ベアラートークンを使用するSPA向け：
```javascript
// トークンベース認証のカスタムヘッダーアプローチ
function apiCsrfProtection(req, res, next) {
  // 状態変更操作にカスタムヘッダーを要求
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
    if (!req.headers['x-requested-with']) {
      return res.status(403).json({error: '必須ヘッダーが不足'});
    }
  }
  next();
}
```

#### 7. 特殊ケース

**ログインCSRF保護**: ログインフォームにプリセッショントークンを使用：
```javascript
// 認証前にトークンを生成、ログイン後にセッションを破棄
const loginToken = crypto.randomBytes(32).toString('hex');
req.session.loginCsrfToken = loginToken;
```

**クライアントサイドCSRF防止**: JavaScriptで入力ソースを検証：
```javascript
// リクエスト生成にURLパラメータ/フラグメントを使用しない
// リクエスト前にエンドポイントURLを許可リストで検証
const allowedEndpoints = ['/api/profile', '/api/settings'];
if (!allowedEndpoints.includes(requestEndpoint)) {
  throw new Error('無効なエンドポイント');
}
```

#### 8. テストと検証

必須のCSRF防御テスト：
* クロスオリジンフォーム送信はブロックされるべき
* すべての状態変更リクエストでCSRFトークンが検証されなければならない
* さまざまなSameSite Cookie設定でテスト
* Origin/Refererヘッダー検証が正しく機能することを確認

これらの多層防御は、使いやすさを維持しながら堅牢なCSRF保護を提供します。