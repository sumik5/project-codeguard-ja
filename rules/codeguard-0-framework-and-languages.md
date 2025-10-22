---
description: フレームワーク・言語セキュリティガイド（Django/DRF、Laravel/Symfony/Rails、.NET、Java/JAAS、Node.js、PHP設定）
languages:
- c
- java
- javascript
- kotlin
- php
- python
- ruby
- typescript
- xml
- yaml
alwaysApply: false
---

## フレームワーク・言語ガイド

プラットフォームごとにセキュアバイデフォルトのパターンを適用します。設定を堅牢化し、組み込みの保護機能を使用し、一般的な落とし穴を避けます。

### Django
- 本番環境でDEBUGを無効化、Djangoと依存関係を最新に保ちます。
- `SecurityMiddleware`、クリックジャッキング対策ミドルウェア、MIMEスニッフィング保護を有効化します。
- HTTPS強制（`SECURE_SSL_REDIRECT`）、HSTSの設定、セキュアCookieフラグの設定（`SESSION_COOKIE_SECURE`、`CSRF_COOKIE_SECURE`）。
- CSRF：`CsrfViewMiddleware`と`{% csrf_token %}`をフォームに確実に配置、適切なAJAXトークン処理。
- XSS：テンプレートの自動エスケープに依存、信頼できる場合を除き`mark_safe`を避ける、JSには`json_script`を使用。
- 認証：`django.contrib.auth`を使用、`AUTH_PASSWORD_VALIDATORS`でバリデータを設定。
- 秘密情報：`get_random_secret_key`で生成、環境変数またはシークレットマネージャーに保存。

### Django REST Framework (DRF)
- `DEFAULT_AUTHENTICATION_CLASSES`を設定し、制限的な`DEFAULT_PERMISSION_CLASSES`を使用、保護されたエンドポイントに`AllowAny`を残さない。
- オブジェクトレベルの認可には必ず`self.check_object_permissions(request, obj)`を呼び出します。
- シリアライザ：明示的に`fields=[...]`を指定、`exclude`と`"__all__"`を避けます。
- スロットリング：レート制限を有効化（および/またはゲートウェイ/WAFで）。
- 不要なHTTPメソッドを無効化。生SQLを避け、ORMまたはパラメータ化を使用。

### Laravel
- 本番環境：`APP_DEBUG=false`、アプリキーの生成、セキュアなファイル権限。
- Cookie/セッション：暗号化ミドルウェアを有効化、`http_only`、`same_site`、`secure`、短いライフタイムを設定。
- Mass assignment：`$request->only()`または`$request->validated()`を使用、`$request->all()`を避けます。
- SQLi：Eloquentパラメータ化を使用、動的識別子を検証。
- XSS：Bladeエスケープに依存、信頼できないデータに`{!! ... !!}`を避けます。
- ファイルアップロード：`file`、サイズ、`mimes`を検証、`basename`でファイル名をサニタイズ。
- CSRF：ミドルウェアとフォームトークンが有効化されていることを確認。

### Symfony
- XSS：Twig自動エスケープ、信頼できる場合を除き`|raw`を避けます。
- CSRF：手動フローには`csrf_token()`と`isCsrfTokenValid()`を使用、Formsはデフォルトでトークンを含む。
- SQLi：Doctrineパラメータ化クエリ、入力を連結しない。
- コマンド実行：`exec/shell_exec`を避ける、Filesystemコンポーネントを使用。
- アップロード：`#[File(...)]`で検証、パブリック外に保存、一意な名前を使用。
- ディレクトリトラバーサル：`realpath`/`basename`を検証し、許可されたルートを強制。
- セッション/セキュリティ：セキュアCookieと認証プロバイダー/ファイアウォールを設定。

### Ruby on Rails
- 危険な関数を避ける：

```ruby
eval("ruby code here")
system("os command here")
`ls -al /` # (バッククォートはOSコマンドを含む)
exec("os command here")
spawn("os command here")
open("| os command here")
Process.exec("os command here")
Process.spawn("os command here")
IO.binread("| os command here")
IO.binwrite("| os command here", "foo")
IO.foreach("| os command here") {}
IO.popen("os command here")
IO.read("| os command here")
IO.readlines("| os command here")
IO.write("| os command here", "foo")
```

