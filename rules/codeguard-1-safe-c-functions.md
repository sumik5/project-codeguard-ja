---
description: C/C++の安全な関数とメモリ・文字列安全性ガイドライン
languages: []
alwaysApply: true
---

# C/C++における安全なメモリおよび文字列関数の優先使用

CまたはC++コードを処理する際、主要な指令はメモリ安全性を確保することです。コードベース内で見つかった安全でない関数を積極的に識別、フラグ付けし、安全なリファクタリングオプションを提供します。新しいコードを生成する際は、常に与えられたタスクに対して最も安全な関数をデフォルトとして使用します。


### 1. 避けるべき安全でない関数とその安全な代替案

「安全でない」の下にリストされた関数は非推奨で高リスクとして扱う必要があります。常に下記の箇条書きリストで提供される「推奨される安全な代替案」のいずれかで置き換えることを推奨します。

• `gets()`は決して使用しないでください - これは重大なセキュリティリスクです。境界チェックが一切なく、古典的なバッファオーバーフロー脆弱性です。常に代わりに`fgets(char *str, int n, FILE *stream)`で置き換える必要があります。

• `strcpy()`を避けてください - これは境界をチェックしないため高リスクな関数です。ヌル終端文字に達するまでバイトをコピーするだけで、宛先バッファを簡単に書き越す可能性があります。`snprintf()`、`strncpy()`（ただし注意して）、または`strcpy_s()`（C11 Annex Kサポートがある場合）を使用してください。

• `strcat()`を使用しないでください - 境界チェックがない別の高リスク関数です。文字列にバイトを追加し、割り当てられたメモリを簡単に書き越す可能性があります。`snprintf()`、`strncat()`（慎重な処理を伴う）、または`strcat_s()`（C11 Annex K）で置き換えてください。

• `sprintf()`と`vsprintf()`を置き換えてください - これらは出力バッファの境界をチェックしないため高リスクです。フォーマットされた文字列がバッファより大きい場合、バッファオーバーフローが発生します。代わりに`snprintf()`、`snwprintf()`、または`vsprintf_s()`（C11 Annex K）を使用してください。

• `scanf()`ファミリーに注意してください - これは中リスクです。幅制限なしの`%s`フォーマット指定子はバッファオーバーフローを引き起こす可能性があります。以下を実行してください：
  1. `scanf("%127s", buffer)`のように幅指定子を使用
  2. さらに良い方法：`fgets()`で行を読み取り、`sscanf()`で解析

• `strtok()`を避けてください - これは再入可能でもスレッドセーフでもないため中リスクです。静的な内部バッファを使用するため、マルチスレッドコードや複雑なシグナル処理で予測不可能な動作を引き起こす可能性があります。代わりに`strtok_r()`（POSIX）または`strtok_s()`（C11 Annex K）を使用してください。

• `memcpy()`と`memmove()`を慎重に使用してください - これらは本質的に安全ではありませんが、サイズ引数を誤って計算したり適切に検証しなかった場合、バグの一般的な原因です。以下を実行してください：
  1. サイズ計算を再確認
  2. 利用可能な場合は`memcpy_s()`（C11 Annex K）を優先
  3. ソースとデスティネーションバッファがオーバーラップする可能性がある場合は`memmove()`を使用

### 2. 実行可能な実装ガイドライン

#### 新しいコード生成の場合：

- `gets()`、`strcpy()`、`strcat()`、または`sprintf()`を使用するコードを決して生成しないでください。

- 文字列のフォーマットと連結には、最も柔軟で安全なオプションであることが多いため、`snprintf()`をデフォルトとして使用してください。

- ファイルや標準入力から文字列入力を読み取る場合は、`fgets()`をデフォルトとして使用してください。


#### コード分析とリファクタリングの場合：

1. 識別：コードをスキャンし、「安全でない」列の関数のすべてのインスタンスにフラグを付けます。

2. リスクの説明：安全でない関数にフラグを付けるときは、特定の脆弱性の簡潔な説明を提供します。

    - _説明の例：_ `警告：'strcpy'関数は境界チェックを実行せず、ソース文字列がデスティネーションバッファより大きい場合にバッファオーバーフローを引き起こす可能性があります。これは一般的なセキュリティ脆弱性です。`

