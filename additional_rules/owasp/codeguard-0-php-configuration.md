---
description: PHPセキュア設定
languages:
- php
alwaysApply: false
---

## PHPセキュア設定ガイドライン

一般的な脆弱性からPHPアプリケーションを堅牢化するためのPHP設定の重要なセキュリティ設定。

### PHPバージョン管理

サポートされているバージョンのPHPを実行します。この記事執筆時点では、8.1がPHPからセキュリティサポートを受けている最も古いバージョンですが、ディストリビューションベンダーは多くの場合延長サポートを提供します。

### エラーハンドリング設定

エラーを確実にログに記録しながら情報開示を防ぐため、適切なエラーハンドリングを設定します：

```ini
expose_php              = Off
error_reporting         = E_ALL
display_errors          = Off
display_startup_errors  = Off
log_errors              = On
error_log               = /valid_path/PHP-logs/php_error.log
ignore_repeated_errors  = Off
```

本番サーバーでは`display_errors`を`Off`に保ち、ログを頻繁に監視します。

### 一般的なセキュリティ設定

```ini
doc_root                = /path/DocumentRoot/PHP-scripts/
open_basedir            = /path/DocumentRoot/PHP-scripts/
include_path            = /path/PHP-pear/
extension_dir           = /path/PHP-extensions/
mime_magic.magicfile    = /path/PHP-magic.mime
allow_url_fopen         = Off
allow_url_include       = Off
variables_order         = "GPCS"
allow_webdav_methods    = Off
session.gc_maxlifetime  = 600
```

`allow_url_*`はLFIが簡単にRFIにエスカレートすることを防ぎます。

### ファイルアップロード処理

```ini
file_uploads            = On
upload_tmp_dir          = /path/PHP-uploads/
upload_max_filesize     = 2M
max_file_uploads        = 2
```

アプリケーションがファイルアップロードを使用していない場合、`file_uploads`を`Off`にする必要があります。

### 実行可能ファイル処理

```ini
enable_dl               = Off
disable_functions       = system, exec, shell_exec, passthru, phpinfo, show_source, highlight_file, popen, proc_open, fopen_with_path, dbmopen, dbase_open, putenv, move_uploaded_file, chdir, mkdir, rmdir, chmod, rename, filepro, filepro_rowcount, filepro_retrieve, posix_mkfifo
disable_classes         =
```

これらは危険なPHP関数です。使用しないすべての関数を無効化します。

### セッション処理

セッション設定は、設定で集中すべき最も重要な値の一部です。`session.name`を新しいものに変更することは良いプラクティスです。

```ini
session.save_path                = /path/PHP-session/
session.name                     = myPHPSESSID
session.auto_start               = Off
session.use_trans_sid            = 0
session.cookie_domain            = full.qualified.domain.name
#session.cookie_path             = /application/path/
session.use_strict_mode          = 1
session.use_cookies              = 1
session.use_only_cookies         = 1
session.cookie_lifetime          = 14400 # 4時間
session.cookie_secure            = 1
session.cookie_httponly          = 1
session.cookie_samesite          = Strict
session.cache_expire             = 30
session.sid_length               = 256
session.sid_bits_per_character   = 6
```

### 追加のセキュリティ設定

```ini
session.referer_check   = /application/path
memory_limit            = 50M
post_max_size           = 20M
max_execution_time      = 60
report_memleaks         = On
html_errors             = Off
zend.exception_ignore_args = On
```

### Snuffleupagusによる高度な保護

SnuffleupagusはPHP 7以降のSuhosinの精神的後継で、モダンな機能を備えています。安定していると考えられ、本番環境で使用可能です。

### 実装概要

セキュアなPHP設定には以下が必要です：
- PHPバージョン情報の非表示（expose_php = Off）
- ロギングを有効化し本番環境で表示を無効化した適切なエラーハンドリング
- リモートファイルアクセスの無効化（allow_url_fopen/include = Off）
- アプリケーションニーズに基づく危険な関数の制限
- セキュアCookie設定によるセッション管理の堅牢化
- DoSを防ぐための適切なリソース制限設定
- Snuffleupagusなどのモダンセキュリティ拡張の使用

これらの設定プラクティスに従うことで、PHPアプリケーションの攻撃面を大幅に削減し、一般的な脆弱性から保護します。
