---
description: クエリパラメータ化によるSQLインジェクション防止
languages:
- c
- java
- perl
- php
- ruby
- rust
- sql
alwaysApply: false
---

## クエリパラメータ化ガイドライン

データベースクエリを構築する際に文字列連結の代わりにパラメータ化されたクエリを使用することでSQLインジェクション攻撃を防ぐための必須プラクティス。

### 基本原則

SQLインジェクションは、SQL構造とデータを分離するパラメータ化されたクエリによって防止されます。ユーザー入力は実行可能なSQLコードではなくデータパラメータとして扱われ、攻撃者がクエリ構造を変更することを防ぎます。

### 実装要件

常に言語固有のパラメータ化されたクエリまたはプリペアドステートメントを使用します:

#### JavaでPreparedStatementを使用
```java
String custname = request.getParameter("customerName");
String query = "SELECT account_balance FROM user_data WHERE user_name = ? ";
PreparedStatement pstmt = connection.prepareStatement( query );
pstmt.setString( 1, custname);
ResultSet results = pstmt.executeQuery( );
```

#### JavaでHibernateを使用
```java
// HQL
@Entity // エンティティとして宣言;
@NamedQuery(
 name="findByDescription",
 query="FROM Inventory i WHERE i.productDescription = :productDescription"
)
public class Inventory implements Serializable {
 @Id
 private long id;
 private String productDescription;
}

// ユースケース
// これも本当に検証すべき
String userSuppliedParameter = request.getParameter("Product-Description");
// 攻撃を検出するための入力検証を実行
List<Inventory> list =
 session.getNamedQuery("findByDescription")
 .setParameter("productDescription", userSuppliedParameter).list();

// Criteria API
// これも本当に検証すべき
String userSuppliedParameter = request.getParameter("Product-Description");
// 攻撃を検出するための入力検証を実行
Inventory inv = (Inventory) session.createCriteria(Inventory.class).add
(Restrictions.eq("productDescription", userSuppliedParameter)).uniqueResult();
```

#### .NETでOleDbCommandを使用
```csharp
String query = "SELECT account_balance FROM user_data WHERE user_name = ?";
try {
   OleDbCommand command = new OleDbCommand(query, connection);
   command.Parameters.Add(new OleDbParameter("customerName", CustomerName Name.Text));
   OleDbDataReader reader = command.ExecuteReader();
   // …
} catch (OleDbException se) {
   // エラー処理
}
```

#### ASP.NETでSqlCommandを使用
```csharp
string sql = "SELECT * FROM Customers WHERE CustomerId = @CustomerId";
SqlCommand command = new SqlCommand(sql);
command.Parameters.Add(new SqlParameter("@CustomerId", System.Data.SqlDbType.Int));
command.Parameters["@CustomerId"].Value = 1;
```

#### RubyでActiveRecordを使用
```ruby
## 作成
Project.create!(:name => 'owasp')
## 読み取り
Project.all(:conditions => "name = ?", name)
Project.all(:conditions => { :name => name })
Project.where("name = :name", :name => name)
## 更新
project.update_attributes(:name => 'owasp')
## 削除
Project.delete(:name => 'name')
```

#### Ruby組み込み
```ruby
insert_new_user = db.prepare "INSERT INTO users (name, age, gender) VALUES (?, ? ,?)"
insert_new_user.execute 'aizatto', '20', 'male'
```

#### PHPでPDOを使用
```php
$stmt = $dbh->prepare("INSERT INTO REGISTRY (name, value) VALUES (:name, :value)");
$stmt->bindParam(':name', $name);
$stmt->bindParam(':value', $value);
```

#### Cold Fusion
```coldfusion
<cfquery name = "getFirst" dataSource = "cfsnippets">
    SELECT * FROM #strDatabasePrefix#_courses WHERE intCourseID =
    <cfqueryparam value = #intCourseID# CFSQLType = "CF_SQL_INTEGER">
</cfquery>
```

#### PerlでDBIを使用
```perl
my $sql = "INSERT INTO foo (bar, baz) VALUES ( ?, ? )";
my $sth = $dbh->prepare( $sql );
$sth->execute( $bar, $baz );
```

#### RustでSQLxを使用
```rust
// CLIの引数からの入力だが何でも可
let username = std::env::args().last().unwrap();

// 組み込みマクロを使用（コンパイル時チェック）
let users = sqlx::query_as!(
        User,
        "SELECT * FROM users WHERE name = ?",
        username
    )
    .fetch_all(&pool)
    .await
    .unwrap();

// 組み込み関数を使用
let users: Vec<User> = sqlx::query_as::<_, User>(
        "SELECT * FROM users WHERE name = ?"
    )
    .bind(&username)
    .fetch_all(&pool)
    .await
    .unwrap();
```

### ストアドプロシージャのセキュリティ

#### 通常のストアドプロシージャ
パラメータは特別な要件なしに自然にバインドされます:

##### Oracle PL/SQL
```sql
PROCEDURE SafeGetBalanceQuery(UserID varchar, Dept varchar) AS BEGIN
   SELECT balance FROM accounts_table WHERE user_ID = UserID AND department = Dept;
END;
```

##### SQL Server T-SQL
```sql
PROCEDURE SafeGetBalanceQuery(@UserID varchar(20), @Dept varchar(10)) AS BEGIN
   SELECT balance FROM accounts_table WHERE user_ID = @UserID AND department = @Dept
END
```

#### ストアドプロシージャ内の動的SQL
バインド変数を使用して、動的SQLが入力をコードではなくデータとして扱うようにします:

##### OracleでEXECUTE IMMEDIATEを使用
```sql
PROCEDURE AnotherSafeGetBalanceQuery(UserID varchar, Dept varchar)
          AS stmt VARCHAR(400); result NUMBER;
BEGIN
   stmt := 'SELECT balance FROM accounts_table WHERE user_ID = :1
            AND department = :2';
   EXECUTE IMMEDIATE stmt INTO result USING UserID, Dept;
   RETURN result;
END;
```

##### SQL Serverでsp_executesqlを使用
```sql
PROCEDURE SafeGetBalanceQuery(@UserID varchar(20), @Dept varchar(10)) AS BEGIN
   DECLARE @sql VARCHAR(200)
   SELECT @sql = 'SELECT balance FROM accounts_table WHERE '
                 + 'user_ID = @UID AND department = @DPT'
   EXEC sp_executesql @sql,
                      '@UID VARCHAR(20), @DPT VARCHAR(10)',
                      @UID=@UserID, @DPT=@Dept
END
```

### 重要なセキュリティ注意事項

- パラメータ化はサーバー側で行われることを確認してください。クライアント側のパラメータ化ライブラリは、文字列連結によって依然として安全でないクエリを構築する可能性があります
- パラメータ化されたクエリはSQLインジェクションに対する主要な防御策です
- 入力検証はSQLインジェクション防止ではなく、ビジネスロジック要件に焦点を当てるべきです
- ユーザー入力をSQLクエリ文字列に直接連結しないでください
- ストアドプロシージャ内の動的SQL構築にはバインド変数を使用してください
