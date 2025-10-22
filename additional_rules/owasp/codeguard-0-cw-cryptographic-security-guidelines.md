---
description: 暗号化セキュリティガイドライン
languages:
- c
alwaysApply: false
---

### 暗号化セキュリティガイドライン

#### 非推奨SSL/暗号化API - 禁止
**これらの非推奨関数を決して使用しないでください。以下にリストされている代替APIを使用してください：**

##### 対称暗号化（AES）
- **非推奨**：`AES_encrypt()`、`AES_decrypt()`
- **代替**：EVP高レベルAPIを使用：
  ```c
  EVP_EncryptInit_ex()
  EVP_EncryptUpdate()
  EVP_EncryptFinal_ex()
  EVP_DecryptInit_ex()
  EVP_DecryptUpdate()
  EVP_DecryptFinal_ex()
  ```

##### RSA操作
- **非推奨**：`RSA_new()`、`RSA_up_ref()`、`RSA_free()`、`RSA_set0_crt_params()`、`RSA_get0_n()`
- **代替**：EVPキー管理APIを使用：
  ```c
  EVP_PKEY_new()
  EVP_PKEY_up_ref()
  EVP_PKEY_free()
  ```

##### ハッシュ関数
- **非推奨**：`SHA1_Init()`、`SHA1_Update()`、`SHA1_Final()`
- **代替**：EVPダイジェストAPIを使用：
  ```c
  EVP_DigestInit_ex()
  EVP_DigestUpdate()
  EVP_DigestFinal_ex()
  EVP_Q_digest()  // シンプルなワンショットハッシュ用
  ```

##### MAC操作
- **非推奨**：`CMAC_Init()`、`HMAC()`（特にSHA1との併用）
- **代替**：EVP MAC APIを使用：
  ```c
  EVP_Q_MAC()  // シンプルなMAC操作用
  ```

##### 鍵ラッピング
- **非推奨**：`AES_wrap_key()`、`AES_unwrap_key()`
- **代替**：EVP鍵ラッピングAPIを使用、またはEVP暗号化を使用して実装

##### その他の非推奨関数
- **非推奨**：`DSA_sign()`、`DH_check()`
- **代替**：DSAおよびDH操作用の対応するEVP APIを使用

#### 禁止される安全でないアルゴリズム - 厳格に禁止
**これらのアルゴリズムはいかなる形でも使用してはいけません：**

##### ハッシュアルゴリズム（禁止）
- MD2、MD4、MD5、SHA-0
- **理由**：暗号化的に破られており、衝突攻撃に脆弱
- **代わりに使用**：SHA-256、SHA-384、SHA-512

##### 対称暗号（禁止）
- RC2、RC4、Blowfish、DES、3DES
- **理由**：鍵サイズが弱い、既知の脆弱性
- **代わりに使用**：AES-128、AES-256、ChaCha20

##### 鍵交換（禁止）
- 静的RSA鍵交換
- 匿名Diffie-Hellman
- **理由**：前方秘匿性なし、中間者攻撃に脆弱
- **代わりに使用**：適切な検証を伴うECDHE、DHE

#### Broccoliプロジェクト固有の要件
- **SHA1を使用したHMAC()**：Broccoliプロジェクト要件により非推奨
- **代替**：SHA-256以上を使用したHMACを使用：
  ```c
  // SHA1を使用したHMAC()の代わりに
  EVP_Q_MAC(NULL, "HMAC", NULL, "SHA256", NULL, key, key_len, data, data_len, out, out_size, &out_len);
  ```

#### 安全な暗号化実装パターン
```c
// 例：安全なAES暗号化
EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
if (!ctx) handle_error();

if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key, iv) != 1)
    handle_error();

int len, ciphertext_len;
if (EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len) != 1)
    handle_error();
ciphertext_len = len;

if (EVP_EncryptFinal_ex(ctx, ciphertext + len, &len) != 1)
    handle_error();
ciphertext_len += len;

EVP_CIPHER_CTX_free(ctx);
```

#### コードレビューチェックリスト
- [ ] 非推奨のSSL/暗号化APIが使用されていない
- [ ] 禁止されたアルゴリズム（MD5、DES、RC4等）が使用されていない
- [ ] HMACはSHA-256以上を使用（SHA1ではない）
- [ ] すべての暗号化操作がEVP高レベルAPIを使用
- [ ] すべての暗号化操作に適切なエラー処理
- [ ] 使用後にキーマテリアルが適切にゼロ化されている