- SQLi：常にパラメータ化、LIKEパターンには`sanitize_sql_like`を使用。
- XSS：デフォルト自動エスケープ、信頼できないデータに`raw`、`html_safe`を避ける、`sanitize`許可リストを使用。
- セッション：機密アプリにはデータベースバックエンドストアを使用、HTTPS強制（`config.force_ssl = true`）。
- 認証：Deviseまたはプロヴンなライブラリーを使用、ルートと保護領域を設定。
- CSRF：状態変更アクションに`protect_from_forgery`を使用。
- セキュアリダイレクト：ターゲットを検証/許可リスト化。
- ヘッダー/CORS：セキュアデフォルトを設定、`rack-cors`を慎重に設定。

### .NET (ASP.NET Core)
- ランタイムとNuGetパッケージを最新に保ち、CIでSCAを有効化。
- 認可：`[Authorize]`属性を使用、サーバー側チェックを実行、IDORを防止。
- 認証/セッション：ASP.NET Identity、ロックアウト、Cookie `HttpOnly`/`Secure`、短いタイムアウト。
- 暗号化：パスワードにPBKDF2、暗号化にAES-GCM、ローカルシークレットにDPAPI、TLS 1.2+。
- インジェクション：SQL/LDAPをパラメータ化、許可リストで検証。
- 設定：HTTPSリダイレクトを強制、バージョンヘッダーを削除、CSP/HSTS/X-Content-Type-Optionsを設定。
- CSRF：状態変更アクションにアンチフォージェリトークン、サーバーで検証。

### JavaとJAAS
- SQL/JPA：`PreparedStatement`または名前付きパラメータを使用、入力を連結しない。
- XSS：許可リスト検証、信頼できるライブラリーで出力をサニタイズ、コンテキストに応じてエンコード。
- ロギング：ログインジェクションを防ぐためパラメータ化されたロギング。
- 暗号化：AES-GCM、セキュアランダムノンス、キーのハードコーディング禁止、KMS/HSMを使用。
- JAAS：`LoginModule`スタンザを設定、`initialize/login/commit/abort/logout`を実装、資格情報の露出を避ける、パブリック/プライベート資格情報を分離、サブジェクトプリンシパルを適切に管理。

### Node.js
- リクエストサイズを制限、入力を検証・サニタイズ、出力をエスケープ。
- ユーザー入力で`eval`、`child_process.exec`を避ける、ヘッダーに`helmet`、パラメータ汚染に`hpp`を使用。
- 認証エンドポイントをレート制限、イベントループの健全性を監視、未キャッチ例外を適切に処理。
- Cookie：`secure`、`httpOnly`、`sameSite`を設定、`NODE_ENV=production`を設定。
- パッケージを最新に保つ、`npm audit`を実行、セキュリティリンターとReDoSテストを使用。

### PHP設定
- 本番環境php.ini：`expose_php=Off`、エラーを表示せずログに記録、`allow_url_fopen/include`を制限、`open_basedir`を設定。
- 危険な関数を無効化、セッションCookieフラグ（`Secure`、`HttpOnly`、`SameSite=Strict`）を設定、厳密セッションモードを有効化。
- アップロードサイズ/数を制約、リソース制限（メモリ、postサイズ、実行時間）を設定。
- 追加の堅牢化にSnuffleupagusまたは類似ツールを使用。

### 実装チェックリスト
- 各フレームワークの組み込みCSRF/XSS/セッション保護とセキュアCookieフラグを使用。
- すべてのデータアクセスをパラメータ化、信頼できない入力で危険なOS/実行関数を避けます。
- HTTPS/HSTSを強制、セキュアヘッダーを設定。
- シークレット管理を集中化、シークレットのハードコーディング禁止、本番環境でデバッグをロック。
- リダイレクトと動的識別子を検証/許可リスト化。
- 依存関係とフレームワークを最新に保ち、定期的にSCAと静的解析を実行。
