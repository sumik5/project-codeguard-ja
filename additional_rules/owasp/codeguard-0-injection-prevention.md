---
description: インジェクション防止のベストプラクティス
languages:
- c
- go
- java
- javascript
- php
- powershell
- python
- ruby
- shell
- sql
- typescript
alwaysApply: false
---

## インジェクション防止ガイドライン

このルールは、複数の言語とインジェクションタイプにわたるインジェクション欠陥を防ぐための明確で実行可能なガイダンスを提供します。インジェクション欠陥は、信頼できないデータがコマンドまたはクエリの一部としてインタープリターに送信されるときに発生します。

### はじめに

インジェクション攻撃、特にSQLインジェクションは、残念ながら非常に一般的です。インジェクション欠陥は、アプリケーションが信頼できないデータをインタープリターに送信するときに発生します。インジェクション欠陥は非常に蔓延しており、特にレガシーコードで、SQLクエリ、LDAPクエリ、XPathクエリ、OSコマンド、プログラム引数などでよく見られます。

### SQLインジェクション防止

防御オプション1：プリペアドステートメント（パラメータ化クエリ付き）

安全なJava プリペアドステートメントの例：
```java
// これも本当に検証すべき
String custname = request.getParameter("customerName");
String query = "SELECT account_balance FROM user_data WHERE user_name = ?";
PreparedStatement pstmt = connection.prepareStatement( query );
pstmt.setString( 1, custname);
ResultSet results = pstmt.executeQuery( );
```

防御オプション2：ストアドプロシージャ

安全なJavaストアドプロシージャの例：
```java
// これも本当に検証すべき
String custname = request.getParameter("customerName");
try {
 CallableStatement cs = connection.prepareCall("{call sp_getAccountBalance(?)}");
 cs.setString(1, custname);
 ResultSet results = cs.executeQuery();
 // 結果セット処理...
} catch (SQLException se) {
 // ロギングとエラー処理...
}
```

防御オプション3：許可リスト入力検証

防御オプション4：すべてのユーザー提供入力のエスケープ

### LDAPインジェクション防止

正しいLDAPエンコーディング関数を使用してすべての変数をエスケープ

LDAPエスケープ用の安全なJavaの例：
```java
public String escapeDN (String name) {
 // RFC 2253とJNDI用の/文字から
 final char[] META_CHARS = {'+', '"', '<', '>', ';', '/'};
 String escapedStr = new String(name);
 // バックスラッシュはJavaとLDAP両方のエスケープ文字なので
 // 最初にエスケープ
 escapedStr = escapedStr.replaceAll("\\\\\\\\","\\\\\\\\");
 // 位置的文字 - RFC 2253を参照
 escapedStr = escapedStr.replaceAll("\^#","\\\\\\\\#");
 escapedStr = escapedStr.replaceAll("\^ | $","\\\\\\\\ ");
 for (int i=0 ; i < META_CHARS.length ; i++) {
        escapedStr = escapedStr.replaceAll("\\\\" +
                     META_CHARS[i],"\\\\\\\\" + META_CHARS[i]);
 }
 return escapedStr;
}
```

```java
public String escapeSearchFilter (String filter) {
 // RFC 2254から
 String escapedStr = new String(filter);
 escapedStr = escapedStr.replaceAll("\\\\\\\\","\\\\\\\\5c");
 escapedStr = escapedStr.replaceAll("\\\\\*","\\\\\\\\2a");
 escapedStr = escapedStr.replaceAll("\\\\(","\\\\\\\\28");
 escapedStr = escapedStr.replaceAll("\\\\)","\\\\\\\\29");
 escapedStr = escapedStr.replaceAll("\\\\" +
               Character.toString('\u0000'), "\\\\\\\\00");
 return escapedStr;
}
```

### オペレーティングシステムコマンド

ユーザー提供入力を組み込んだシステムコマンド呼び出しが避けられないと判断される場合、以下の2層の防御を使用すべきです：

1. パラメータ化 - 利用可能な場合、データとコマンド間の分離を自動的に強制する構造化されたメカニズムを使用
2. 入力検証 - コマンドと関連する引数の値は両方とも検証されるべき：
   - コマンドは許可されたコマンドのリストと照合して検証
   - 引数はポジティブまたは許可リスト入力検証を使用して検証
   - 許可リスト正規表現 - 許可される良い文字のリストと最大長を明示的に定義。`& | ; $ > < \` \ !`やホワイトスペースなどのメタ文字が正規表現の一部でないことを確認

正規表現の例：`^[a-z0-9]{3,10}$`

間違った使用法：
```java
ProcessBuilder b = new ProcessBuilder("C:\DoStuff.exe -arg1 -arg2");
```

正しい使用法：
```java
ProcessBuilder pb = new ProcessBuilder("TrustedCmd", "TrustedArg1", "TrustedArg2");
Map<String, String> env = pb.environment();
pb.directory(new File("TrustedDir"));
Process p = pb.start();
```

### インジェクション防止ルール

ルール#1（適切な入力検証を実行）
- 適切な入力検証を実行してください。適切な正規化を伴うポジティブまたは許可リスト入力検証が推奨されますが、多くのアプリケーションが入力に特殊文字を必要とするため、完全な防御ではありません。

ルール#2（安全なAPIを使用）
- 推奨オプションは、インタープリターの使用を完全に回避するか、パラメータ化インターフェースを提供する安全なAPIを使用することです。ストアドプロシージャなど、パラメータ化されているがバックグラウンドでインジェクションを導入する可能性のあるAPIに注意してください。

ルール#3（コンテキストに応じてユーザーデータをエスケープ）
- パラメータ化APIが利用できない場合、そのインタープリター用の特定のエスケープ構文を使用して特殊文字を注意深くエスケープする必要があります。
