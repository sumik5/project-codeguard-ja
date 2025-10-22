---
description: Content Security Policy (CSP) Best Practices
languages:
- c
- html
- javascript
- php
- typescript
alwaysApply: false
---

## Content Security Policy（CSP）：多層防御戦略

強力なContent Security Policy（CSP）の実装は、クロスサイトスクリプティング（XSS）、クリックジャッキング、その他のインジェクション攻撃を軽減する最も効果的な方法の1つです。CSPは、読み込みを許可する動的リソースを宣言することで、ブラウザが強制する許可リストを効果的に作成します。

### 実装

#### 1. HTTPヘッダー経由でCSPを配信

CSPを実装する最も効果的な方法は、HTTPレスポンスヘッダーを使用することです：

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.com;
```

新しいポリシーをテストする際は、ブロックせずに監視するレポート専用モードを使用してください：

```http
Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self';
```

**注意：** HTTPヘッダーを変更できない場合を除き、metaタグアプローチ（`<meta http-equiv="Content-Security-Policy"...>`）の使用は避けてください。保護レベルが低く、すべてのディレクティブをサポートしていません。

#### 2. Strict CSP戦略の採用

モダンなCSPベストプラクティスは、ドメイン許可リストよりもnonce（ナンス）ベースまたはハッシュベースのアプローチを推奨します：

**nonceベースアプローチ：**

```http
Content-Security-Policy: script-src 'nonce-random123' 'strict-dynamic';
```

対応するHTML：

```html
<script nonce="random123">alert('Hello');</script>
```

**重要：** 各ページロードごとに一意で暗号学的に強力なnonceを生成してください。nonceは少なくとも128ビットのエントロピーをbase64エンコードしたものであるべきです。

**サーバーサイドのnonce生成例：**

```javascript
// Node.js: crypto.randomBytes(16).toString('base64')
// Python: base64.b64encode(secrets.token_bytes(16)).decode('utf-8')
```

**ハッシュベースの代替：**
```http
Content-Security-Policy: script-src 'sha256-hashOfYourScriptContent' 'strict-dynamic';
```

#### 3. 開始のためのベースラインCSP

```http
Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'self'; form-action 'self'; object-src 'none'; base-uri 'none'; upgrade-insecure-requests;
```

このポリシーは：
- リソースを同一オリジンに制限
- インラインスタイルを許可（多くのアプリケーションで最初は必要）
- フレーム化を制御してクリックジャッキングを防止
- フォーム送信を同一オリジンに制限
- プラグインコンテンツ（Flash、Javaアプレット）をブロック
- baseタグインジェクション攻撃を防止
- HTTPリクエストを自動的にHTTPSにアップグレード（`upgrade-insecure-requests`使用時）

#### 4. CSP互換性のためのコードリファクタリング

CSP実装を容易にするため：

1. **インラインコードを外部ファイルに移動：**
   ```html
   <!-- これの代わりに -->
   <button onclick="doSomething()">

   <!-- こうする -->
   <button id="myButton">
   <script src="buttons.js"></script> <!-- イベントリスナー付き -->
   ```

2. **インラインスタイルを除去：**
   ```html
   <!-- これの代わりに -->
   <div style="color: red">

   <!-- こうする -->
   <div class="red-text">
   ```

#### 5. 知っておくべき主要なCSPディレクティブ

- **`default-src`**: 他のfetchディレクティブのフォールバック
- **`script-src`**: JavaScriptソースを制御
- **`style-src`**: CSSソースを制御 - 外部スタイルシートには`'self'`を使用、インラインスタイルが必要な場合のみ`'unsafe-inline'`を追加
- **`img-src`**: 画像ソースを制御
- **`connect-src`**: fetch、XHR、WebSocket接続を制御
- **`object-src`**: `<object>`、`<embed>`、`<applet>`要素を制御 - Flash/プラグインをブロックするには`'none'`に設定
- **`frame-ancestors`**: どのサイトがページを埋め込めるかを制御（X-Frame-Optionsの代替） - すべてのフレーム化を防ぐには`'none'`を使用
- **`form-action`**: フォームの送信先を制御
- **`upgrade-insecure-requests`**: HTTPリクエストを自動的にHTTPSにアップグレード

#### 6. 違反レポートの有効化

CSP違反を収集するレポートエンドポイントを設定：

```http
Content-Security-Policy: default-src 'self'; report-uri https://your-domain.com/csp-reports;
```

#### 7. 実装手順

1. `Content-Security-Policy-Report-Only`から開始
2. 違反レポートを分析
3. 段階的にポリシーを強化
4. 強制モードに切り替え
5. 監視を継続

CSPは多層防御手段であることを忘れないでください。適切な入力検証、出力エンコーディング、その他のセキュアコーディングプラクティスを補完するものであり、それらの代替ではありません。