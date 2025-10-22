---
description: Node.jsセキュリティベストプラクティス
languages:
- c
- javascript
- typescript
alwaysApply: false
---

## Node.jsセキュリティガイドライン

一般的な脆弱性と攻撃を防ぐために安全なNode.jsアプリケーションを開発するための必須セキュリティプラクティス。

### アプリケーションセキュリティ

#### フラットPromiseチェーンを使用

コールバック地獄を避け、Promise チェーンまたはasync/awaitを使用してエラーハンドリングを改善：

```javascript
// コールバック地獄を避ける
func1("input1")
   .then(function (result){
      return func2("input2");
   })
   .then(function (result){
      return func3("input3");
   })
   .then(function (result){
      return func4("input4");
   })
   .catch(function (error) {
      // error operations
   });
```

async/awaitを使用：
```javascript
(async() => {
  try {
    let res1 = await func1("input1");
    let res2 = await func2("input2");
    let res3 = await func3("input2");
    let res4 = await func4("input2");
  } catch(err) {
    // error operations
  }
})();
```

#### リクエストサイズ制限を設定

リクエストボディサイズを制限してリソース枯渇を防止：

```javascript
app.use(express.urlencoded({ extended: true, limit: "1kb" }));
app.use(express.json({ limit: "1kb" }));
```

raw-bodyを使用したカスタム制限の場合：
```JavaScript
const contentType = require('content-type')
const express = require('express')
const getRawBody = require('raw-body')

const app = express()

app.use(function (req, res, next) {
  if (!['POST', 'PUT', 'DELETE'].includes(req.method)) {
    next()
    return
  }

  getRawBody(req, {
    length: req.headers['content-length'],
    limit: '1kb',
    encoding: contentType.parse(req).parameters.charset
  }, function (err, string) {
    if (err) return next(err)
    req.text = string
    next()
  })
})
```

#### 入力検証を実行

インジェクション攻撃を防ぐために許可リストを使用しすべての入力をサニタイズ。入力検証にはvalidatorやexpress-mongo-sanitizeなどのモジュールを検討。

#### 出力エスケープを実行

XSS攻撃を防ぐためにescape-htmlやnode-esapiなどのライブラリを使用してすべてのHTMLとJavaScriptコンテンツをエスケープ。

#### イベントループの健全性をモニタリング

サーバーが過負荷状態になったときを検出するためにモニタリングを使用：

```javascript
const toobusy = require('toobusy-js');
app.use(function(req, res, next) {
    if (toobusy()) {
        res.status(503).send("Server Too Busy");
    } else {
    next();
    }
});
```

#### ブルートフォース攻撃を防止

認証エンドポイントのためにレート制限と遅延を実装：

```javascript
const bouncer = require('express-bouncer');
bouncer.blocked = function (req, res, next, remaining) {
    res.status(429).send("Too many requests have been made. Please wait " + remaining/1000 + " seconds.");
};
app.post("/login", bouncer.block, function(req, res) {
    if (LoginFailed){  }
    else {
        bouncer.reset( req );
    }
});
```

#### アンチCSRF保護を使用

クロスサイトリクエストフォージェリに対して状態変更リクエストを保護。注意：csurfパッケージは非推奨、代替のCSRF保護パッケージを使用。

#### HTTPパラメータ汚染を防止

同じ名前を持つ複数のパラメータを処理するためにhppモジュールを使用：

```javascript
const hpp = require('hpp');
app.use(hpp());
```

#### 必要なデータのみを返す

必要なフィールドのみを返すことでデータ露出を制限：

```javascript
exports.sanitizeUser = function(user) {
  return {
    id: user.id,
    username: user.username,
    fullName: user.fullName
  };
};
```

### エラーと例外処理

#### キャッチされない例外を処理

シャットダウン前にリソースをクリーンアップするためにuncaughtExceptionイベントにバインド：

```javascript
process.on("uncaughtException", function(err) {
    // clean up allocated resources
    // log necessary error details to log files
    process.exit(); // exit the process to avoid unknown state
});
```

#### EventEmitterエラーを処理

EventEmitterオブジェクトを使用する際は常にerrorイベントをリッスン：

```javascript
const events = require('events');
const emitter = new myEventEmitter();
emitter.on('error', function(err){
    //Perform necessary error handling here
});
```

### サーバーセキュリティ

#### 安全なCookieフラグを設定

適切なセキュリティフラグでCookieを設定：

```javascript
const session = require('express-session');
app.use(session({
    secret: 'your-secret-key',
    name: 'cookieName',
    cookie: { secure: true, httpOnly: true, path: '/user', sameSite: true}
}));
```

#### セキュリティヘッダーを使用

helmetを使用してセキュリティヘッダーを実装：

```javascript
const helmet = require("helmet");
app.use(helmet()); // Add various HTTP headers
```

主要なヘッダーには以下が含まれます：
- HSTS: `app.use(helmet.hsts());`
- フレーム保護: `app.use(helmet.frameguard());`
- XSS保護: `app.use(helmet.xssFilter());`
- コンテンツセキュリティポリシー: `app.use(helmet.contentSecurityPolicy({...}));`
- コンテンツタイプ保護: `app.use(helmet.noSniff());`
- Powered By隠蔽: `app.use(helmet.hidePoweredBy());`

### プラットフォームセキュリティ

#### パッケージを最新に保つ

依存関係を定期的に監査・更新：

```bash
npm audit
npm audit fix
```

脆弱なパッケージを識別するためにOWASP Dependency-CheckやRetire.jsなどのツールを使用。

#### 危険な関数を避ける

潜在的に危険な関数には注意を払う：
- ユーザー入力で`eval()`を避ける（リモートコード実行リスク）
- `child_process.exec`に注意（コマンドインジェクションリスク）
- `fs`モジュール使用時は入力をサニタイズ（ディレクトリトラバーサルリスク）
- `vm`モジュールは適切なサンドボックス内で使用

#### ReDoS攻撃を防止

vuln-regex-detectorなどのツールを使用してサービス拒否脆弱性の正規表現をテスト。

#### セキュリティリンターを使用

開発ワークフローにセキュリティ重視ルールを持つESLintやJSHintなどの静的分析ツールを実装。

#### 厳格モードを有効化

一般的なJavaScriptエラーをキャッチするために常に厳格モードを使用：

```javascript
"use strict";

func();
function func() {
  y = 3.14;   // This will cause an error (y is not defined)
}
```

### アプリケーションアクティビティロギング

セキュリティモニタリングのために包括的なロギングを実装：

```javascript
const logger = new (Winston.Logger) ({
    transports: [
        new (winston.transports.Console)(),
        new (winston.transports.File)({ filename: 'application.log' })
    ],
    level: 'verbose'
});
```

これらのプラクティスに従うことで、Node.jsアプリケーションのセキュリティ姿勢を大幅に改善し、一般的なWebアプリケーション脆弱性から保護できます。
