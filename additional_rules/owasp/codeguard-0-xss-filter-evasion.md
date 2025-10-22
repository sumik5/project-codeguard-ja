---
description: クロスサイトスクリプティング（XSS）フィルタ回避防止 - 攻撃者が入力フィルタリングとブラックリストを回避するために使用する高度な技術
languages:
- c
- javascript
- typescript
alwaysApply: false
---

入力フィルタリングやブラックリストのみに依存することは不十分です。なぜなら、攻撃者はこれらの防御を回避するために多数の技術を使用するためです:

- 混合エンコーディングスキーム: HTML、URL、およびUnicodeエンコーディングの組み合わせ
- 空白文字の操作: タブ、改行、その他の空白文字を使用してパーサーを混乱させる
- 不正なタグ: レンダリング時にブラウザが「修正」する意図的に壊れたHTMLを作成する
- 難読化: `String.fromCharCode()`のようなJavaScriptエンコーディング関数を使用して悪意のあるコードを隠す

### コンテキストに応じた出力エンコーディング

最も効果的な防御は、データが使用される場所に基づいて適切なエンコーディングを適用することです:

#### HTMLコンテキスト（タグ間のコンテンツ）

```javascript
// 脆弱な実装
const userName = request.getParameter("user");
document.getElementById("welcome").innerHTML = "Hello, " + userName;

// 安全な実装
import { encodeForHTML } from 'your-encoding-library';
const userName = request.getParameter("user");
document.getElementById("welcome").innerHTML = "Hello, " + encodeForHTML(userName);
```

#### HTML属性コンテキスト

```javascript
// 脆弱な実装
const userColor = request.getParameter("color");
document.getElementById("profile").innerHTML =
  `<div class="profile" style="background-color:${userColor}">Profile</div>`;

// 安全な実装
import { encodeForHTMLAttribute } from 'your-encoding-library';
const userColor = request.getParameter("color");
document.getElementById("profile").innerHTML =
  `<div class="profile" style="background-color:${encodeForHTMLAttribute(userColor)}">Profile</div>`;
```

#### JavaScriptコンテキスト

```javascript
// 脆弱な実装
const userInput = request.getParameter("input");
const script = document.createElement("script");
script.textContent = `const userValue = "${userInput}";`;

// 安全な実装
import { encodeForJavaScript } from 'your-encoding-library';
const userInput = request.getParameter("input");
const script = document.createElement("script");
script.textContent = `const userValue = "${encodeForJavaScript(userInput)}";`;
```

#### URLコンテキスト

```javascript
// 脆弱な実装
const redirectUrl = request.getParameter("url");
location.href = redirectUrl;

// 安全な実装
import { encodeForURL } from 'your-encoding-library';
const redirectUrl = request.getParameter("url");
// まずURLパターンを検証
if (isValidRedirectURL(redirectUrl)) {
  location.href = encodeForURL(redirectUrl);
}
```

#### CSSコンテキスト

```javascript
// 脆弱な実装
const userTheme = request.getParameter("theme");
document.getElementById("custom").style = userTheme;

// 安全な実装
import { encodeForCSS } from 'your-encoding-library';
const userTheme = request.getParameter("theme");
document.getElementById("custom").style = encodeForCSS(userTheme);
```

### 確立されたサニタイゼーションライブラリの使用

独自のサニタイゼーションロジックを作成することは避けてください。代わりに、十分にメンテナンスされたライブラリを使用してください:

#### JavaScript/DOM

```javascript
// DOMPurifyの使用
import DOMPurify from 'dompurify';

function displayUserContent(content) {
  // 特定のタグと属性のみを許可するようにDOMPurifyを設定
  const config = {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'target']
  };

  const sanitized = DOMPurify.sanitize(content, config);
  document.getElementById('user-content').innerHTML = sanitized;
}
```

#### Java

```java
// OWASP Java Encoderの使用
import org.owasp.encoder.Encode;

@Controller
public class UserController {
    @GetMapping("/profile")
    public String showProfile(Model model, @RequestParam String username) {
        model.addAttribute("encodedUsername", Encode.forHtml(username));
        return "profile";
    }
}

// テンプレート内（例：Thymeleaf）
// <div th:text="${encodedUsername}">Username</div>
```

#### PHP

```php
// HTMLPurifierの使用
require_once 'HTMLPurifier.auto.php';

$config = HTMLPurifier_Config::createDefault();
$purifier = new HTMLPurifier($config);

$userBio = $_POST['bio'];
$cleanBio = $purifier->purify($userBio);

echo '<div class="bio">' . $cleanBio . '</div>';
```

### 危険なパターンの回避

特定のコーディングパターンはクロスサイトスクリプティング（XSS）攻撃に対して特に脆弱です:

#### 安全でないJavaScript APIの回避

```javascript
// 危険 - ユーザー入力で絶対に実行しないでください
eval(userInput);
document.write(userInput);
new Function(userInput);
setTimeout(userInput, 100);
setInterval(userInput, 100);
element.innerHTML = userInput;

// より安全な代替案
// evalの代わりに、JSONを安全に解析
const data = JSON.parse(userInput);

// innerHTMLの代わりに、textContentを使用
element.textContent = userInput;

// または要素を適切に作成
const div = document.createElement('div');
div.textContent = userInput;
parentElement.appendChild(div);
```

#### インラインスクリプトとイベントハンドラの回避

```html
<!-- 危険 - インラインイベントハンドラはXSSに対して脆弱 -->
<button onclick="doSomething('<?php echo $userInput; ?>')">Click me</button>

<!-- より安全 - 代わりにaddEventListenerを使用 -->
<button id="safeButton">Click me</button>
<script>
  document.getElementById('safeButton').addEventListener('click', function() {
    doSomething(sanitizedUserInput);
  });
</script>
```

### 多層防御戦略

複数の保護レイヤーを実装してください:

#### コンテンツセキュリティポリシー（CSP）

```http
# インラインスクリプトをブロックし、ソースを制限する強力なCSPヘッダー
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; style-src 'self'; img-src 'self' data:;
```

```javascript
// Express.jsでのCSP設定
const helmet = require('helmet');
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", 'trusted-cdn.com'],
    objectSrc: ["'none'"],
    styleSrc: ["'self'"],
    imgSrc: ["'self'", 'data:']
  }
}));
```

#### 安全なCookie設定

```http
Set-Cookie: sessionId=abc123; HttpOnly; Secure; SameSite=Strict
```

#### 入力検証

```javascript
// 処理前に入力形式を検証
function validateUsername(username) {
  // 英数字と限定された記号のみを許可
  const usernameRegex = /^[a-zA-Z0-9_.-]{3,30}$/;
  if (!usernameRegex.test(username)) {
    throw new Error('Invalid username format');
  }
  return username;
}
```
