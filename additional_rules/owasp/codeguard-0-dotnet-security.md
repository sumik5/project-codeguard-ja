---
description: .NETセキュリティベストプラクティス
languages:
- c
- javascript
- xml
alwaysApply: false
---

## .NETセキュリティガイドライン

このルールは、一般的なWeb脆弱性を防ぐための重要な.NETセキュリティプラクティスを示します。

- 一般的なセキュリティ設定
  - .NET Framework、.NET Core、すべてのNuGetパッケージを最新に保ちます。
  - CI/CDパイプラインでSoftware Composition Analysis（SCA）ツールを使用します。
  - GitHub上の.NET CoreとASP.NET Coreセキュリティアナウンスを購読します。

- アクセス制御と認可
  - すべての外部向けエンドポイントにコントローラーまたはメソッドレベルで`[Authorize]`属性を使用します。
  - リソースアクセス前に常にサーバー側でユーザー権限を検証します。
  - 必要に応じてコードで`User.Identity.IsInRole`を使用してロールをチェックします。
  - IDOR攻撃を防ぐため、適切な直接オブジェクト参照検証を実装します。

- 認証とセッション管理
  - セキュアなパスワードポリシーとアカウントロックアウトを伴うASP.NET Core Identityを使用します。
  - 本番環境では`HttpOnly = true`と`requireSSL = true`でCookieを設定します。
  - セッションタイムアウトを短縮し、スライディング有効期限を無効にしてセキュリティを向上させます。
  - ブルートフォース攻撃に対してログイン、登録、パスワードリセットメソッドをスロットリングします。

- 暗号化セキュリティ
  - カスタム暗号化関数を記述せず、.NETの実証された実装を使用します。
  - 強力なハッシュアルゴリズムを使用：一般的なハッシュにはSHA512、パスワードにはPBKDF2。
  - 適切なキー管理を伴う暗号化にはAES-GCMを使用します。
  - セキュアなローカルストレージにはWindows Data Protection API（DPAPI）を使用します。
  - すべてのネットワーク通信にTLS 1.2+を強制します。

- インジェクション防止
  - パラメータ化SQLクエリまたはEntity Frameworkを排他的に使用します。
  - ユーザー入力をSQLコマンドまたはOSコマンドに連結しません。
  - `IPAddress.TryParse`などのメソッドを使用してすべてのユーザー入力に許可リスト検証を使用します。
  - 必要に応じてバックスラッシュでLDAP特殊文字をエスケープします。

- セキュリティ設定ミス
  - web.config変換を使用して本番環境でデバッグとトレースを無効化します。
  - `app.UseHttpsRedirection()`またはGlobal.asaxを使用してHTTPSリダイレクトを強制します。
  - サーバーバージョンヘッダーを削除し、セキュアなHTTPヘッダーを実装します。
  - デフォルトのパスワードまたは資格情報を使用しません。

- CSRF保護
  - フォームで`@Html.AntiForgeryToken()`を使用してアンチフォージェリトークンを使用します。
  - POST/PUTアクションで`[ValidateAntiForgeryToken]`を使用してトークンを検証します。
  - Web FormsのCSRF保護のため`ViewStateUserKey = Session.SessionID`を設定します。
  - ログアウト時にアンチフォージェリCookieを削除します。

- セキュアヘッダー設定
  - `X-Frame-Options`、`X-Content-Type-Options`、`Content-Security-Policy`ヘッダーを設定します。
  - `Strict-Transport-Security`ヘッダーでHSTSを設定します。
  - `X-Powered-By`とバージョン開示ヘッダーを削除します。

- ロギングと監視
  - ユーザーコンテキストを伴う認証失敗、アクセス制御違反をログに記録します。
  - 集中ロギングのためILoggerフレームワークを使用します。
  - パスワードやトークンなどの機密データをログに記録しません。
  - セキュリティログにスタックトレースとエラーコンテキストを含めます。

- シリアライゼーションセキュリティ
  - 信頼できないデータには危険な`BinaryFormatter`を避けます。
  - `System.Text.Json`、`XmlSerializer`、または`DataContractSerializer`を安全に使用します。
  - 検証なしに信頼できないデータをデシリアライズしません。
  - シリアライズされたオブジェクトのデジタル署名検証を実装します。

CSRF保護の例（OWASPから）：

```csharp
protected override OnInit(EventArgs e) {
    base.OnInit(e);
    ViewStateUserKey = Session.SessionID;
}
```

セキュアヘッダー設定（OWASPから）：

```xml
<system.webServer>
  <httpProtocol>
    <customHeaders>
      <add name="Content-Security-Policy"
         value="default-src 'none'; style-src 'self'; img-src 'self'; font-src 'self'" />
      <add name="X-Content-Type-Options" value="NOSNIFF" />
      <add name="X-Frame-Options" value="DENY" />
      <add name="X-Permitted-Cross-Domain-Policies" value="master-only"/>
      <add name="X-XSS-Protection" value="0"/>
      <remove name="X-Powered-By"/>
    </customHeaders>
  </httpProtocol>
</system.webServer>
```

まとめ：
適切な認可制御を実装し、セキュアな認証とセッション管理を使用し、強力な暗号化を適用し、インジェクション攻撃を防止し、セキュリティヘッダーを設定し、CSRF保護を実装し、セキュアな設定を維持し、セキュリティイベントを適切にログに記録し、シリアライゼーションを安全に処理することで.NETアプリケーションを保護します。
