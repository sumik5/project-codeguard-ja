---
description: クロスサイトリーク（XS-Leaks）の防止
languages:
- c
- javascript
- typescript
alwaysApply: false
---

アプリケーションをクロスサイトリーク（XS-Leaks）から保護することは、ユーザーのプライバシーを守るために重要です。XS-Leaksは、ブラウザの微妙な動作を悪用してオリジン間で機密性の高いユーザー情報を抽出する脆弱性のクラスです。

XS-Leaksは、攻撃者のWebサイトが以下のようなサイドチャネルを通じて別のWebサイト上のユーザーの状態に関する情報を推測できる場合に発生します:

- エラーメッセージ
- フレームカウント
- リソースタイミング
- キャッシュプロービング
- レスポンスサイズ検出

これらの攻撃は、ユーザーがログインしているかどうか、特定のアカウント詳細、またはクロスオリジンリソースからデータを抽出することさえ可能な機密情報を明らかにすることができます。

適切に設定されたCookieは、XS-Leaksに対する第一の防御線です。例えば:

```javascript
// 安全な属性を持つJavaScriptでのCookie設定
document.cookie = "sessionId=abc123; SameSite=Strict; Secure; HttpOnly; Path=/";
```

サーバーサイドでのCookie設定（Express.jsの例）:

```javascript
app.use(session({
  secret: 'your-secret-key',
  cookie: {
    sameSite: 'strict',  // オプション: strict, lax, none
    secure: true,         // HTTPSが必要
    httpOnly: true        // JavaScriptアクセスを防止
  }
}));
```

HTTPレスポンスヘッダー内:

```http
Set-Cookie: sessionId=abc123; SameSite=Strict; Secure; HttpOnly; Path=/
```



* 必ず`SameSite`属性を指定してください:
  * 機密性の高いアクションに関連するCookieには`SameSite=Strict`を使用
  * サイトへの通常のナビゲーションで必要なCookieには`SameSite=Lax`を使用
  * サードパーティでの使用が絶対に必要な場合のみ`SameSite=None; Secure`を使用

* ブラウザのデフォルトに依存しないでください。ブラウザやバージョンによって異なる可能性があります

### フレーミング保護

潜在的に悪意のあるサイトによってサイトがフレーム化されることを防止します:

```javascript
// Express.jsアプリケーションでの実装
app.use((req, res, next) => {
  // CSP frame-ancestorsディレクティブ（モダンなアプローチ）
  res.setHeader(
    'Content-Security-Policy',
    "frame-ancestors 'self' https://trusted-parent.com"
  );

  // X-Frame-Options（レガシーフォールバック）
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');

  next();
});
```

Fetch Metadataヘッダーを使用して疑わしいクロスオリジンリクエストを検出してブロックします:

```javascript
// Express.js 機密エンドポイント保護ミドルウェア
function secureEndpoint(req, res, next) {
  // Fetch Metadataヘッダーを取得
  const fetchSite = req.get('Sec-Fetch-Site') || 'unknown';
  const fetchMode = req.get('Sec-Fetch-Mode') || 'unknown';
  const fetchDest = req.get('Sec-Fetch-Dest') || 'unknown';

  // 機密エンドポイントへのクロスサイトリクエストをブロック
  if (fetchSite === 'cross-site' && req.path.startsWith('/api/sensitive')) {
    return res.status(403).send('Cross-site requests not allowed');
  }

  // 信頼されていないサイトからのiframe埋め込みをブロック
  if (fetchDest === 'iframe' && fetchSite === 'cross-site') {
    return res.status(403).send('Embedding not allowed');
  }

  next();
}

app.use(secureEndpoint);
```

### 安全なクロスオリジン通信

クロスオリジン通信に`postMessage`を使用する場合:

```javascript
// 安全でない - 絶対にこれを実行しないでください
window.postMessage(sensitiveData, '*');

// 安全 - 常に正確なターゲットオリジンを指定
window.postMessage(sensitiveData, 'https://trusted-receiver.com');

// メッセージを受信する際は、常にオリジンを検証
window.addEventListener('message', (event) => {
  // 常にメッセージのオリジンを検証
  if (event.origin !== 'https://trusted-sender.com') {
    console.error('Received message from untrusted origin:', event.origin);
    return;
  }

  // メッセージを処理
  processMessage(event.data);
});
```

### ブラウジングコンテキストの分離

Cross-Origin-Opener-Policy（COOP）を使用してサイトを潜在的な攻撃者から分離します:

```http
Cross-Origin-Opener-Policy: same-origin
```

Express.jsでの実装:

```javascript
app.use((req, res, next) => {
  res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
  next();
});
```

最大限の分離のために、Cross-Origin-Embedder-Policy（COEP）と組み合わせます:

```javascript
app.use((req, res, next) => {
  res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
  res.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
  next();
});
```

### キャッシュベースのリークの防止

キャッシュプロービング攻撃から機密リソースを保護します:

```javascript
// Express.js 機密エンドポイント用ミドルウェア
app.get('/api/sensitive-data', (req, res) => {
  // キャッシュプロービングを防ぐためにユーザー固有のトークンを追加
  const userToken = req.user.securityToken;

  // 機密リソースのキャッシュを無効化
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Pragma', 'no-cache');

  // 一意性を確保するためにレスポンスにユーザートークンを追加
  const data = { userToken, sensitiveData: 'secret information' };
  res.json(data);
});
```

ユーザーの状態を明らかにする可能性のある静的リソースの場合:

```javascript
// 機密リソースのURLにユーザー固有のトークンを追加
function getUserSpecificUrl(baseUrl) {
  const userToken = generateUserToken();
  return `${baseUrl}?token=${userToken}`;
}

const profileImageUrl = getUserSpecificUrl('/images/profile.jpg');
```

### 包括的な防御戦略

XS-Leaksに対する堅牢な防御のためにこれらのヘッダーを実装してください:

```javascript
app.use((req, res, next) => {
  // フレーミング保護
  res.setHeader('Content-Security-Policy', "frame-ancestors 'self'");
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');

  // リソース分離
  res.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
  res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');

  // 動的コンテンツのキャッシュ制御
  if (req.path.startsWith('/api/')) {
    res.setHeader('Cache-Control', 'no-store');
  }

  next();
});
```
