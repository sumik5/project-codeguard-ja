---
description: クリックジャッキング防御のベストプラクティス
languages:
- c
- html
- javascript
- php
- typescript
alwaysApply: false
---

## クリックジャッキングからWebアプリケーションを保護

クリックジャッキング（UI詐称攻撃）は、インタラクティブ要素を隠したり偽装したりすることで、ユーザーに意図しない操作を実行させます。これらの攻撃は、サイトを見えないiframeに埋め込むことで、攻撃者のサイト向けのクリックを捕捉し、アプリケーションにリダイレクトします。

### 防御戦略：多層防御

#### 1. HTTPヘッダー：第一の防御線

**Content Security Policy（CSP）**は、モダンブラウザでX-Frame-Optionsに代わる推奨アプローチです：

```http
Content-Security-Policy: frame-ancestors 'none';
```

このディレクティブは、あらゆるサイトがコンテンツをフレーム化することを防ぎます。特定のサイトにフレーム化を許可する必要がある場合は、以下を使用します：

```http
Content-Security-Policy: frame-ancestors 'self' https://trusted-site.com;
```

**重要：** CSP frame-ancestorsは、両方が存在する場合X-Frame-Optionsより優先されます。CSPをサポートしない古いブラウザ向けに、フォールバックとして**X-Frame-Options**ヘッダーを実装してください：

```http
X-Frame-Options: DENY
```

または

```http
X-Frame-Options: SAMEORIGIN
```

**重要：** `X-Frame-Options: ALLOW-FROM`は廃止され、モダンブラウザでサポートされていないため、決して使用しないでください。

#### 2. Cookie保護

セッションCookieをクロスオリジンリクエストに含めないよう保護します：

```http
Set-Cookie: sessionid=abc123; SameSite=Lax; Secure; HttpOnly
```

SameSite属性のオプション：
- `Strict`: ファーストパーティコンテキストでのみCookieを送信（最も安全）
- `Lax`: 他サイトからの遷移時にCookieを送信（バランスが良い）

#### 3. JavaScript フレームバスター

レガシーブラウザ向け、または追加の防御層として、ページの`<head>`セクションにこの防御コードを実装します：

```html
<style id="antiClickjack">body{display:none !important;}</style>
<script type="text/javascript">
  if (self === top) {
    // フレーム化されていない場合、コンテンツを隠すスタイルを削除
    var antiClickjack = document.getElementById("antiClickjack");
    antiClickjack.parentNode.removeChild(antiClickjack);
  } else {
    // フレーム化されている場合、フレームから抜け出す
    top.location = self.location;
  }
</script>
```

このアプローチは、まずページコンテンツを非表示にし、ページがフレーム化されていない場合のみ表示します。フレーム化されている場合、フレームから抜け出そうとします。**注意：** フレームバスターは高度な攻撃者に破られる可能性があり、唯一の防御策にすべきではありません。

#### 4. 特殊ケース：サイトがフレーム化される必要がある場合

アプリケーションが正当にフレーム化される必要がある場合（例：埋め込み用に設計されている）：

1. CSPで特定のドメインのみを許可リスト化：
   ```http
   Content-Security-Policy: frame-ancestors 'self' https://trusted-partner.com;
   ```

2. 機密操作に対する追加確認を実装：
   ```javascript
   if (sensitiveAction && window !== window.top) {
     if (!window.confirm('この操作を確認しますか？')) {
       return false; // 確認されなければ操作をキャンセル
     }
   }
   ```

### 実装のベストプラクティス

1. **グローバルに適用：** 機密ページだけでなく、すべてのページにこれらの保護を追加してください。
2. **ヘッダーインジェクションの自動化：** 各ページに手動で追加するのではなく、Webサーバー、CDN、またはアプリケーションフレームワークを設定して自動的にヘッダーを注入してください。
3. **テスト用にCSP Report-Onlyを使用：** 強制前に違反を監視するため、まず`Content-Security-Policy-Report-Only: frame-ancestors 'none';`をデプロイしてください。
4. **徹底的にテスト：** 異なるブラウザやプロキシで防御が機能することを検証してください。
5. **多層防御：** 最大限のセキュリティのため、3つの保護手法をすべて組み合わせてください。
6. **監視と検証：** OWASP ZAPスキャナーなどのツールを使用してヘッダーが適切に設定されていることを確認し、CSPレポートで違反を監視してください。

これらの防御を実装することで、Webアプリケーションに対するクリックジャッキング攻撃のリスクを大幅に軽減できます。