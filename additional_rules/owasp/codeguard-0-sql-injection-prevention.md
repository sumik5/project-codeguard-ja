---
description: SQLインジェクション防止ガイドライン
languages:
- c
- go
- java
- javascript
- perl
- php
- python
- ruby
- sql
- typescript
alwaysApply: false
---

## SQLインジェクション防止ガイドライン

文字列連結の代わりにセキュアなデータベースクエリ構築メソッドを使用して、SQLインジェクション攻撃を防止するための必須プラクティス。

### SQLインジェクションの理解

SQLインジェクションは、アプリケーションがユーザー入力をSQL文字列に直接連結する動的データベースクエリを使用する場合に発生します。攻撃者はこれを悪用して悪意のあるSQLコードを実行できます。SQLインジェクションを防止するには、開発者は文字列連結による動的クエリの記述を停止するか、実行されるクエリに悪意のあるSQL入力が含まれないようにする必要があります。

### 主要な防御オプション

#### オプション1: プリペアドステートメント（パラメータ化クエリ） - 推奨

変数バインディングを使用したプリペアドステートメントを使用して、SQLコードとデータを分離します。データベースは常にコードとデータを区別し、攻撃者がクエリの意図を変更することを防ぎます。

安全なJavaの例：
```java
// This should REALLY be validated too
String custname = request.getParameter("customerName");
// Perform input validation to detect attacks
String query = "SELECT account_balance FROM user_data WHERE user_name = ? ";
PreparedStatement pstmt = connection.prepareStatement( query );
pstmt.setString( 1, custname);
ResultSet results = pstmt.executeQuery( );
```

安全なC# .NETの例：
```csharp
String query = "SELECT account_balance FROM user_data WHERE user_name = ?";
try {
  OleDbCommand command = new OleDbCommand(query, connection);
  command.Parameters.Add(new OleDbParameter("customerName", CustomerName Name.Text));
  OleDbDataReader reader = command.ExecuteReader();
  // …
} catch (OleDbException se) {
  // error handling
}
```

安全なHQLの例：
```java
// This is an unsafe HQL statement
Query unsafeHQLQuery = session.createQuery("from Inventory where productID='"+userSuppliedParameter+"'");
// Here is a safe version of the same query using named parameters
Query safeHQLQuery = session.createQuery("from Inventory where productID=:productid");
safeHQLQuery.setParameter("productid", userSuppliedParameter);
```

#### オプション2: ストアドプロシージャ（安全に実装された場合）

入力がパラメータ化され、ストアドプロシージャ内で動的SQL生成が発生しない場合のみストアドプロシージャを使用します。

安全なJavaストアドプロシージャの例：
```java
// This should REALLY be validated
String custname = request.getParameter("customerName");
try {
  CallableStatement cs = connection.prepareCall("{call sp_getAccountBalance(?)}");
  cs.setString(1, custname);
  ResultSet results = cs.executeQuery();
  // … result set handling
} catch (SQLException se) {
  // … logging and error handling
}
```

安全なVB .NETストアドプロシージャの例：
```vbnet
 Try
   Dim command As SqlCommand = new SqlCommand("sp_getAccountBalance", connection)
   command.CommandType = CommandType.StoredProcedure
   command.Parameters.Add(new SqlParameter("@CustomerName", CustomerName.Text))
   Dim reader As SqlDataReader = command.ExecuteReader()
   '...
 Catch se As SqlException
   'error handling
 End Try
```

#### オプション3: 許可リスト入力検証

バインド変数を使用できないSQL要素（テーブル名、カラム名、ソートインジケーター）には、厳格な許可リストを使用します。

安全なテーブル名検証：
```text
String tableName;
switch(PARAM):
  case "Value1": tableName = "fooTable";
                 break;
  case "Value2": tableName = "barTable";
                 break;
  ...
  default      : throw new InputValidationException("unexpected value provided"
                                                  + " for table name");
```

ソート順の安全な動的クエリ：
```java
public String someMethod(boolean sortOrder) {
 String SQLquery = "some SQL ... order by Salary " + (sortOrder ? "ASC" : "DESC");`
 ...
```

#### オプション4: エスケープ（強く非推奨）

ユーザー入力のエスケープはデータベース固有で、エラーが発生しやすく、すべてのSQLインジェクションの防止を保証できません。代わりにパラメータ化クエリを使用してください。

### 追加の防御

#### 最小権限

すべてのデータベースアカウントの権限を最小化：
- 必要なアクセス権のみを付与（読み取り vs. 書き込み）
- アプリケーションアカウントにDBAまたは管理者アクセスを避ける
- 異なるアプリケーションに個別のデータベースユーザーを使用
- データアクセスをさらに制限するためにビューの使用を検討

#### 入力検証

SQL実行前に不正な入力を検出するため、二次防御として入力検証を使用します。検証済みデータは必ずしも文字列連結に安全ではありません - 常にパラメータ化クエリを使用してください。

### 重要な原則

- すべてのSQLコードを最初に定義し、その後パラメータを個別に渡す
- ユーザー入力をSQL文字列に直接連結しない
- ユーザー入力をデータとして扱い、実行可能なSQLコードとして扱わない
- 最小権限データベースアカウントを使用
- 主要な保護ではなく、多層防御として入力検証を実装
