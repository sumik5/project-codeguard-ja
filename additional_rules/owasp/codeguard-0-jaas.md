---
description: JAASセキュリティのベストプラクティス
languages:
- c
- java
- xml
alwaysApply: false
---

## はじめに - JAAS認証とは

ユーザーまたは他のシステムの身元を確認するプロセスが認証です。

JAASは認証フレームワークとして、ログインからログアウトまで、認証されたユーザーの身元と認証情報を管理します。

JAAS認証ライフサイクル：

1. `LoginContext`を作成。
2. 初期化する1つ以上の`LoginModule`の設定ファイルを読み取る。
3. 各LoginModuleを初期化するため`LoginContext.initialize()`を呼び出す。
4. 各LoginModuleのため`LoginContext.login()`を呼び出す。
5. ログイン成功の場合`LoginContext.commit()`を呼び出し、失敗の場合`LoginContext.abort()`を呼び出す

## 設定ファイル

JAAS設定ファイルには、アプリケーションへのログオンに利用可能な各`LoginModule`のための`LoginModule`スタンザが含まれています。

JAAS設定ファイルからのスタンザ：

```text
Branches
{
    USNavy.AppLoginModule required
    debug=true
    succeeded=true;
}
```

セミコロンの配置に注意してください。`LoginModule`エントリとスタンザの両方を終了します。

requiredという単語は、ユーザーをログインする際に`LoginContext`の`login()`メソッドが成功する必要があることを示します。`LoginModule`固有の値`debug`と`succeeded`は`LoginModule`に渡されます。

これらは`LoginModule`によって定義され、その使用は`LoginModule`内で管理されます。オプションは`debug="true"`のようなキーバリューペアを使用して設定され、キーと値は`=`記号で区切られる必要があります。

## Main.java（クライアント）

- 実行構文：

```text
Java –Djava.security.auth.login.config==packageName/packageName.config
        packageName.Main Stanza1

ここで：
    packageNameは設定ファイルを含むディレクトリ。
    packageName.configはJavaパッケージpackageName内の設定ファイルを指定。
    packageName.MainはJavaパッケージpackageName内のMain.javaを指定。
    Stanza1はMain()が設定ファイルから読み取るべきスタンザの名前。
```

- 実行時、第1コマンドライン引数は設定ファイルからのスタンザです。スタンザは使用される`LoginModule`に名前を付けます。第2引数は`CallbackHandler`です。
- Main.javaに渡された引数で新しい`LoginContext`を作成します。
    - `loginContext = new LoginContext (args[0], new AppCallbackHandler());`
- LoginContext.Login Moduleを呼び出します：
    - `loginContext.login();`
- succeededオプションの値が`loginContext.login()`から返されます。
- ログインが成功した場合、subjectが作成されました。

## LoginModule.java

`LoginModule`には以下の認証メソッドが必要です：

- `initialize()`
- `login()`
- `commit()`
- `abort()`
- `logout()`

### initialize()

`Main()`内で、`LoginContext`が設定ファイルから正しいスタンザを読み取った後、`LoginContext`はスタンザで指定された`LoginModule`をインスタンス化します。

- `initialize()`メソッドのシグネチャ：
    - `Public void initialize (Subject subject, CallbackHandler callbackHandler, Map sharedState, Map options)`
- 上記の引数は以下のように保存する必要があります：
    - `this.subject = subject;`
    - `this.callbackHandler = callbackHandler;`
    - `this.sharedState = sharedState;`
    - `this.options = options;`
- `initialize()`メソッドが行うこと：
    - 成功した`login()`を条件とする`Subject`クラスのsubjectオブジェクトを構築します。
    - ログイン情報を収集するためにユーザーと対話する`CallbackHandler`を設定します。
    - `LoginContext`が2つ以上のLoginModuleを指定する場合、これは合法であり、`sharedState`マップを介して情報を共有できます。
    - debugやsucceededなどの状態情報をoptionsマップに保存します。

