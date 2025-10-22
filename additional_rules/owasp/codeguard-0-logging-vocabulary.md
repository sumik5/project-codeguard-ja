---
description: 標準化されたセキュリティイベントロギング用語
languages:
- c
- go
- java
- javascript
- kotlin
- php
- python
- ruby
- swift
- typescript
alwaysApply: false
---

## セキュリティイベントロギング用語ガイドライン

監視、アラート、インシデント対応を改善するためのセキュリティイベントロギングの標準化された用語。

### 標準イベントフォーマット

注意：すべての日付は、最大の移植性を確保するためUTCオフセットを伴うISO 8601形式でログに記録する必要があります

```json
{
    "datetime": "2021-01-01T01:01:01-0700",
    "appid": "foobar.netportal_auth",
    "event": "AUTHN_login_success:joebob1",
    "level": "INFO",
    "description": "User joebob1 login successfully",
    "useragent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "source_ip": "165.225.50.94",
    "host_ip": "10.12.7.9",
    "hostname": "portalauth.foobar.com",
    "protocol": "https",
    "port": "440",
    "request_uri": "/api/v2/auth/",
    "request_method": "POST",
    "region": "AWS-US-WEST-2",
    "geo": "USA"
}
```

### 認証イベント [AUTHN]

authn_login_success[:userid] - ログイン成功（レベル：INFO）
authn_login_successafterfail[:userid,retries] - 以前の失敗後のログイン成功（レベル：INFO）
authn_login_fail[:userid] - ログイン試行失敗（レベル：WARN）
authn_login_fail_max[:userid,maxlimit] - 最大失敗回数到達（レベル：WARN）
authn_login_lock[:userid,reason] - アカウントロック（理由：maxretries、suspicious、customer、other）（レベル：WARN）
authn_password_change[:userid] - パスワード変更成功（レベル：INFO）
authn_password_change_fail[:userid] - パスワード変更失敗（レベル：CRITICAL）
authn_impossible_travel[:userid,region1,region2] - ユーザーが同時に離れた場所に（レベル：CRITICAL）
authn_token_created[:userid,entitlements] - サービストークン作成（レベル：INFO）
authn_token_revoked[:userid,tokenid] - トークン失効（レベル：INFO）
authn_token_reuse[:userid,tokenid] - 失効済みトークンの再利用試行（レベル：CRITICAL）
authn_token_delete[:appid] - トークン削除（レベル：WARN）

### 認可イベント [AUTHZ]

authz_fail[:userid,resource] - 不正アクセス試行（レベル：CRITICAL）
authz_change[:userid,from,to] - ユーザー権限変更（レベル：WARN）
authz_admin[:userid,event] - すべての特権ユーザー活動（レベル：WARN）

### 暗号化/復号化イベント [CRYPT]

crypt_decrypt_fail[userid] - 復号化失敗（レベル：WARN）
crypt_encrypt_fail[userid] - 暗号化失敗（レベル：WARN）

### 過度な使用イベント [EXCESS]

excess_rate_limit_exceeded[userid,max] - レート制限超過（レベル：WARN）

### ファイルアップロードイベント [UPLOAD]

upload_complete[userid,filename,type] - ファイルアップロード完了（レベル：INFO）
upload_stored[filename,from,to] - 新しい名前/場所でファイル保存（レベル：INFO）
upload_validation[filename,(virusscan|imagemagick|...):(FAILED|incomplete|passed)] - ファイル検証結果（レベル：INFO|CRITICAL）
upload_delete[userid,fileid] - ファイル削除（レベル：INFO）

### 入力検証イベント [INPUT]

input_validation_fail:[(fieldone,fieldtwo...),userid] - サーバー側検証失敗（レベル：WARN）

### 悪意のある振る舞いイベント [MALICIOUS]

malicious_excess_404:[userid|IP,useragent] - フォースブラウジングを示す過度の404（レベル：WARN）
malicious_extraneous:[userid|IP,inputname,useragent] - 予期しない入力データ送信（レベル：CRITICAL）
malicious_attack_tool:[userid|IP,toolname,useragent] - 既知の攻撃ツール検出（レベル：CRITICAL）
malicious_cors:[userid|IP,useragent,referer] - 違法なクロスオリジンリクエスト（レベル：CRITICAL）
malicious_direct_reference:[userid|IP,useragent] - 直接オブジェクト参照試行（レベル：CRITICAL）

### 権限変更イベント [PRIVILEGE]

privilege_permissions_changed:[userid,file|object,fromlevel,tolevel] - オブジェクト権限変更（レベル：WARN）

### 機密データイベント [DATA]

sensitive_create:[userid,file|object] - 機密データ作成（レベル：WARN）
sensitive_read:[userid,file|object] - 機密データアクセス（レベル：WARN）
sensitive_update:[userid,file|object] - 機密データ変更（レベル：WARN）
sensitive_delete:[userid,file|object] - 機密データ削除マーク（レベル：WARN）

### シーケンスエラーイベント [SEQUENCE]

sequence_fail:[userid] - ビジネスロジックフローバイパス（レベル：CRITICAL）

### セッション管理イベント [SESSION]

session_created:[userid] - 新しい認証済みセッション（レベル：INFO）
session_renewed:[userid] - 有効期限警告後のセッション延長（レベル：INFO）
session_expired:[userid,reason] - セッション期限切れ（理由：logout、timeout、revoked）（レベル：INFO）
session_use_after_expire:[userid] - 期限切れセッション使用試行（レベル：CRITICAL）

### システムイベント [SYS]

sys_startup:[userid] - システム起動（レベル：WARN）
sys_shutdown:[userid] - システムシャットダウン（レベル：WARN）
sys_restart:[userid] - システム再起動（レベル：WARN）
sys_crash[:reason] - システムクラッシュ（レベル：WARN）
sys_monitor_disabled:[userid,monitor] - セキュリティ監視無効化（レベル：WARN）
sys_monitor_enabled:[userid,monitor] - セキュリティ監視有効化（レベル：WARN）

### ユーザー管理イベント [USER]

user_created:[userid,newuserid,attributes[one,two,three]] - 新規ユーザー作成（レベル：WARN）
user_updated:[userid,onuserid,attributes[one,two,three]] - ユーザーアカウント更新（レベル：WARN）
user_archived:[userid,onuserid] - ユーザーアカウントアーカイブ（レベル：WARN）
user_deleted:[userid,onuserid] - ユーザーアカウント削除（レベル：WARN）

### データ除外

機密情報をログに記録しません：プライベートまたは秘密情報、ソースコード、キー、証明書、認証パスワード、セッション識別値、アクセストークン、機密個人データ、PII、データベース接続文字列、暗号化キー、銀行口座または支払いカードデータ、商業上機密情報。

### 実装要件

- すべてのタイムスタンプにUTCオフセットを伴うISO 8601形式を使用
- 相関のためアプリケーション識別子（appid）を含める
- 一貫した深刻度レベル（INFO、WARN、CRITICAL）を適用
- 関連コンテキスト（IPアドレス、ユーザーエージェント、リクエスト詳細）を含める
- ユーザー情報をログに記録する際はデータプライバシー規制を考慮
- イベントタイプ後にログに記録されるフィールドは、ビジネスニーズとデータスチュワードシップ責任に基づいてオプションと見なされる必要があります