3. コンテキストに応じた置き換えの提供：あなたの提案は、周囲のコードのコンテキストを考慮したドロップイン可能な安全な置き換えでなければなりません。


#### コンパイラフラグの使用：

コンパイル時および実行時にバッファオーバーフロー脆弱性を捕捉するため、これらの保護的なコンパイラフラグを有効にします：

- スタック保護：スタックバッファオーバーフローを検出するため`-fstack-protector-all`または`-fstack-protector-strong`を使用
- Address Sanitizer：開発中にメモリエラーを捕捉するため`-fsanitize=address`を使用
- オブジェクトサイズチェック（OSC）：`strcpy`、`strcat`、`sprintf`などの関数でバッファオーバーフローの実行時チェックを有効にするため`-D_FORTIFY_SOURCE=2`を使用。これは上記で言及された多くの安全でない関数に境界チェックを追加します
- フォーマット文字列保護：フォーマット文字列脆弱性を捕捉するため`-Wformat -Wformat-security`を使用

### 3. リファクタリング例

あなたの提案は具体的で実行可能である必要があります。

例1：`strcpy`の置き換え

- 元の安全でないコード：

    ```
    char destination[64];
    strcpy(destination, source_string);
    ```

- 提案するリファクタリング：

    ```
    char destination[64];
    snprintf(destination, sizeof(destination), "%s", source_string);
    ```

- 説明：`'strcpy'を'snprintf'で置き換え、デスティネーションバッファに63文字とヌル終端文字以上が書き込まれないようにし、潜在的なバッファオーバーフローを防止しました。`


例2：`strncpy`使用の修正

`strncpy`関数は一般的ですが不完全な置き換えです。デスティネーションバッファをヌル終端しない可能性があります。これを使用する必要がある場合、または使用されているのを見る場合、正しい処理を強制する必要があります。

- 元の（潜在的に安全でない）`strncpy`：

    ```
    // これはstrlen(source) >= 10の場合安全ではありません
    char dest[10];
    strncpy(dest, source, sizeof(dest));
    ```

- 修正した提案：

    ```
    char dest[10];
    strncpy(dest, source, sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0';
    ```

- 説明：`'strncpy'に明示的なヌル終端を追加しました。'strncpy'関数は、ソースがデスティネーションバッファと同じ長さの場合、ヌル終端文字列を保証しません。この修正により、後続の文字列操作でバッファを超えた読み取りを防止します。`


例3：`scanf`のセキュア化

- 元の安全でないコード：

    ```
    char user_name[32];
    printf("Enter your name: ");
    scanf("%s", user_name);
    ```

- 提案するリファクタリング：

    ```
    char user_name[32];
    printf("Enter your name: ");
    if (fgets(user_name, sizeof(user_name), stdin)) {
        // オプション：fgetsから末尾の改行文字を削除
        user_name[strcspn(user_name, "\n")] = 0;
    }
    ```

- 説明：`'scanf("%s", ...)'を'fgets()'で置き換えてユーザー入力を読み取りました。'fgets'は入力をバッファサイズに制限するため安全で、バッファオーバーフローを防止します。元の'scanf'にはそのような保護がありませんでした。`


### メモリおよび文字列安全性ガイドライン

#### 安全でないメモリ関数 - 禁止
入力パラメータの境界をチェックしないこれらの安全でないメモリ関数を決して使用しないでください：

##### 禁止されたメモリ関数：
- `memcpy()` → `memcpy_s()`を使用
- `memset()` → `memset_s()`を使用
- `memmove()` → `memmove_s()`を使用
- `memcmp()` → `memcmp_s()`を使用
- `bzero()` → `memset_s()`を使用
- `memzero()` → `memset_s()`を使用

##### 安全なメモリ関数の置き換え：
```c
// 代わりに：memcpy(dest, src, count);
errno_t result = memcpy_s(dest, dest_size, src, count);
if (result != 0) {
// エラーを処理
}

// 代わりに：memset(dest, value, count);
errno_t result = memset_s(dest, dest_size, value, count);

// 代わりに：memmove(dest, src, count);
errno_t result = memmove_s(dest, dest_size, src, count);

// 代わりに：memcmp(s1, s2, count);
int indicator;
errno_t result = memcmp_s(s1, s1max, s2, s2max, count, &indicator);
if (result == 0) {
// indicatorは比較結果を含む：<0、0、または>0
}
```

