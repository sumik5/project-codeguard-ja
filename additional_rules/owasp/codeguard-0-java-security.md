---
description: Javaセキュリティベストプラクティス
languages:
- c
- java
- javascript
- typescript
- xml
- yaml
alwaysApply: false
---

## Javaセキュリティガイドライン

セキュアなJavaアプリケーション開発のための主要なセキュリティプラクティス。

### SQLインジェクション防止

SQLインジェクションを防ぐためパラメータ化クエリを使用します：

```java
// 安全 - パラメータを伴うPreparedStatement
String query = "select * from color where friendly_name = ?";
try (PreparedStatement pStatement = con.prepareStatement(query)) {
    pStatement.setString(1, userInput);
    try (ResultSet rSet = pStatement.executeQuery()) {
        // 結果を処理
    }
}
```

### JPAクエリセキュリティ

パラメータ化JPAクエリを使用します：

```java
// 安全 - 名前付きパラメータ
String queryPrototype = "select c from Color c where c.friendlyName = :colorName";
Query queryObject = entityManager.createQuery(queryPrototype);
Color c = (Color) queryObject.setParameter("colorName", userInput).getSingleResult();
```

### XSS防止

入力検証と出力エンコーディングを適用します：

```java
// 許可リストを使用した入力検証
if (!Pattern.matches("[a-zA-Z0-9\\s\\-]{1,50}", userInput)) {
    return false;
}

// 出力サニタイゼーション
PolicyFactory policy = new HtmlPolicyBuilder().allowElements("p", "strong").toFactory();
String safeOutput = policy.sanitize(outputToUser);
safeOutput = Encode.forHtml(safeOutput);
```

### セキュアロギング

ログインジェクションを防ぐためパラメータ化されたロギングを使用します：

```java
// 安全 - パラメータ化されたロギング
logger.warn("Login failed for user {}.", username);

// 避ける - 文字列連結
// logger.warn("Login failed for user " + username);
```

### 暗号化ベストプラクティス

信頼できる暗号化ライブラリとセキュアなアルゴリズムを使用します：

```java
// 適切なノンス管理を伴うAES-GCMを使用
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
GCMParameterSpec gcmParameterSpec = new GCMParameterSpec(128, nonce);
cipher.init(Cipher.ENCRYPT_MODE, secretKey, gcmParameterSpec);

// セキュアランダムノンスを生成
byte[] nonce = new byte[12];
SecureRandom.getInstanceStrong().nextBytes(nonce);
```

### 主要なセキュリティ要件

- 暗号化キーをソースコードにハードコーディングしません
- 可能な場合、Google Tinkまたは類似の信頼できる暗号化ライブラリを使用します
- カスタム暗号化実装の記述を避けます
- 適切なキーローテーションと管理を実装します
- すべての依存関係をセキュリティパッチで最新に保ちます
