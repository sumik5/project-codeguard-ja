---
description: LDAPインジェクションの防止
languages:
- c
- go
- java
- javascript
- php
- python
- ruby
- typescript
- xml
- yaml
alwaysApply: false
---

## LDAPインジェクションの防止ガイドライン

ディレクトリサービスを使用するアプリケーションでLDAPインジェクション脆弱性を防ぐための必須プラクティス。

### LDAPインジェクションの理解

LDAPインジェクションは、信頼されていないユーザー入力が不適切にLDAPクエリに組み込まれることで発生し、攻撃者が認証をバイパスしたり、認可されていないデータにアクセスしたり、ディレクトリ情報を変更したりする可能性があります。

インジェクションに脆弱な2つの主要コンポーネント：
- **識別名（DN）**：`cn=Richard Feynman, ou=Physics Department, dc=Caltech, dc=edu`のような一意の識別子
- **検索フィルター**：ポーランド記法でブール論理を使用するクエリ条件

### 主要な防御策：適切なエスケープ

#### 識別名（DN）のエスケープ

DNでエスケープする必要がある文字：`\ # + < > , ; " =`および先頭または末尾のスペース

DNで許可される文字（エスケープ不要）：`* ( ) . & - _ [ ] ` ~ | @ $ % ^ ? : { } ! '`

#### 検索フィルターのエスケープ

検索フィルターでエスケープする必要がある文字：`* ( ) \ NUL`

### 安全なJavaの例

元のOWASPドキュメントでは、この許可リスト検証アプローチを提供しています：

```java
// String userSN = "Sherlock Holmes"; // Valid
// String userPassword = "secret2"; // Valid
// ... beginning of LDAPInjection.searchRecord()...
sc.setSearchScope(SearchControls.SUBTREE_SCOPE);
String base = "dc=example,dc=com";

if (!userSN.matches("[\\w\\s]*") || !userPassword.matches("[\\w]*")) {
 throw new IllegalArgumentException("Invalid input");
}

String filter = "(&(sn = " + userSN + ")(userPassword=" + userPassword + "))";
// ... remainder of LDAPInjection.searchRecord()...
```

### 安全な.NETエンコーディング

.NET AntiXSS（現在はEncoderクラス）のLDAPエンコーディング関数を使用：
- `Encoder.LdapFilterEncode(string)` - RFC4515に従ってエンコード
- `Encoder.LdapDistinguishedNameEncode(string)` - RFC2253に従ってエンコード
- `LdapDistinguishedNameEncode(string, bool, bool)` - オプションの初期/最終文字エスケープ付き

### フレームワークベースの保護

LDAPインジェクションから自動的に保護するフレームワークを使用：
- **Java**：`encodeForLDAP(String)`および`encodeForDN(String)`を持つOWASP ESAPI
- **.NET**：LINQ to LDAP（.NET Framework 4.5以前）は自動的なLDAPエンコーディングを提供

### 追加の防御策

#### 最小権限
- LDAPバインディングアカウントに割り当てられる権限を最小化
- 可能な場合は読み取り専用アカウントを使用
- アプリケーション接続には管理者アカウントを避ける

#### バインド認証
- 検証と認可チェックを追加するため、バインド認証を使用してLDAPを設定
- 匿名接続と未認証バインドを防止

#### 許可リスト入力検証
- LDAPクエリ構築前に既知の安全な文字に対して入力を検証
- 検証前にユーザー入力を正規化
- 機密データをサニタイズした形式で保存

### 主要なセキュリティ要件

- LDAPクエリに組み込む前に、信頼されていないデータを常にエスケープ
- コンテキストに適したエスケープを使用（DN vs 検索フィルター）
- 許可リストを使用した包括的な入力検証を実装
- カスタムエスケープではなく確立されたセキュリティライブラリを使用
- LDAP接続に最小権限の原則を適用
- バイパス攻撃を防ぐための適切な認証メカニズムを有効化