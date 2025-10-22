---
description: Django REST Frameworkセキュリティベストプラクティス
languages:
- python
- yaml
alwaysApply: false
---

## Django REST Frameworkセキュリティガイドライン

このルールは、一般的なリスクから保護するためDjango REST Framework APIを開発する際の重要なセキュリティプラクティスを示します。

- 認証・認可
  - すべての非公開エンドポイントに適切な認証スキームで`DEFAULT_AUTHENTICATION_CLASSES`を常に設定します。
  - SessionAuthenticationを使用する場合、CSRF保護が有効化され適切に設定されていることを確認します。
  - `DEFAULT_PERMISSION_CLASSES`を`AllowAny`のままにしません。適切な権限クラスを使用してアクセスを明示的に制限します。
  - `get_object()`をオーバーライドする場合、オブジェクトレベルのアクセス制御を強制するため必ず`self.check_object_permissions(request, obj)`を呼び出します。
  - 認証、権限、スロットルクラスのビュー単位のオーバーライドは、その影響を完全に理解している場合を除き避けます。

- シリアライザセキュリティ
  - DRFシリアライザで明示的な`fields = [...]`許可リストを指定、`exclude`を使用しません。
  - DjangoのModelForm（DRF外で使用する場合）では、`Meta.exclude`または`"__all__"`の代わりに必ず`Meta.fields`許可リストを使用します。
  - `Meta.exclude`（拒否リストアプローチ）または`ModelForms.Meta.fields = "__all__"`を使用しないでください。

- レート制限・スロットリング
  - DoS防御レイヤーとしてAPIレート制限を有効にするため`DEFAULT_THROTTLE_CLASSES`を設定します。
  - ゲートウェイまたはWAFレベルでのレート制限強制を優先、DRFスロットリングは最後の手段の保護手段です。

- セキュリティ設定
  - 本番環境では`DEBUG`と`DEBUG_PROPAGATE_EXCEPTIONS`を`False`に設定していることを確認します。
  - `SECRET_KEY`などのシークレットをハードコーディングしません。環境変数またはシークレットマネージャーから注入します。
  - 使用されていないまたは危険なHTTPメソッド（例：PUT、DELETE）をAPIレベルで無効化します。
  - すべての受信データを厳密に検証、サニタイズ、フィルタリングします。
  - セキュアHTTPヘッダーを設定：`SECURE_CONTENT_TYPE_NOSNIFF = True`、`X_FRAME_OPTIONS = 'DENY'`、`SECURE_BROWSER_XSS_FILTER = True`。
  - XSSとクリックジャッキング攻撃を防ぐため、django-cspミドルウェアを使用してContent Security Policy（CSP）を実装します。

- インジェクション攻撃の防止
  - ユーザー入力を伴う生SQLクエリを避け、ORMまたはパラメータ化クエリのみを使用します。
  - ユーザー入力を危険なメソッド（`raw()`、`extra()`、`cursor.execute()`）に追加しないでください。
  - YAML解析には安全なローダー（`yaml.SafeLoader`）を使用、信頼できないソースからのYAMLまたはpickleデータを解析しません。
  - ユーザー入力に対して`eval()`、`exec()`、または類似の動的コード実行関数を使用しないでください。

- シークレット管理
  - `SECRET_KEY`などのシークレットをハードコーディングしません。環境変数またはシークレットマネージャーから注入します。
  - APIキー、データベースパスワード、その他の機密資格情報をソースコードにハードコーディングしないでください。

- 入力検証
  - クライアント提供のすべてのデータを厳密に検証、サニタイズ、フィルタリングします。
  - Djangoの組み込みフォーム検証またはDRFシリアライザを適切な検証メソッドで使用します。

- ロギングセキュリティ
  - 認証失敗、認可拒否、検証エラーを十分なコンテキストでログに記録します。
  - 機密データ（パスワード、トークン、PII）をアプリケーションログに記録しないでください。
  - セキュリティ関連のログエントリにスタックトレース、エラーメッセージ、ユーザーコンテキストを含めます。

まとめ：
オブジェクトレベルの権限を`check_object_permissions()`で必ず強制し、シリアライザで明示的なフィールド許可リストを使用し、ユーザー入力で危険な関数を避け、シークレットをハードコーディングせず、適切な入力検証を実装し、セキュリティを意識したロギングプラクティスを確保します。
