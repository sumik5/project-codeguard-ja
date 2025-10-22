---
description: クロスサイトスクリプティング（XSS）防止のベストプラクティス
languages:
- c
- html
- javascript
- php
- typescript
- vlang
alwaysApply: false
---

## はじめに

このチートシートは、開発者がXSS脆弱性を防ぐのに役立ちます。

クロスサイトスクリプティング（XSS）攻撃は深刻であり、アカウントなりすまし、ユーザー行動の観察、外部コンテンツの読み込み、機密データの窃取など、さまざまな被害をもたらします。XSSは、攻撃者が悪意のあるコンテンツをWebページに注入し、ユーザーのブラウザで実行される時に発生します。

**このチートシートには、XSSを防止または影響を制限する技術が含まれています。単一の技術だけではXSSを解決できないため、XSSを防止するには適切な防御技術の組み合わせが必要です。**

## クロスサイトスクリプティング（XSS）脆弱性の防止

### 核心防御戦略

#### 1. コンテキストを意識した出力エンコーディング

XSSに対する最も重要な防御は、データが挿入されるコンテキストに基づいた適切な出力エンコーディングです：

* **HTMLボディコンテキスト：** `innerHTML`の代わりに`element.textContent`を使用、またはリッチコンテンツにはDOMPurifyでサニタイズ
* **HTML属性コンテキスト：** 常に属性を引用符で囲み、値をHTMLエンコード：`<div data-user="{{encodedInput}}">`
* **JavaScriptコンテキスト：** 動的なJavaScript生成を避け、代わりにdata属性とイベントリスナーを使用
* **CSSコンテキスト：** 注入前に厳格な許可リストでCSS値を検証
* **URLコンテキスト：** URLをエンコードし、`javascript:` URLを防ぐためプロトコルを検証

* **ARIA属性とSVGコンテキスト：** 許可リストでARIA値を検証；DOMPurify SVGプロファイルでSVGをサニタイズ
* **JavaScriptイベントハンドラー：** `onclick`属性にユーザーデータを決して注入しない；代わりに`addEventListener()`を使用

#### 2. フレームワーク保護の活用

モダンフレームワークは組み込みのXSS保護を提供します：

* **React：** JSX内の値を自動エスケープしますが、`dangerouslySetInnerHTML`には注意
* **Angular：** コンテキストに応じた自動エスケープを使用しますが、`[innerHTML]`バインディングには注意
* **Vue：** マスタッシュ補間を自動エスケープしますが、`v-html`には注意

`dangerouslySetInnerHTML`、`[innerHTML]`、`v-html`のようなエスケープハッチを使用する際は、必ず最初にDOMPurifyでサニタイズしてください。

#### 3. サーバーサイド入力検証とサニタイゼーション

* **サーバーサイド検証は必須：** すべての入力検証はサーバーで行う必要があります。クライアントサイド検証はユーザー体験のためだけです。
* **許可リストで検証：** 期待される入力タイプ（メール、ユーザー名など）に対して、長さ制限付きの厳格な正規表現パターンを使用。
* **信頼できるライブラリでHTMLサニタイゼーション：** 厳格な設定で[DOMPurify](https://github.com/cure53/DOMPurify)を使用：
  ```javascript
  const cleanHtml = DOMPurify.sanitize(userHtml, {
    ALLOWED_TAGS: ['b', 'i', 'p', 'a', 'ul', 'li'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
    ALLOW_DATA_ATTR: false
  });
  ```

#### 4. 多層防御コントロール

* **Content Security Policy（CSP）：** 追加保護として厳格なCSPヘッダーを実装：
  ```http
  Content-Security-Policy: default-src 'self';
    script-src 'self' 'nonce-{random}';
    style-src 'self' 'unsafe-inline';
    object-src 'none';
    base-uri 'self';
    require-trusted-types-for 'script';
  ```

* **Trusted Types API：** DOM XSSを防ぐためTrusted Typesを使用：
  ```javascript
  // Trusted Typesポリシーを定義
  const policy = trustedTypes.createPolicy('myPolicy', {
    createHTML: (string) => DOMPurify.sanitize(string),
    createScript: () => { throw new Error('スクリプト作成は許可されていません'); }
  });

  // Trusted Typesで使用
  element.innerHTML = policy.createHTML(userInput);
  ```

* **安全なDOM API：** 常に安全なDOM操作メソッドを優先：
  ```javascript
  // 安全なアプローチ
  element.textContent = userInput;          // テキストには常に安全
  element.setAttribute('data-user', userInput); // ほとんどの属性に安全
  element.classList.add(validatedClassName);     // CSSクラスに安全
  ```

* **安全なCookie設定：** Cookie盗難を防止：
  ```http
  Set-Cookie: sessionId=abc123; HttpOnly; Secure; SameSite=Strict
  ```

#### 5. 避けるべき一般的な落とし穴

* **どのデータソースも信頼しない：** 内部APIやデータベースでさえ悪意のあるデータを含む可能性があります。
* **間接的な入力に注意：** ユーザーデータはURL、フォームフィールド、HTTPヘッダー、JSON/XMLペイロードを通じてアプリケーションに入る可能性があります。
* **クライアントサイドのサニタイゼーションのみに依存しない：** 常にサーバーで再検証とサニタイズを行ってください。
* **依存関係を最新に保つ：** セキュリティパッチの恩恵を受けるため、フレームワークとライブラリを定期的に更新してください。

これらのコンテキスト固有のエンコーディング戦略と多層防御アプローチを適用することで、Webアプリケーションにおけるxss脆弱性のリスクを大幅に軽減できます。
