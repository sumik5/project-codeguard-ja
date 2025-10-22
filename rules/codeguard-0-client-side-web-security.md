---
description: クライアント側Webセキュリティ（XSS/DOM XSS、CSP、CSRF、クリックジャッキング、XS-Leaks、サードパーティJS）
languages:
- c
- html
- javascript
- php
- typescript
- vlang
alwaysApply: false
---

## クライアント側Webセキュリティ

コードインジェクション、リクエストフォージェリ、UI詐称、クロスサイトリーク、安全でないサードパーティスクリプトからブラウザクライアントを保護。レイヤード、コンテキスト対応の制御を実施。

### クロスサイトスクリプティング（XSS）防止（コンテキスト対応）
- HTMLコンテキスト：`textContent`を優先。HTMLが必要な場合は、検証済みライブラリ（例：DOMPurify）と厳格な許可リストでサニタイズ。
- 属性コンテキスト：常に属性を引用符で囲み、値をエンコード。
- JavaScriptコンテキスト：信頼できない文字列からJSを構築しない；インラインイベントハンドラを避ける；`addEventListener`を使用。
- URLコンテキスト：プロトコル/ドメインを検証してエンコード；不適切な場合は`javascript:`とdata URLをブロック。
- リダイレクト/フォワード：ユーザー入力を宛先に直接使用しない；サーバー側マッピング（ID→URL）を使用するか、信頼できるドメイン許可リストで検証。
- CSSコンテキスト：値を許可リスト化；ユーザーから生のスタイルテキストを挿入しない。

サニタイズの例：
```javascript
const clean = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['b','i','p','a','ul','li'],
  ALLOWED_ATTR: ['href','target','rel'],
  ALLOW_DATA_ATTR: false
});
```

### DOMベースXSSと危険なシンク
- 信頼できないデータを含む`innerHTML`、`outerHTML`、`document.write`を禁止。
- `eval`、`new Function`、文字列ベースの`setTimeout/Interval`を禁止。
- `location`やイベントハンドラプロパティに割り当てる前にデータを検証してエンコード。
- DOMクロバリングによるグローバル名前空間汚染を防ぐため、strictモードと明示的な変数宣言を使用。
- Trusted Typesを採用し、厳格なCSPを強制してDOMシンク悪用を防止。

Trusted Types + CSP：
```http
Content-Security-Policy: script-src 'self' 'nonce-{random}'; object-src 'none'; base-uri 'self'; require-trusted-types-for 'script'
```

### Content Security Policy（CSP）
- ドメイン許可リストよりもnonceベースまたはハッシュベースのCSPを優先。
- Report-Onlyモードで開始；違反を収集；その後強制。
- 目指すべきベースライン：`default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'self'; form-action 'self'; object-src 'none'; base-uri 'none'; upgrade-insecure-requests`。

### クロスサイトリクエストフォージェリ（CSRF）防御
- まずXSSを修正；次にCSRF防御を重ねる。
- すべての状態変更リクエストで、フレームワークネイティブのCSRF保護と同期トークンを使用。
- Cookie設定：`SameSite=Lax`または`Strict`；セッションは`Secure`と`HttpOnly`；可能な場合は`__Host-`プレフィックスを使用。
- Origin/Refererを検証；SPAトークンモデルではAPIミューテーションにカスタムヘッダーを要求。
- 状態変更にGETを使用しない；POST/PUT/DELETE/PATCHでのみトークンを検証。すべてのトークン伝送にHTTPSを強制。

### クリックジャッキング防御
- 主要：`Content-Security-Policy: frame-ancestors 'none'`または特定の許可リスト。
- レガシーブラウザ用フォールバック：`X-Frame-Options: DENY`または`SAMEORIGIN`。
- フレーム化が必要な場合、機密操作のUX確認を検討。

### クロスサイトリーク（XS-Leaks）制御
- `SameSite` Cookieを適切に使用；機密操作には`Strict`を優先。
- Fetch Metadata保護を採用し、疑わしいクロスサイトリクエストをブロック。
- ブラウジングコンテキストを分離：該当する場合はCOOP/COEPとCORP。
- キャッシングを無効化し、機密レスポンスにユーザー固有トークンを追加してキャッシュプロービングを防止。

### サードパーティJavaScript
- 最小化して分離：`sandbox`とpostMessage origin checksを持つサンドボックス化されたiframeを優先。
- 外部スクリプトにSubresource Integrity（SRI）を使用し、変更を監視。
- ファーストパーティのサニタイズされたデータレイヤーを提供；可能な場合、タグからの直接DOM アクセスを拒否。
- タグマネージャー制御とベンダー契約で管理；ライブラリを最新に保つ。

SRIの例：
```html
<script src="https://cdn.vendor.com/app.js"
  integrity="sha384-..." crossorigin="anonymous"></script>
```

### HTML5、CORS、WebSocket、ストレージ
- postMessage：常に正確なターゲットオリジンを指定；受信時に`event.origin`を検証。
- CORS：`*`を避ける；オリジンを許可リスト化；preflightを検証；認可にCORSに依存しない。
- WebSocket：`wss://`、オリジンチェック、認証、メッセージサイズ制限、安全なJSON解析を要求。
- クライアントストレージ：`localStorage`/`sessionStorage`にシークレットを保存しない；HttpOnly Cookieを優先；回避できない場合はWeb Workerで分離。
- リンク：外部`target=_blank`リンクに`rel="noopener noreferrer"`を追加。

### HTTPセキュリティヘッダー（クライアント影響）
- HSTS：あらゆる場所でHTTPSを強制。
- X-Content-Type-Options：`nosniff`。
- Referrer-PolicyとPermissions-Policy：機密シグナルと機能を制限。

### AJAXと安全なDOM API
- 動的コード実行を避ける；文字列ではなく関数コールバックを使用。
- JSONは`JSON.stringify`で構築；文字列連結は使用しない。
- 生のHTML挿入よりも、要素を作成して`textContent`/安全な属性を設定することを優先。

### 実装チェックリスト
- すべてのシンクでコンテキスト対応のエンコード/サニタイズ；ガードなしの危険なAPIなし。
- nonceとTrusted Typesを持つ厳格なCSP；違反を監視。
- すべての状態変更リクエストでCSRFトークン；安全なCookie属性。
- フレーム保護を設定；XS-Leak緩和策を有効化（Fetch Metadata、COOP/COEP/CORP）。
- サードパーティJSをSRIとサンドボックスで分離；検証済みデータレイヤーのみ。
- HTML5/CORS/WebSocket使用を強化；Webストレージにシークレットなし。
- セキュリティヘッダーを有効化して検証。

### テストプラン
- 危険なDOM/APIパターンの自動チェック。
- CSRFとクリックジャッキングのE2Eテスト；CSPレポート監視。
- XS-Leaks（フレームカウント、タイミング、キャッシュ）とオープンリダイレクト動作の手動プローブ。
