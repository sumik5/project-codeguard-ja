---
description: マスアサインメント防止
languages:
- c
- java
- javascript
- php
- ruby
- scala
alwaysApply: false
---

## マスアサインメント防止ガイドライン

攻撃者が意図しないオブジェクトプロパティを変更できるようにするマスアサインメント脆弱性を防ぐための必須プラクティス。

### マスアサインメントの理解

マスアサインメントは、フレームワークがHTTPリクエストパラメータをプログラム変数またはオブジェクトに自動的にバインドするときに発生します。攻撃者は新しいパラメータを作成して`isAdmin`やその他の権限関連プロパティなどの機密フィールドを上書きすることでこれを悪用できます。

**フレームワーク別の代替名：**
- マスアサインメント：Ruby on Rails、NodeJS
- 自動バインディング：Spring MVC、ASP NET MVC
- オブジェクトインジェクション：PHP

### 脆弱な例

典型的なフィールドを持つユーザーフォーム：
```html
<form>
     <input name="userid" type="text">
     <input name="password" type="text">
     <input name="email" text="text">
     <input type="submit">
</form>
```

機密フィールドを持つユーザーオブジェクト：
```java
public class User {
   private String userid;
   private String password;
   private String email;
   private boolean isAdmin;
   //Getters & Setters
}
```

自動バインディングを持つ脆弱なコントローラー：
```java
@RequestMapping(value = "/addUser", method = RequestMethod.POST)
public String submit(User user) {
   userService.add(user);
   return "successPage";
}
```

攻撃ペイロード：
```text
POST /addUser
userid=bobbytables&password=hashedpass&email=bobby@tables.com&isAdmin=true
```

### 主要な防御戦略

**1. データ転送オブジェクト（DTO）を使用**
安全で編集可能なフィールドのみを公開するオブジェクトを作成：

```java
public class UserRegistrationFormDTO {
 private String userid;
 private String password;
 private String email;
 //注意：isAdminフィールドは存在しない
 //Getters & Setters
}
```

**2. 許可リストアプローチ**
バインディングのために許可されたフィールドを明示的に定義。

**3. ブロックリストアプローチ**
バインディングから機密フィールドを明示的に除外。

### フレームワーク固有の実装

#### Spring MVC

許可されたフィールドの許可リスト：
```java
@Controller
public class UserController {
    @InitBinder
    public void initBinder(WebDataBinder binder, WebRequest request) {
        binder.setAllowedFields(["userid","password","email"]);
    }
}
```

機密フィールドのブロックリスト：
```java
@Controller
public class UserController {
   @InitBinder
   public void initBinder(WebDataBinder binder, WebRequest request) {
      binder.setDisallowedFields(["isAdmin"]);
   }
}
```

#### NodeJS + Mongoose

underscore.jsを使用した許可リスト：
```javascript
var UserSchema = new mongoose.Schema({
    userid: String,
    password: String,
    email : String,
    isAdmin : Boolean,
});

UserSchema.statics = {
    User.userCreateSafeFields: ['userid', 'password', 'email']
};

var User = mongoose.model('User', UserSchema);

_ = require('underscore');
var user = new User(_.pick(req.body, User.userCreateSafeFields));
```

mongoose-mass-assignプラグインを使用したブロックリスト：
```javascript
var massAssign = require('mongoose-mass-assign');

var UserSchema = new mongoose.Schema({
    userid: String,
    password: String,
    email : String,
    isAdmin : { type: Boolean, protect: true, default: false }
});

UserSchema.plugin(massAssign);
var User = mongoose.model('User', UserSchema);

var user = User.massAssign(req.body);
```

#### PHP Laravel + Eloquent

$fillableを使用した許可リスト：
```php
<?php
namespace App;
use Illuminate\Database\Eloquent\Model;

class User extends Model {
    private $userid;
    private $password;
    private $email;
    private $isAdmin;

    protected $fillable = array('userid','password','email');
}
```

$guardedを使用したブロックリスト：
```php
<?php
namespace App;
use Illuminate\Database\Eloquent\Model;

class User extends Model {
    private $userid;
    private $password;
    private $email;
    private $isAdmin;

    protected $guarded = array('isAdmin');
}
```

### 悪用可能性の条件

以下の場合、マスアサインメントは悪用可能になります：
- 攻撃者が一般的な機密フィールドを推測できる
- 攻撃者がモデルをレビューするソースコードにアクセスできる
- ターゲットオブジェクトに空のコンストラクタがある

### 主要な防止原則

1. 機密フィールドを持つドメインオブジェクトにユーザー入力を直接バインドしない
2. DTOを使用して安全で編集可能なフィールドのみを公開
3. フレームワーク固有の許可リストまたはブロックリストメカニズムを適用
4. 機密属性のモデルを定期的にレビュー
5. 可能な限りブロックリストよりも許可リストを優先

マスアサインメント保護は、不正な権限昇格とデータ操作攻撃を防ぐために重要です。
