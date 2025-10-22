---
description: Djangoセキュリティベストプラクティス
languages:
- c
- python
alwaysApply: false
---

## Djangoセキュリティガイドライン

このルールは、一般的なWeb脆弱性を防ぐための重要なDjangoセキュリティプラクティスを示します。

- 一般的なセキュリティ設定
  - 本番環境で`DEBUG = True`を設定しません。
  - Djangoと依存関係を定期的に最新に保ちます。
  - ブルートフォース保護のため`django_ratelimit`または`django-axes`などのレート制限パッケージを使用します。

- 認証システム
  - `INSTALLED_APPS`に`django.contrib.auth`、`django.contrib.contenttypes`、`django.contrib.sessions`を含めます。
  - 認証が必要なビューを保護するため`@login_required`デコレータを使用します。
  - パスワードポリシーのため`AUTH_PASSWORD_VALIDATORS`を適切なバリデータで設定します。
  - パスワードハッシュ化と検証には`make_password()`と`check_password()`関数を使用します。

- シークレットキー管理
  - 文字、数字、記号を含む少なくとも50文字で`SECRET_KEY`を生成します。
  - キー生成には`get_random_secret_key()`関数を使用します。
  - `SECRET_KEY`を環境変数に保存し、ソースにハードコーディングしません。
  - キーを定期的にローテーションし、露出時には即座に行います。

- セキュリティミドルウェア設定
  - `MIDDLEWARE`設定に`django.middleware.security.SecurityMiddleware`を含めます。
  - `MIDDLEWARE`設定に`django.middleware.clickjacking.XFrameOptionsMiddleware`を含めます。
  - MIMEタイプ保護のため`SECURE_CONTENT_TYPE_NOSNIFF = True`を設定します。
  - HTTPS強制のため`SECURE_HSTS_SECONDS`を正の整数で設定します。
  - クリックジャッキング保護のため`X_FRAME_OPTIONS = 'DENY'`または`'SAMEORIGIN'`を設定します。

- Cookie セキュリティ
  - HTTPS経由でのみセッションCookieを送信するため`SESSION_COOKIE_SECURE = True`を設定します。
  - HTTPS経由でのみCSRF Cookieを送信するため`CSRF_COOKIE_SECURE = True`を設定します。
  - `HttpResponse.set_cookie()`でカスタムCookieを設定する際は`secure=True`パラメータを使用します。

- CSRF保護
  - `MIDDLEWARE`設定に`django.middleware.csrf.CsrfViewMiddleware`を含めます。
  - すべてのフォームで`{% csrf_token %}`テンプレートタグを使用します。
  - AJAX呼び出しのためCSRFトークンを適切に抽出します。

- XSS保護
  - 自動HTMLエスケープを伴うDjangoの組み込みテンプレートシステムを使用します。
  - 信頼できるソースからの入力でない限り、`safe`フィルターと`mark_safe`関数を避けます。
  - JavaScriptにデータを渡すため`json_script`テンプレートフィルターを使用します。

- HTTPS設定
  - HTTPリクエストをHTTPSにリダイレクトするため`SECURE_SSL_REDIRECT = True`を設定します。
  - プロキシまたはロードバランサーの背後にある場合、`SECURE_PROXY_SSL_HEADER`を設定します。

- 管理パネルセキュリティ
  - `urls.py`でデフォルトの管理URLを`/admin/`からカスタムパスに変更します。

コード例（OWASPから）：

```python
# 認証のセットアップ
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
]

@login_required
def my_view(request):
    # ビューロジック

# パスワード検証
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
]

# 環境変数からのシークレットキー
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Cookieセキュリティ
response.set_cookie('my_cookie', 'cookie_value', secure=True)
```

```html
<!-- フォームのCSRF -->
<form method="post">
    {% csrf_token %}
    <!-- ここにフォームフィールド -->
</form>
```

まとめ：
本番環境でデバッグモードを無効化し、適切な認証設定を使用し、シークレットキーを安全に保ち、セキュリティミドルウェアを有効化し、安全なCookie属性を設定し、CSRF保護を実装し、XSSを防止し、HTTPSを強制し、管理者アクセスを保護することでDjangoを安全に設定します。
