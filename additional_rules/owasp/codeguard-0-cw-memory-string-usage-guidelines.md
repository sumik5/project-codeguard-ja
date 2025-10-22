---
description: メモリと文字列安全性ガイドライン
languages:
- c
alwaysApply: false
---

### メモリと文字列安全性ガイドライン

#### 安全でないメモリ関数 - 禁止
**入力パラメータ境界をチェックしない以下の安全でないメモリ関数を決して使用しないでください：**

##### 禁止されたメモリ関数：
- `memcpy()` → `memcpy_s()`を使用
- `memset()` → `memset_s()`を使用
- `memmove()` → `memmove_s()`を使用
- `memcmp()` → `memcmp_s()`を使用
- `bzero()` → `memset_s()`を使用
- `memzero()` → `memset_s()`を使用

##### 安全なメモリ関数の置き換え：
```c
// 代わりに: memcpy(dest, src, count);
errno_t result = memcpy_s(dest, dest_size, src, count);
if (result != 0) {
// エラーを処理
}

// 代わりに: memset(dest, value, count);
errno_t result = memset_s(dest, dest_size, value, count);

// 代わりに: memmove(dest, src, count);
errno_t result = memmove_s(dest, dest_size, src, count);

// 代わりに: memcmp(s1, s2, count);
int indicator;
errno_t result = memcmp_s(s1, s1max, s2, s2max, count, &indicator);
if (result == 0) {
// indicatorには比較結果が含まれる: <0, 0, または >0
}
```

#### 安全でない文字列関数 - 禁止
**バッファオーバーフローを引き起こす可能性がある以下の安全でない文字列関数を決して使用しないでください：**

##### 禁止された文字列関数：
- `strstr()` → `strstr_s()`を使用
- `strtok()` → `strtok_s()`を使用
- `strcpy()` → `strcpy_s()`を使用
- `strcmp()` → `strcmp_s()`を使用
- `strlen()` → `strnlen_s()`を使用
- `strcat()` → `strcat_s()`を使用
- `sprintf()` → `snprintf()`を使用

##### 安全な文字列関数の置き換え：
```c
// 文字列検索
errno_t strstr_s(char *dest, rsize_t dmax, const char *src, rsize_t slen, char **substring);

// 文字列トークン化
char *strtok_s(char *dest, rsize_t *dmax, const char *src, char **ptr);

// 文字列コピー
errno_t strcpy_s(char *dest, rsize_t dmax, const char *src);

// 文字列比較
errno_t strcmp_s(const char *dest, rsize_t dmax, const char *src, int *indicator);

// 文字列長（境界付き）
rsize_t strnlen_s(const char *str, rsize_t strsz);

// 文字列連結
errno_t strcat_s(char *dest, rsize_t dmax, const char *src);

// フォーマット済み文字列（常にサイズ境界付きバージョンを使用）
int snprintf(char *s, size_t n, const char *format, ...);
```

#### 実装例：

##### 安全な文字列コピーパターン：
```c
// 悪い - 安全でない
char dest[256];
strcpy(dest, src); // バッファオーバーフローリスク!

// 良い - 安全
char dest[256];
errno_t result = strcpy_s(dest, sizeof(dest), src);
if (result != 0) {
// エラーを処理: srcが長すぎるか無効なパラメータ
EWLC_LOG_ERROR("String copy failed: %d", result);
return ERROR;
}
```

##### 安全な文字列連結パターン：
```c
// 悪い - 安全でない
char buffer[256] = "prefix_";
strcat(buffer, suffix); // バッファオーバーフローリスク!

// 良い - 安全
char buffer[256] = "prefix_";
errno_t result = strcat_s(buffer, sizeof(buffer), suffix);
if (result != 0) {
EWLC_LOG_ERROR("String concatenation failed: %d", result);
return ERROR;
}
```

##### 安全なメモリコピーパターン：
```c
// 悪い - 安全でない
memcpy(dest, src, size); // 境界チェックなし!

// 良い - 安全
errno_t result = memcpy_s(dest, dest_max_size, src, size);
if (result != 0) {
EWLC_LOG_ERROR("Memory copy failed: %d", result);
return ERROR;
}
```

##### 安全な文字列トークン化パターン：
```c
// 悪い - 安全でない
char *token = strtok(str, delim); // 元の文字列を安全でない方法で変更

// 良い - 安全
char *next_token = NULL;
rsize_t str_max = strnlen_s(str, MAX_STRING_SIZE);
char *token = strtok_s(str, &str_max, delim, &next_token);
while (token != NULL) {
// トークンを処理
token = strtok_s(NULL, &str_max, delim, &next_token);
}
```

#### メモリと文字列安全性コードレビューチェックリスト：

##### コードレビュー前（開発者）：
- [ ] 安全でないメモリ関数なし（`memcpy`、`memset`、`memmove`、`memcmp`、`bzero`）
- [ ] 安全でない文字列関数なし（`strcpy`、`strcat`、`strcmp`、`strlen`、`sprintf`、`strstr`、`strtok`）
- [ ] すべてのメモリ操作は適切なサイズパラメータを持つ`*_s()`バリアントを使用
- [ ] バッファサイズは`sizeof()`または既知の制限を使用して正しく計算
- [ ] 変更される可能性のあるハードコードされたバッファサイズなし

##### コードレビュー（レビュー担当者）：
- [ ] **メモリ安全性**: すべてのメモリ操作が安全なバリアントを使用することを確認
- [ ] **バッファ境界**: 宛先バッファサイズが適切に指定されていることを確認
- [ ] **エラーハンドリング**: すべての`errno_t`戻り値が処理されていることをチェック
- [ ] **サイズパラメータ**: `rsize_t dmax`パラメータが正しいことを検証
- [ ] **文字列終端**: 文字列が適切にnull終端されていることを確保
- [ ] **長さ検証**: 操作前にソース文字列の長さが検証されていることをチェック

##### 静的分析統合：
- [ ] 安全でない関数使用のコンパイラ警告を有効化
- [ ] 静的分析ツールを使用して安全でない関数呼び出しを検出
- [ ] 安全でない関数警告をエラーとして扱うようにビルドシステムを設定
- [ ] 禁止された関数をスキャンするプリコミットフックを追加

#### 一般的な落とし穴と解決策：

##### 落とし穴1: 間違ったサイズパラメータ
```c
// 間違い - 宛先サイズの代わりにソースサイズを使用
strcpy_s(dest, strlen(src), src); // 間違い!

// 正しい - 宛先バッファサイズを使用
strcpy_s(dest, sizeof(dest), src); // 正しい
```

##### 落とし穴2: 戻り値を無視
```c
// 間違い - 潜在的なエラーを無視
strcpy_s(dest, sizeof(dest), src); // エラーがチェックされていない

// 正しい - 戻り値をチェック
if (strcpy_s(dest, sizeof(dest), src) != 0) {
// エラーを適切に処理
}
```

##### 落とし穴3: ポインタでsizeof()を使用
```c
// 間違い - バッファではなくポインタのsizeof
void func(char *buffer) {
strcpy_s(buffer, sizeof(buffer), src); // sizeof(char*) = 8!
}

// 正しい - バッファサイズをパラメータとして渡す
void func(char *buffer, size_t buffer_size) {
strcpy_s(buffer, buffer_size, src);
}
```
