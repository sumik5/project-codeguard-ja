---
description: Java向けJSON Web Tokenセキュリティ
languages:
- c
- java
- javascript
- typescript
- xml
- yaml
alwaysApply: false
---

## Java向けJSON Web Tokenセキュリティ

JavaアプリケーションでJWTを実装するための主要なセキュリティプラクティス。

### アルゴリズムセキュリティ

期待されるアルゴリズムを常に明示的に指定します：

```java
// 'none'アルゴリズム攻撃を防ぐ
JWTVerifier verifier = JWT.require(Algorithm.HMAC256(keyHMAC)).build();
DecodedJWT decodedToken = verifier.verify(token);
```

### トークンサイドジャッキング防止

認証成功後にトークンを作成するコード。

``` java
// HMAC鍵 - JVMメモリでの文字列としてのシリアル化と保存をブロック
private transient byte[] keyHMAC = ...;
// ランダムデータ生成器
private SecureRandom secureRandom = new SecureRandom();

...

//このユーザーのフィンガープリントを構成するランダム文字列を生成
byte[] randomFgp = new byte[50];
secureRandom.nextBytes(randomFgp);
String userFingerprint = DatatypeConverter.printHexBinary(randomFgp);

//強化されたCookieにフィンガープリントを追加 - 手動でCookieを追加。なぜなら
//SameSite属性はjavax.servlet.http.Cookieクラスでサポートされていないため
String fingerprintCookie = "__Secure-Fgp=" + userFingerprint
                           + "; SameSite=Strict; HttpOnly; Secure";
response.addHeader("Set-Cookie", fingerprintCookie);

//XSSがフィンガープリントを読み取り、期待されるCookieを自ら設定することを
//防ぐため、トークンに（生の値の代わりに）フィンガープリントハッシュを
//保存するため、フィンガープリントのSHA256ハッシュを計算
MessageDigest digest = MessageDigest.getInstance("SHA-256");
byte[] userFingerprintDigest = digest.digest(userFingerprint.getBytes("utf-8"));
String userFingerprintHash = DatatypeConverter.printHexBinary(userFingerprintDigest);

//15分間の有効期限とクライアントコンテキスト（フィンガープリント）情報を持つトークンを作成
Calendar c = Calendar.getInstance();
Date now = c.getTime();
c.add(Calendar.MINUTE, 15);
Date expirationDate = c.getTime();
Map<String, Object> headerClaims = new HashMap<>();
headerClaims.put("typ", "JWT");
String token = JWT.create().withSubject(login)
   .withExpiresAt(expirationDate)
   .withIssuer(this.issuerID)
   .withIssuedAt(now)
   .withNotBefore(now)
   .withClaim("userFingerprint", userFingerprintHash)
   .withHeader(headerClaims)
   .sign(Algorithm.HMAC256(this.keyHMAC));
```

トークンを検証するコード。

``` java
// HMAC鍵 - JVMメモリでの文字列としてのシリアル化と保存をブロック
private transient byte[] keyHMAC = ...;

...

//専用Cookieからユーザーフィンガープリントを取得
String userFingerprint = null;
if (request.getCookies() != null && request.getCookies().length > 0) {
 List<Cookie> cookies = Arrays.stream(request.getCookies()).collect(Collectors.toList());
 Optional<Cookie> cookie = cookies.stream().filter(c -> "__Secure-Fgp"
                                            .equals(c.getName())).findFirst();
 if (cookie.isPresent()) {
   userFingerprint = cookie.get().getValue();
 }
}

//トークンに保存されたフィンガープリントハッシュと比較するため、
//Cookie内で受信したフィンガープリントのSHA256ハッシュを計算
MessageDigest digest = MessageDigest.getInstance("SHA-256");
byte[] userFingerprintDigest = digest.digest(userFingerprint.getBytes("utf-8"));
String userFingerprintHash = DatatypeConverter.printHexBinary(userFingerprintDigest);

//トークンの検証コンテキストを作成
JWTVerifier verifier = JWT.require(Algorithm.HMAC256(keyHMAC))
                              .withIssuer(issuerID)
                              .withClaim("userFingerprint", userFingerprintHash)
                              .build();

//トークンを検証、検証が失敗すると例外がスローされます
DecodedJWT decodedToken = verifier.verify(token);
```


### トークン取り消し

ログアウト機能のためトークンブラックリストを実装：


トークンを拒否リストに追加し、トークンが取り消されたかチェックする担当コード。

``` java
/**
* トークンの取り消し（ログアウト）を処理します。
* 複数のインスタンスが取り消されたトークンをチェックできるようにし、
* 集中化されたDBレベルでのクリーンアップを可能にするためDBを使用します。
*/
public class TokenRevoker {

 /** DB接続 */
 @Resource("jdbc/storeDS")
 private DataSource storeDS;

 /**
  * 暗号化されたトークンのHEXエンコードされたダイジェストが
  * 取り消しテーブルに存在するか検証
  *
  * @param jwtInHex HEXエンコードされたトークン
  * @return 存在フラグ
  * @throws Exception DBとの通信中に問題が発生した場合
  */
 public boolean isTokenRevoked(String jwtInHex) throws Exception {
     boolean tokenIsPresent = false;
     if (jwtInHex != null && !jwtInHex.trim().isEmpty()) {
         //暗号化されたトークンをデコード
         byte[] cipheredToken = DatatypeConverter.parseHexBinary(jwtInHex);

         //暗号化されたトークンのSHA256を計算
         MessageDigest digest = MessageDigest.getInstance("SHA-256");
         byte[] cipheredTokenDigest = digest.digest(cipheredToken);
         String jwtTokenDigestInHex = DatatypeConverter.printHexBinary(cipheredTokenDigest);

         //DB内でHEXのトークンダイジェストを検索
         try (Connection con = this.storeDS.getConnection()) {
             String query = "select jwt_token_digest from revoked_token where jwt_token_digest = ?";
             try (PreparedStatement pStatement = con.prepareStatement(query)) {
                 pStatement.setString(1, jwtTokenDigestInHex);
                 try (ResultSet rSet = pStatement.executeQuery()) {
                     tokenIsPresent = rSet.next();
                 }
             }
         }
     }

     return tokenIsPresent;
 }


### 安全なクライアントストレージ

フィンガープリントバインディングを伴うsessionStorageにトークンを保存：

```javascript
// localStorageではなくsessionStorageに保存
sessionStorage.setItem("token", data.token);

// Bearerトークンとして送信
xhr.setRequestHeader("Authorization", "bearer " + token);
```

### 強力なシークレット

強力なHMACシークレットまたはRSA鍵を使用：
- HMACシークレット：最小64文字、暗号学的にランダム
- より良いセキュリティのため、HMACよりRSAまたはECDSAを優先
- ソースコードにシークレットを決してハードコードしない
