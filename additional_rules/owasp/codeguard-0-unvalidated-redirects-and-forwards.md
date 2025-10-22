---
description: 未検証のリダイレクトとフォワードの防止
languages:
- c
- java
- javascript
- php
- ruby
- rust
- typescript
alwaysApply: false
---

## 未検証のリダイレクトとフォワードの防止

すべてのユーザー制御のリダイレクト先を検証することで、オープンリダイレクトとフォワードの脆弱性を防止し、フィッシング攻撃とアクセス制御バイパスを阻止します。

### セキュリティリスク

未検証のリダイレクトとフォワードは、アプリケーションがリダイレクト先に信頼できない入力を受け入れる場合に発生し、以下を可能にします：
- 信頼されたドメインの外観を維持したまま悪意のあるサイトにユーザーをリダイレクトするフィッシング攻撃
- 通常制限されている特権機能へのフォワードによるアクセス制御バイパス
- 攻撃者が制御するサイトへの説得力のあるリダイレクトによるユーザー認証情報の盗難

### 安全なリダイレクトの例

セキュアなリダイレクトは、攻撃者が操作できないハードコードされたURLを使用します：

Java:
```java
response.sendRedirect("http://www.mysite.com");
```

PHP:
```php
<?php
/* Redirect browser */
header("Location: http://www.mysite.com");
/* Exit to prevent the rest of the code from executing */
exit;
?>
```

ASP .NET:
```csharp
Response.Redirect("~/folder/Login.aspx")
```

Rails:
```ruby
redirect_to login_path
```

Rust actix web:
```rust
  Ok(HttpResponse::Found()
        .insert_header((header::LOCATION, "https://mysite.com/"))
        .finish())
```

### 危険なリダイレクトの例

脆弱なコードはリダイレクト先にユーザー入力を直接受け入れます：

Java:
```java
response.sendRedirect(request.getParameter("url"));
```

PHP:
```php
$redirect_url = $_GET['url'];
header("Location: " . $redirect_url);
```

C# .NET:
```csharp
string url = request.QueryString["url"];
Response.Redirect(url);
```

Rails:
```ruby
redirect_to params[:url]
```

Rust actix web:
```rust
  Ok(HttpResponse::Found()
        .insert_header((header::LOCATION, query_string.path.as_str()))
        .finish())
```

ASP.NET MVC脆弱な例：
```csharp
[HttpPost]
 public ActionResult LogOn(LogOnModel model, string returnUrl)
 {
   if (ModelState.IsValid)
   {
     if (MembershipService.ValidateUser(model.UserName, model.Password))
     {
       FormsService.SignIn(model.UserName, model.RememberMe);
       if (!String.IsNullOrEmpty(returnUrl))
       {
         return Redirect(returnUrl);
       }
       else
       {
         return RedirectToAction("Index", "Home");
       }
     }
     else
     {
       ModelState.AddModelError("", "The user name or password provided is incorrect.");
     }
   }

   // If we got this far, something failed, redisplay form
   return View(model);
 }
```

攻撃の例：
```text
 http://example.com/example.php?url=http://malicious.example.com
```

### 危険なフォワードの例

ユーザー入力がフォワード先を決定する場合、サーバーサイドフォワードはアクセス制御をバイパスできます：

Javaサーブレット脆弱なフォワード：
```java
public class ForwardServlet extends HttpServlet
{
  protected void doGet(HttpServletRequest request, HttpServletResponse response)
                    throws ServletException, IOException {
    String query = request.getQueryString();
    if (query.contains("fwd"))
    {
      String fwd = request.getParameter("fwd");
      try
      {
        request.getRequestDispatcher(fwd).forward(request, response);
      }
      catch (ServletException e)
      {
        e.printStackTrace();
      }
    }
  }
}
```

攻撃の例：
```text
http://www.example.com/function.jsp?fwd=admin.jsp
```

### 防止戦略

#### 宛先にユーザー入力を使用しない
単にリダイレクトとフォワードを使用しないか、宛先のユーザー入力としてURLを許可しないでください。

#### サーバーサイドマッピングを使用
ユーザーに短縮名、ID、またはトークンを提供させ、サーバーサイドで完全なターゲットURLにマッピングします。

利点：
- URL改ざんに対する最高度の保護
- 直接URL操作を防止

考慮事項：
- ユーザーがIDをサイクルする列挙脆弱性を防止
- 十分に大きいまたは複雑なトークンスペースを使用

#### 入力検証と認可
ユーザー入力を避けられない場合：
- 提供された値がアプリケーションにとって有効で適切であることを確認
- ユーザーがリダイレクト/フォワードターゲットに対して認可されていることを検証
- リダイレクトまたはフォワードを実行する前に検証

#### 許可リストアプローチ
信頼できるURLまたはホストのリストを作成して実施：
- 拒否リストではなく許可リストアプローチを使用
- 信頼できるURLリストに対して入力をサニタイズ
- 柔軟なマッチングのために正規表現パターンを検討

#### 外部リダイレクト警告
間接警告ページを通じて外部リダイレクトを強制：
- ユーザーに宛先を明確に表示
- 続行する前にユーザー確認を要求
- ユーザーが潜在的なフィッシング試行を識別するのを支援

#### フレームワーク固有の考慮事項

PHP:
- `header("Location: ...")`の後は常に`exit;`を続ける
- リダイレクト後のコード実行の継続を防止

ASP.NET MVC:
- MVC 1と2は特にオープンリダイレクション攻撃に脆弱
- 脆弱性を回避するためMVC 3以降を使用

### 実装ガイドライン

1. 可能な限りリダイレクトにハードコードされたURLを使用
2. ユーザー制御のリダイレクトにサーバーサイドマッピングを実装
3. 許可された宛先の許可リストに対してすべてのユーザー入力を検証
4. リダイレクトまたはフォワードを実行する前にユーザー認可を検証
5. 外部リダイレクトに間接警告を使用
6. フレームワーク固有のセキュリティプラクティスに従う
7. 複雑なトークンスペースを通じて列挙を防止
8. セキュリティパッチでフレームワークを最新に保つ
9. リダイレクト先の決定にユーザー入力を信頼しない
10. バイパス試行のためにリダイレクト機能をテスト
