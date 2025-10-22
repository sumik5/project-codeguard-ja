---
description: DOMクロバリング防止のベストプラクティス
languages:
- c
- html
- javascript
- php
- typescript
- vlang
alwaysApply: false
---

## DOMクロバリング防止セキュリティルール

**ルール適用：** このルールは、`id`または`name`属性を持つ悪意のあるHTML要素がJavaScript変数やブラウザAPIを上書きし、XSSやセキュリティバイパスにつながる可能性があるDOMクロバリング攻撃を防ぎます。

## ルール1：HTMLサニタイゼーション要件

**すべてのユーザー提供HTMLをサニタイズする必要があります**。DOMPurifyまたはSanitizer APIを使用：

```javascript
// 必須：DOMPurify設定
const clean = DOMPurify.sanitize(userInput, {
  SANITIZE_DOM: true,           // 組み込みAPIを保護
  SANITIZE_NAMED_PROPS: true,   // 必須：カスタム変数を保護
  FORBID_ATTR: ['id', 'name']   // 必須：クロバリング属性を削除
});

// 代替：Sanitizer API
const sanitizer = new Sanitizer({
  blockAttributes: [{'name': 'id', elements: '*'}, {'name': 'name', elements: '*'}]
});
element.setHTML(userInput, {sanitizer});
```

**禁止事項：**
* サニタイズされていないユーザー入力で`innerHTML`を使用
* ユーザー生成コンテンツで`id`または`name`属性を許可
* DOMPurify設定で`SANITIZE_NAMED_PROPS`を無効化

## ルール2：Content Security Policy要件

**DOMクロバリング悪用を防ぐため厳格なCSPを実装する必要があります：**

```http
Content-Security-Policy:
  script-src 'self' 'nonce-{random}';
  object-src 'none';
  base-uri 'self';
  require-trusted-types-for 'script';
```

**DOM操作にTrusted Typesを使用する必要があります：**

```javascript
const policy = trustedTypes.createPolicy('dompurify', {
  createHTML: (string) => DOMPurify.sanitize(string, {SANITIZE_NAMED_PROPS: true})
});
element.innerHTML = policy.createHTML(userInput);
```

## ルール3：変数宣言要件

**グローバル名前空間の汚染を防ぐため明示的な変数宣言を使用する必要があります：**

```javascript
"use strict";                       // すべてのJavaScriptファイルで必須
const config = { isAdmin: false };  // 必須：明示的な宣言
let userState = {};                 // 必須：ブロックスコープ変数

// 禁止：脆弱なグローバルを作成
config = { isAdmin: false };        // 違反としてフラグ付けされる
```

**禁止事項：**
* `window`または`document`オブジェクトに機密データを保存
* 宣言キーワードなしで暗黙的なグローバル変数を使用
* 代入式の左辺でユーザー入力にアクセス

## ルール4：オブジェクト検証要件

**潜在的にクロバリングされたプロパティにアクセスする前にオブジェクトタイプを検証する必要があります：**

```javascript
// 必須：使用前の型検証
function safePropertyAccess(obj, property) {
  if (obj && typeof obj === 'object' && !(obj instanceof Element)) {
    return obj[property];
  }
  throw new Error('潜在的なDOMクロバリングが検出されました');
}

// 必須：組み込みAPIの検証
if (typeof document.getElementById === 'function') {
  const element = document.getElementById('myId');
}
```

## ルール5：動的属性制限

**すべての動的HTML属性を検証する必要があります：**

```javascript
function setElementAttribute(element, name, value) {
  const forbidden = ['id', 'name', 'onclick', 'onload', 'onerror'];
  if (forbidden.includes(name.toLowerCase())) {
    throw new Error(`セキュリティ上、属性${name}は禁止されています`);
  }
  element.setAttribute(name, DOMPurify.sanitize(value, {ALLOWED_TAGS: []}));
}
```

**禁止事項：**
* ユーザー入力から`id`または`name`属性を設定
* 検証なしで動的属性代入を使用
* `data-`または`aria-`属性のサニタイゼーションをバイパス

## ルール6：フレームワークセキュリティ要件

**React/VueアプリケーションはサニタイズされたHTMLレンダリングを使用する必要があります：**

```javascript
// REACT：必須の安全なHTMLコンポーネント
function SafeHtmlComponent({ userContent }) {
  const clean = DOMPurify.sanitize(userContent, {
    SANITIZE_NAMED_PROPS: true,
    FORBID_ATTR: ['id', 'name']
  });
  return <div dangerouslySetInnerHTML={{__html: clean}} />;
}

// VUE：必須のディレクティブ
Vue.directive('safe-html', {
  update(el, binding) {
    el.innerHTML = DOMPurify.sanitize(binding.value, {
      SANITIZE_NAMED_PROPS: true,
      FORBID_ATTR: ['id', 'name']
    });
  }
});
```

## ルール7：ランタイム監視要件

**DOMクロバリング検出を実装する必要があります：**

```javascript
// 必須：ランタイム監視
function detectClobbering() {
  ['config', 'api', 'user', 'admin'].forEach(global => {
    if (window[global] instanceof Element) {
      console.error(`セキュリティ違反：${global}でDOMクロバリングが検出されました`);
      securityLogger.warn('DOM_CLOBBERING_DETECTED', { variable: global });
    }
  });
}
setInterval(detectClobbering, 5000);
```

## ルール違反検出

**以下のパターンはセキュリティ違反をトリガーします：**

```javascript
// 違反：暗黙的なグローバル作成
config = { sensitive: true };

// 違反：windowに機密データを保存
window.userRole = 'admin';

// 違反：未検証のinnerHTML使用
element.innerHTML = userInput;

// 違反：検証なしの動的プロパティアクセス
obj[userControlledProperty] = value;

// 違反：サニタイゼーションの欠如
document.body.appendChild(htmlFromUser);
```

## 必須コンプライアンスチェック

以下のチェックを実行する必要があります：

✅ **DOMPurifyがインポートされ、`SANITIZE_NAMED_PROPS: true`で設定されている**
✅ **サニタイゼーションなしの直接的な`innerHTML`使用がない**
✅ **すべてのJavaScriptファイルでStrictモードが有効**
✅ **`script-src 'self'`を含むCSPヘッダーが実装されている**
✅ **ユーザーコンテンツに`id`または`name`属性がない**
✅ **ランタイムクロバリング検出が実装されている**
✅ **プロパティアクセス前の型検証**

**非コンプライアンスの結果：** これらのルールに違反するコードは、XSS攻撃や権限昇格につながる可能性のあるDOMクロバリング脆弱性を作成します。

**テストペイロード：** `<a id=config><a id=config name=isAdmin href=true>`は適切にサニタイズまたはブロックされる必要があります。