### login()

ユーザー提供のログイン情報をキャプチャします。以下のコードスニペットは、`callbackHandler.java`プログラムの`callbackHandler.handle`メソッドに渡されると、ユーザーによって対話的に提供されたユーザー名とパスワードで読み込まれる2つのコールバックオブジェクトの配列を宣言します：

```java
 NameCallback nameCB = new NameCallback("Username");
 PasswordCallback passwordCB = new PasswordCallback ("Password", false);
Callback[] callbacks = new Callback[] { nameCB, passwordCB };
callbackHandler.handle (callbacks);
```

- ユーザーを認証します
- コールバックオブジェクトからユーザー提供情報を取得します：
    - `String ID = nameCallback.getName ();`
    - `char[] tempPW = passwordCallback.getPassword ();`
- `name`と`tempPW`をLDAPなどのリポジトリに保存された値と比較します。
- 変数succeededの値を設定し、`Main()`に戻ります。

### commit()

`login()`中にユーザーの認証情報が正常に検証されると、JAAS認証フレームワークは必要に応じて認証情報をsubjectに関連付けます。

認証情報には**Public**と**Private**の2種類があります：

- Public認証情報には公開鍵が含まれます。
- Private認証情報にはパスワードと公開鍵が含まれます。

Principals（つまりログイン名以外のsubjectが持つ身元）、例えば従業員番号やユーザーグループのメンバーシップIDは、subjectに追加されます。

以下は、認証されたユーザーがメンバーシップを持つ各グループについて、最初にグループ名がprincipalとしてsubjectに追加される例の`commit()`メソッドです。次に、subjectのユーザー名がパブリック認証情報に追加されます。

Principalsとパブリック認証情報をsubjectに設定して追加するコードスニペット：

```java
public boolean commit() {
    If (userAuthenticated) {
        Set groups = UserService.findGroups (username);
        for (Iterator itr = groups.iterator (); itr.hasNext (); {
            String groupName = (String) itr.next ();
            UserGroupPrincipal group = new UserGroupPrincipal (GroupName);
            subject.getPrincipals ().add (group);
        }
        UsernameCredential cred = new UsernameCredential (username);
        subject.getPublicCredentials().add (cred);
    }
}
```

### abort()

`abort()`メソッドは認証が成功しなかった場合に呼び出されます。`abort()`メソッドが`LoginModule`を終了する前に、ユーザー名やパスワード入力フィールドを含む状態をリセットするよう注意する必要があります。

### logout()

`LoginContext.logout`が呼び出されたときのユーザーのprincipalsと認証情報の解放：

```java
public boolean logout() {
    if (!subject.isReadOnly()) {
        Set principals = subject.getPrincipals(UserGroupPrincipal.class);
        subject.getPrincipals().removeAll(principals);
        Set creds = subject.getPublicCredentials(UsernameCredential.class);
        subject.getPublicCredentials().removeAll(creds);
        return true;
    } else {
        return false;
    }
}
```

## CallbackHandler.java

`callbackHandler`は、異なるコールバックオブジェクトを持つ多数のLoginModuleにサービスを提供できるように、単一の`LoginModule`とは別のソース（`.java`）ファイルにあります：

- `CallbackHandler`クラスのインスタンスを作成し、`handle()`メソッドのみを持ちます。
- ログインにユーザー名とパスワードを必要とするLoginModuleにサービスを提供する`CallbackHandler`：

```java
public void handle(Callback[] callbacks) {
    for (int i = 0; i < callbacks.length; i++) {
        Callback callback = callbacks[i];
        if (callback instanceof NameCallback) {
            NameCallback nameCallBack = (NameCallback) callback;
            nameCallBack.setName(username);
    }  else if (callback instanceof PasswordCallback) {
            PasswordCallback passwordCallBack = (PasswordCallback) callback;
            passwordCallBack.setPassword(password.toCharArray());
        }
    }
}
```
