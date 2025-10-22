---
description: エラーハンドリングセキュリティベストプラクティス
languages:
- c
- java
- javascript
- python
- typescript
- xml
alwaysApply: false
---

## エラーハンドリングセキュリティガイドライン

このルールは、情報漏洩を防ぎ、適切なロギングを確保するための安全なエラーハンドリングプラクティスを示します。

- 一般的なエラーハンドリングセキュリティ
  - すべての未処理例外をキャッチするためグローバルエラーハンドラーを実装します。
  - スタックトレース、ファイルパス、バージョン情報を露出せず、汎用的なエラーメッセージを返します。
  - 調査用にサーバー側で詳細なエラー情報を安全にログに記録します。
  - 適切なHTTPステータスコードを使用：クライアントエラーには4xx、サーバーエラーには5xx。

- 本番環境設定
  - 本番環境で詳細なエラーページとデバッグ情報を無効化します。
  - ASP.NETアプリケーションのweb.configで`customErrors mode="RemoteOnly"`を設定します。
  - ASP.NET Core本番環境で開発例外ページを無効化します。
  - 汎用エラーハンドラーへの適切なエラーページリダイレクトを設定します。

- セキュアエラーロギング
  - フォレンジックのため十分なコンテキスト（ユーザーID、IPアドレス、タイムスタンプ）で例外をログに記録します。
  - エラーログにパスワード、トークン、個人情報などの機密データをログに記録しません。
  - より良い分析と監視のため構造化ロギングを使用します。
  - エラーログのログローテーションと安全なストレージを実装します。

- エラーレスポンスセキュリティ
  - RFC 7807などの標準を使用して一貫したエラーレスポンス形式を返します。
  - XSSと情報開示を防ぐためエラーレスポンスにセキュリティヘッダーを追加します。
  - エラーレスポンスコンテンツが適切にエスケープされインジェクション攻撃を防ぐことを確認します。
  - エラーレスポンスからサーバーバージョンヘッダーと技術スタック情報を削除します。

コード例（OWASPから）：

標準的なJava Webアプリケーション：
```xml
<!-- web.xml設定 -->
<error-page>
    <exception-type>java.lang.Exception</exception-type>
    <location>/error.jsp</location>
</error-page>
```

```java
<%@ page language="java" isErrorPage="true" contentType="application/json; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%
String errorMessage = exception.getMessage();
//「exception」という名前の暗黙変数の内容を介して例外をログに記録
//...
//REST APIアプリコンテキストであるため、JSON形式で汎用レスポンスを構築
//また、レスポンスがエラーであることをクライアントアプリに示すHTTPレスポンスヘッダーを追加
response.setHeader("X-ERROR", "true");
//内部サーバーエラーレスポンスを使用していることに注意
//場合によっては、誤動作しているクライアントがいる場合、4xxエラーコードを返すのが賢明
response.setStatus(500);
%>
{"message":"エラーが発生しました。再試行してください"}
```

Spring Bootグローバルエラーハンドラー：
```java

@RestControllerAdvice
public class RestResponseEntityExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(value = {Exception.class})
    public ProblemDetail handleGlobalError(RuntimeException exception, WebRequest request) {
        //「exception」という名前のパラメータの内容を介して例外をログに記録
        //...
        //内部サーバーエラーレスポンスを使用していることに注意
        //場合によっては、誤動作しているクライアントがいる場合、4xxエラーコードを返すのが賢明
        //仕様により、content-typeは「application/problem+json」または「application/problem+xml」が可能
        return ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "エラーが発生しました。再試行してください");
    }
}
```

ASP.NET Core エラーコントローラー：
```csharp
[Route("api/[controller]")]
[ApiController]
[AllowAnonymous]
public class ErrorController : ControllerBase
{
    [HttpGet]
    [HttpPost]
    [HttpHead]
    [HttpDelete]
    [HttpPut]
    [HttpOptions]
    [HttpPatch]
    public JsonResult Handle()
    {
        //このコントローラーの呼び出しを引き起こした例外を取得
        Exception exception = HttpContext.Features.Get<IExceptionHandlerFeature>()?.Error;
        //「exception」という名前の変数の内容を介して例外をログに記録（NULLでない場合）
        //...
        //REST APIアプリコンテキストであるため、JSON形式で汎用レスポンスを構築
        //また、レスポンスがエラーであることをクライアントアプリに示すHTTPレスポンスヘッダーを追加
        var responseBody = new Dictionary<String, String>{ {
            "message", "エラーが発生しました。再試行してください"
        } };
        JsonResult response = new JsonResult(responseBody);
        //内部サーバーエラーレスポンスを使用していることに注意
        //場合によっては、誤動作しているクライアントがいる場合、4xxエラーコードを返すのが賢明
        response.StatusCode = (int)HttpStatusCode.InternalServerError;
        Request.HttpContext.Response.Headers.Remove("X-ERROR");
        Request.HttpContext.Response.Headers.Add("X-ERROR", "true");
        return response;
    }
}
```

ASP.NET Web.configセキュリティ設定：
```xml
<configuration>
    <system.web>
        <customErrors mode="RemoteOnly"
                      defaultRedirect="~/ErrorPages/Oops.aspx" />
    </system.web>
</configuration>
```

まとめ：
集中化されたエラーハンドリングを汎用的なユーザーメッセージで実装し、詳細なエラー情報を安全にログに記録します。本番環境でデバッグ情報を無効化し、エラーレスポンスが機密システム詳細を漏洩しないことを確保します。
