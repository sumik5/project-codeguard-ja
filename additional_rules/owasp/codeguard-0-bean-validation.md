---
description: Bean Validationセキュリティベストプラクティス
languages:
- java
- xml
alwaysApply: false
---

セキュリティと保守性のために、宣言的で集中化されたバリデーションアプローチを使用することが重要です。Java Bean Validation標準（現Jakarta Validation）とその主要実装であるHibernate Validatorは、これを処理する強力な方法を提供します。

### Bean Validationを使用する理由

ビジネスレイヤー全体にバリデーションロジックを散在させる代わりに、ドメインモデル（「Bean」）に直接バリデーションルールを定義します。これにより、バリデーションロジックが一箇所に保たれ、一貫性があり管理しやすくなります。

### 1. プロジェクトのセットアップ

`pom.xml`にHibernate Validatorを追加します：

```xml
<dependency>
    <groupId>org.hibernate.validator</groupId>
    <artifactId>hibernate-validator</artifactId>
    <version>8.0.0.Final</version>
</dependency>
```

Spring Bootを使用している場合、`spring-boot-starter-web`依存関係に自動的にHibernate Validatorが含まれています。

### 2. Beanのアノテーション

モデルクラスのフィールドに直接標準バリデーションアノテーションを適用します。**機密フィールドには必ず@NotNull/@NotBlankと@Size制約を組み合わせてください。**

**例（`UserForm.java`）：**
```java
public class UserForm {

    @NotBlank @Size(min = 2, max = 50)
    private String name;

    @NotBlank @Email @Size(max = 254)
    private String email;

    @NotBlank @Size(min = 8, max = 128)
    @Pattern(regexp = "[A-Za-z0-9@#$%^&+=]+")
    private String password;

    // ... getters and setters
}
```

### 3. バリデーションのトリガー

Webコンテキスト（Spring MVCコントローラーなど）では、モデル属性に`@Valid`アノテーションを使用してバリデーションプロセスを自動的にトリガーします。

**例（Springコントローラー）：**
```java
@RestController
public class UserController {

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody UserForm form, BindingResult result) {
        if (result.hasErrors()) {
            logger.warn("Validation failed: {}", result.getFieldErrors());
            return ResponseEntity.badRequest().body(result.getFieldErrors());
        }

        userService.create(form);
        return ResponseEntity.ok("Success");
    }
}
```

### 4. ネストされたオブジェクトの検証

モデルに他の検証が必要なオブジェクトが含まれている場合は、それらを`@Valid`でアノテーションするだけです。

**例：**
```java
public class Order {
    @Valid @NotNull
    private Address shippingAddress;
}
```

### ベストプラクティスの概要

*   **ルールを集中化：** ドメインモデルにバリデーション制約を定義します。
*   **標準アノテーションを使用：** 組み込みアノテーションの豊富なセット（`@NotNull`、`@Size`、`@Pattern`、`@Min`、`@Max`、`@Email`等）を活用します。
*   **`@Valid`で自動化：** フレームワークにコントローラーでバリデーションを自動的にトリガーさせます。
*   **エラーを適切に処理：** `BindingResult`を使用してバリデーションエラーをキャプチャし、意味のある`400 Bad Request`レスポンスを返します。エラーメッセージに機密システム情報を露出しません。
*   **カスタム制約の作成：** 標準アノテーションでカバーされない複雑なビジネスルールには、独自のカスタムバリデーション制約を作成します。