#### 安全でない文字列関数 - 禁止
バッファオーバーフローを引き起こす可能性があるこれらの安全でない文字列関数を決して使用しないでください：

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

// フォーマット文字列（常にサイズ境界バージョンを使用）
int snprintf(char *s, size_t n, const char *format, ...);
```

#### 実装例：

##### 安全な文字列コピーパターン：
```c
// 悪い - 安全でない
char dest[256];
strcpy(dest, src); // バッファオーバーフローリスク！

// 良い - 安全
char dest[256];
errno_t result = strcpy_s(dest, sizeof(dest), src);
if (result != 0) {
// エラーを処理：srcが長すぎるか無効なパラメータ
EWLC_LOG_ERROR("文字列コピー失敗：%d", result);
return ERROR;
}
```

##### 安全な文字列連結パターン：
```c
// 悪い - 安全でない
char buffer[256] = "prefix_";
strcat(buffer, suffix); // バッファオーバーフローリスク！

// 良い - 安全
char buffer[256] = "prefix_";
errno_t result = strcat_s(buffer, sizeof(buffer), suffix);
if (result != 0) {
EWLC_LOG_ERROR("文字列連結失敗：%d", result);
return ERROR;
}
```

##### 安全なメモリコピーパターン：
```c
// 悪い - 安全でない
memcpy(dest, src, size); // 境界チェックなし！

// 良い - 安全
errno_t result = memcpy_s(dest, dest_max_size, src, size);
if (result != 0) {
EWLC_LOG_ERROR("メモリコピー失敗：%d", result);
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

#### メモリおよび文字列安全性コードレビューチェックリスト：

##### コードレビュー前（開発者）：
- [ ] 安全でないメモリ関数なし（`memcpy`、`memset`、`memmove`、`memcmp`、`bzero`）
- [ ] 安全でない文字列関数なし（`strcpy`、`strcat`、`strcmp`、`strlen`、`sprintf`、`strstr`、`strtok`）
- [ ] すべてのメモリ操作で適切なサイズパラメータを持つ`*_s()`バリアントを使用
- [ ] バッファサイズは`sizeof()`または既知の制限を使用して正しく計算
- [ ] 変更される可能性のあるハードコードされたバッファサイズなし

##### コードレビュー（レビュアー）：
- [ ] メモリ安全性：すべてのメモリ操作で安全なバリアントを使用していることを確認
- [ ] バッファ境界：デスティネーションバッファサイズが適切に指定されていることを確認
- [ ] エラー処理：すべての`errno_t`戻り値が処理されていることをチェック
- [ ] サイズパラメータ：`rsize_t dmax`パラメータが正しいことを検証
- [ ] 文字列終端：文字列が適切にヌル終端されていることを確認
- [ ] 長さ検証：操作前にソース文字列の長さが検証されていることをチェック

##### 静的解析統合：
- [ ] 安全でない関数使用に対するコンパイラ警告を有効化
- [ ] 静的解析ツールを使用して安全でない関数呼び出しを検出
- [ ] 安全でない関数警告をエラーとして扱うようビルドシステムを設定
- [ ] 禁止された関数をスキャンするプリコミットフックを追加

#### 一般的な落とし穴と解決策：

##### 落とし穴1：誤ったサイズパラメータ
```c
// 誤り - デスティネーションサイズの代わりにソースサイズを使用
strcpy_s(dest, strlen(src), src); // 誤り！

// 正しい - デスティネーションバッファサイズを使用
strcpy_s(dest, sizeof(dest), src); // 正しい
```

##### 落とし穴2：戻り値の無視
```c
// 誤り - 潜在的なエラーを無視
strcpy_s(dest, sizeof(dest), src); // エラーがチェックされていない

// 正しい - 戻り値をチェック
if (strcpy_s(dest, sizeof(dest), src) != 0) {
// エラーを適切に処理
}
```

##### 落とし穴3：ポインタでsizeof()を使用
```c
// 誤り - バッファではなくポインタのsizeof
void func(char *buffer) {
strcpy_s(buffer, sizeof(buffer), src); // sizeof(char*) = 8！
}

// 正しい - バッファサイズをパラメータとして渡す
void func(char *buffer, size_t buffer_size) {
strcpy_s(buffer, buffer_size, src);
}
```

このルールがどのように適用され、なぜ適用されたかを常に説明する必要があります。
