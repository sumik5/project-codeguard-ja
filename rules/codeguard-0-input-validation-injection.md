---
description: 入力検証とインジェクション防御（SQL/LDAP/OS）、パラメータ化、プロトタイプ汚染
languages:
- c
- go
- html
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

## 入力検証・インジェクション防御

信頼できない入力を検証し、決してコードとして解釈されないようにする。SQL、LDAP、OSコマンド、テンプレート、JavaScriptランタイムオブジェクトグラフ全体でインジェクションを防止。

### 核心戦略
- 信頼境界で早期にポジティブ（許可リスト）検証と正規化を実施。
- すべての信頼できない入力をデータとして扱い、決してコードとしない。コードとデータを分離する安全なAPIを使用。
- クエリ/コマンドをパラメータ化；エスケープは最後の手段としてコンテキスト固有に使用。

### 検証プレイブック
- 構文検証：各フィールドでフォーマット、タイプ、範囲、長さを強制。
- 意味検証：ビジネスルールを強制（例：開始 ≤ 終了日、enum許可リスト）。
- 正規化：検証前にエンコーディングを正規化；完全な文字列を検証（正規表現アンカー ^$）；ReDoSに注意。
- 自由形式テキスト：文字クラス許可リストを定義；Unicodeを正規化；長さの境界を設定。
- ファイル：コンテンツタイプ（マジック）、サイズ上限、安全な拡張子で検証；サーバーでファイル名を生成；スキャン；Webルート外に保存。

### SQLインジェクション防止
- データアクセスの100%でプリペアドステートメントとパラメータ化クエリを使用。
- ストアドプロシージャ内の動的SQL構築にはbind変数を使用し、ユーザー入力をSQLに連結しない。
- 最小権限DBユーザーとビューを優先；アプリアカウントに管理者権限を付与しない。
- エスケープは脆弱で非推奨；パラメータ化が主要な防御策。

例（Java PreparedStatement）：
```java
String custname = request.getParameter("customerName");
String query = "SELECT account_balance FROM user_data WHERE user_name = ? ";
PreparedStatement pstmt = connection.prepareStatement( query );
pstmt.setString( 1, custname);
ResultSet results = pstmt.executeQuery( );
```

### LDAPインジェクション防止
- 常にコンテキストに適したエスケープを適用：
  - DNエスケープ：`\ # + < > , ; " =`と先頭/末尾スペース
  - フィルタエスケープ：`* ( ) \ NUL`
- クエリ構築前に許可リストで入力を検証；DN/フィルタエンコーダを提供するライブラリを使用。
- bind認証を使用した最小権限LDAP接続；アプリケーションクエリには匿名bindを避ける。

### OSコマンドインジェクション防御
- シェル実行の代わりに組み込みAPIを優先（例：`exec`よりライブラリ呼び出し）。
- 回避できない場合、コマンドと引数を分離する構造化実行を使用（例：ProcessBuilder）。シェルを呼び出さない。
- コマンドを厳格に許可リスト化し、許可リスト正規表現で引数を検証；メタ文字（& | ; $ > < ` \ ! ' " ( ) および必要に応じて空白）を除外。
- サポートされている場合は`--`を使用して引数を区切り、オプションインジェクションを防止。

例（Java ProcessBuilder）：
```java
ProcessBuilder pb = new ProcessBuilder("TrustedCmd", "Arg1", "Arg2");
Map<String,String> env = pb.environment();
pb.directory(new File("TrustedDir"));
Process p = pb.start();
```

### クエリパラメータ化ガイダンス
- プラットフォームのパラメータ化機能を使用（JDBC PreparedStatement、.NET SqlCommand、Ruby ActiveRecord bindパラメータ、PHP PDO、SQLx bind等）。
- ストアドプロシージャでは、パラメータをバインドすることを確認；プロシージャ内で文字列連結による動的SQLを構築しない。

### プロトタイプ汚染（JavaScript）
- 開発者はオブジェクトリテラルの代わりに`new Set()`または`new Map()`を使用すべき
- オブジェクトが必要な場合、継承されたプロトタイプを避けるため`Object.create(null)`または`{ __proto__: null }`で作成。
- 不変であるべきオブジェクトをフリーズまたはシール；多層防御としてNode `--disable-proto=delete`を検討。
- 安全でないディープマージユーティリティを避ける；許可リストでキーを検証し、`__proto__`、`constructor`、`prototype`をブロック。

### キャッシングとトランスポート
- 機密データを含むレスポンスに`Cache-Control: no-store`を適用；データフロー全体でHTTPSを強制。

### 実装チェックリスト
- 中央バリデータ：タイプ、範囲、長さ、enum；チェック前に正規化。
- SQLの100%パラメータ化カバレッジ；動的識別子は許可リストのみ。
- LDAP DN/フィルタエスケープを使用；クエリ前に入力を検証。
- 信頼できない入力にシェル呼び出しなし；回避できない場合、構造化exec + 許可リスト + 正規表現検証。
- JSオブジェクトグラフを強化：安全なコンストラクタ、ブロックされたプロトタイプパス、安全なマージユーティリティ。
- ファイルアップロードをコンテンツ、サイズ、拡張子で検証；Webルート外に保存してスキャン。

### テストプラン
- クエリ/コマンドでの文字列連結と危険なDOM/マージシンクの静的チェック。
- SQL/LDAP/OSインジェクションベクターのファジング；バリデータのエッジケースのユニットテスト。
- ブロックされたプロトタイプキーとディープマージ動作を実行するネガティブテスト。
