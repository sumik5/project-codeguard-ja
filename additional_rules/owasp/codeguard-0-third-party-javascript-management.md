---
description: サードパーティJavaScript管理のセキュリティ
languages:
- c
- javascript
- typescript
alwaysApply: false
---

## サードパーティJavaScript管理のセキュリティ

任意のコード実行、データ漏洩、アプリケーション制御の喪失を防ぐため、サードパーティJavaScriptタグをセキュアにします。

### 主要なリスク

サードパーティJavaScriptには3つの重大なリスクがあります：
1. クライアントアプリケーション変更の制御喪失
2. クライアントシステムでの任意のコード実行
3. サードパーティへの機密情報の開示

### セキュリティ戦略

#### サーバーダイレクトデータレイヤー（推奨）
サードパーティスクリプトが直接DOMアクセスする代わりにアクセスできる、制御されたデータレイヤーを作成します。

主要な原則：
- ファーストパーティコードのみがデータレイヤーを設定
- サードパーティスクリプトはサニタイズされたデータレイヤーから排他的に読み取り
- タグJavaScriptはホストデータレイヤー値のみにアクセス可能で、URLパラメータにはアクセス不可

利点：
- ユーザーのブラウザで実行されるのは自社のJavaScriptのみ
- ベンダーに送信されるのは検証済みデータのみ
- 複数のベンダータグを持つ大規模サイトにスケーラブル

#### サブリソース整合性（SRI）
整合性メタデータを追加して、レビュー済みコードのみが実行されることを保証します。

```html
<script src="https://analytics.vendor.com/v1.1/script.js"
   integrity="sha384-MBO5IDfYaE6c6Aao94oZrIOiC7CGiSNE64QUbHNPhzk8Xhm0djE6QqTpL0HzTUxk"
   crossorigin="anonymous">
</script>
```

要件：
- ベンダーホストでCORSが有効化されている必要がある
- ベンダーJavaScriptの変更を定期的に監視
- ベンダーがスクリプトを更新した場合は整合性ハッシュを更新

#### iframeによるサンドボックス化
ベンダーJavaScriptを分離して、直接DOMおよびCookieアクセスを防止します。

```html
<!-- Host page with sandboxed iframe -->
<html>
   <head></head>
     <body>
       ...
       <iframe
       src="https://somehost-static.net/analytics.html"
       sandbox="allow-same-origin allow-scripts">
       </iframe>
   </body>
</html>

<!-- somehost-static.net/analytics.html -->
<html>
   <head></head>
     <body>
       ...
       <script>
       window.addEventListener("message", receiveMessage, false);
       function receiveMessage(event) {
         if (event.origin !== "https://somehost.com:443") {
           return;
         } else {
         // Make some DOM here and initialize other
        //data required for 3rd party code
         }
       }
       </script>
       <!-- 3rd party vendor javascript -->
       <script src="https://analytics.vendor.com/v1.1/script.js"></script>
       <!-- /3rd party vendor javascript -->
   </body>
 </html>
```

通信要件：
- セキュアなデータ交換にpostMessageメカニズムを使用
- メッセージを処理する前にイベント送信元を検証
- 追加保護のためにコンテンツセキュリティポリシー（CSP）を検討

#### コンテンツサニタイゼーション
サードパーティに送信する前に以下を使用してDOMデータをクリーニング：
- DOMPurify: HTML、MathML、SVG用のXSSサニタイザー
- MentalJS: JavaScriptパーサーとサンドボックス

#### タグマネージャー制御
タグ管理システムの場合：
- JavaScriptアクセスをデータレイヤー値のみに制限
- 可能な場合はカスタムHTMLタグとJavaScriptコードを無効化
- タグマネージャーのセキュリティプラクティスとアクセス制御を検証
- タグ設定に二要素認証を実装

### 運用セキュリティ

#### ライブラリを最新に保つ
- 脆弱性に対処するため、JavaScriptライブラリを定期的に更新
- RetireJSなどのツールを使用して脆弱なライブラリを特定

#### ベンダー契約
契約による制御：
- セキュアコーディングプラクティスとコード整合性監視の証拠を要求
- 悪意のあるJavaScriptを提供した場合のペナルティを含める
- ソースコード監視と変更検出を義務付ける

#### 完全な防止戦略
最も効果的な制御：
1. マーケティングサーバーへのAPI呼び出しを含むデータレイヤーアーキテクチャ
2. サブリソース整合性の実装
3. 仮想フレーム封じ込めの展開

### 実装ガイドライン

1. アナリティクスタグ用にサーバーダイレクトデータレイヤーアーキテクチャを実装
2. すべての外部スクリプトリクエストにサブリソース整合性を使用
3. 高リスクなサードパーティスクリプトにiframeサンドボックス化を展開
4. タグペイロードに含める前にすべての動的データをサニタイズ
5. 更新されたJavaScriptライブラリを維持し、脆弱性を監視
6. セキュリティ要件を含むベンダー契約を確立
7. サードパーティスクリプトの変更を定期的に監査および監視
