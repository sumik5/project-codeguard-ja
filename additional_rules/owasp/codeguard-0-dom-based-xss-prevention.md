---
description: DOMベースXSS防止のベストプラクティス
languages:
- c
- html
- javascript
- php
- typescript
- vlang
alwaysApply: false
---

## DOMベースXSS防止セキュリティルール

**ルール適用：** このルールは、ユーザー制御可能なソースからの信頼できないデータが、適切なエンコーディングやサニタイゼーションなしにDOMシンクに挿入されることで発生するDOMベースXSS脆弱性を防ぎます。

## ルール1：コンテキスト別のDOMシンク制限

**DOMシンクを保護する必要があります**。リスクレベルに基づいて：

### 高リスクHTMLシンク

```javascript
// 違反：HTMLシンクへの直接代入
element.innerHTML = userInput;           // 危険
element.outerHTML = userInput;           // 危険
document.write(userInput);               // 危険

// 必須：安全な代替を使用
element.textContent = userInput;         // 安全
element.innerHTML = DOMPurify.sanitize(userInput); // 安全
```

### 重大なJavaScript実行シンク

```javascript
// 違反：コード実行シンク
eval(userInput);                         // 重大な脆弱性
new Function(userInput);                 // 重大な脆弱性
setTimeout(userInput, 100);              // 重大な脆弱性

// 必須：安全な代替
setTimeout(() => processData(userInput), 100);  // 安全
JSON.parse(userInput);                   // JSONには安全
```

### 中リスクURL/イベントシンク

```javascript
// 違反：未検証の代入
location.href = userInput;               // 危険
element.onclick = userInput;             // 危険

// 必須：検証し、安全なパターンを使用
if (/^https?:\/\/trusted-domain\.com/.test(userInput)) {
  location.href = encodeURI(userInput);
}
element.addEventListener('click', () => handleClick(userInput));
```

## ルール2：必須のCSPとTrusted Types

**厳格なCSPを実装する必要があります：**

```http
Content-Security-Policy:
  script-src 'self' 'nonce-{random}';
  object-src 'none';
  base-uri 'self';
  require-trusted-types-for 'script';
```

**Trusted Typesを使用する必要があります：**

```javascript
const policy = trustedTypes.createPolicy('dom-xss-prevention', {
  createHTML: (string) => DOMPurify.sanitize(string, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
    ALLOWED_ATTR: []
  })
});
element.innerHTML = policy.createHTML(userInput);
```

## ルール3：サーバーサイド検証要件

**すべてのユーザー入力をサーバーサイドで検証する必要があります：**

```javascript
function validateInput(input, context) {
  if (input.length > 1000) throw new Error('入力が長すぎます');

  const patterns = {
    html: /<script|javascript:|on\w+\s*=/i,
    url: /^https?:\/\/[a-zA-Z0-9.-]+/,
    text: /<[^>]*>/g
  };

  if (patterns[context] && patterns[context].test(input)) {
    throw new Error('無効な入力が検出されました');
  }
  return input;
}
```

## ルール4：コンテキストを意識したエンコーディング

**コンテキストに応じた適切なエンコーディングを適用する必要があります：**

```javascript
// HTMLコンテキスト
function encodeHTML(str) {
  return str.replace(/[&<>"'\/]/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '/': '&#x2F;'
  })[char]);
}

// JavaScriptコンテキスト
function encodeJS(str) {
  return str.replace(/[\\'"<>/\n\r\t]/g, char => ({
    '\\': '\\\\', "'": "\\'", '"': '\\"', '<': '\\u003C',
    '>': '\\u003E', '/': '\\u002F', '\n': '\\n', '\r': '\\r', '\t': '\\t'
  })[char]);
}

// URLコンテキスト
function encodeURL(str) {
  return encodeURIComponent(str).replace(/['"<>]/g, char =>
    '%' + char.charCodeAt(0).toString(16).toUpperCase());
}
```

## ルール5：安全なDOM API使用

**安全なDOM構築を使用する必要があります：**

```javascript
function createSafeElement(tagName, textContent, attributes = {}) {
  const element = document.createElement(tagName);
  if (textContent) element.textContent = textContent;

  const safeAttrs = ['class', 'id', 'title', 'alt', 'src', 'href', 'role'];
  for (const [key, value] of Object.entries(attributes)) {
    if (safeAttrs.includes(key.toLowerCase())) {
      element.setAttribute(key, value);
    }
  }
  return element;
}
```

## ルール6：ソース検証

**信頼できないデータソースを検証する必要があります：**

### URLパラメータとPostMessage

```javascript
// URLパラメータ検証
function getURLParam(name) {
  const value = new URLSearchParams(location.search).get(name);
  if (!value || value.length > 100 || /<script|javascript:/i.test(value)) {
    throw new Error('無効なパラメータ');
  }
  return value;
}

// PostMessage検証
window.addEventListener('message', (event) => {
  const allowedOrigins = ['https://trusted-domain.com'];
  if (!allowedOrigins.includes(event.origin)) return;
  processMessage(event.data);
});
```

## ルール7：フレームワーク統合

**フレームワーク固有の安全なパターン：**

```javascript
// React：安全なHTMLレンダリング
function SafeComponent({ htmlContent }) {
  const clean = DOMPurify.sanitize(htmlContent, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br']
  });
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}

// Vue：安全なディレクティブ
Vue.directive('safe-html', {
  update: (el, binding) => {
    el.innerHTML = DOMPurify.sanitize(binding.value, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br']
    });
  }
});
```

## 違反検出パターン

**これらのパターンはセキュリティ違反をトリガーします：**

```javascript
// 違反：直接的なDOM操作
element.innerHTML = userInput;
eval(userData);
setTimeout(userData, 100);
location.href = userUrl;
element.onclick = userHandler;

// 違反：エスケープされていないテンプレートリテラル
const html = `<div>${userInput}</div>`;

// 違反：検証の欠如
window.addEventListener('message', (e) => processMessage(e.data));
```

## 必須コンプライアンスチェック


✅ **DOMPurifyがインポートされ、HTML挿入に使用されている**
✅ **サニタイゼーションなしのinnerHTML/outerHTMLが使用されていない**
✅ **eval()、new Function()、文字列を伴うsetTimeout/setIntervalが使用されていない**
✅ **script-src 'self'を含むCSPが実装されている**
✅ **Trusted Typesポリシーが実装されている**
✅ **location代入前のURL検証**
✅ **postMessageのオリジン検証**

**違反の結果：** DOMベースXSS脆弱性は、任意のJavaScript実行を許可し、アカウント侵害、データ窃取、悪意のあるユーザー操作につながります。

**テストペイロード：** コードは以下を安全に処理する必要があります：
- `<script>alert('XSS')</script>`
- `javascript:alert('XSS')`
- `"><script>alert('XSS')</script>`
- `'; eval('alert(1)'); //`
