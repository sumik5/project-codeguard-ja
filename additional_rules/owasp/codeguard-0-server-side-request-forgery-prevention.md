---
description: サーバーサイドリクエストフォージェリ（SSRF）の防止
languages:
- c
- go
- java
- javascript
- php
- python
- ruby
- typescript
alwaysApply: false
---

## サーバーサイドリクエストフォージェリ（SSRF）の防止

送信リクエストを検証および制限することで、アプリケーションが内部/外部ネットワークとやり取りするために悪用されるSSRF攻撃を防止します。

### SSRF攻撃のコンテキスト

SSRF攻撃は、アプリケーションが以下を行う場合に発生します：
- 外部リソース（アバター、Webhook）のためにユーザー提供のURLを処理
- ユーザー制御データを使用して内部リクエストを実行
- 適切な検証なしでURLリダイレクトを処理

SSRFはHTTPに限定されません - 攻撃者はFTP、SMB、SMTPプロトコルや`file://`、`phar://`、`gopher://`、`data://`、`dict://`などのスキームを悪用できます。

### ケース1: 許可リストアプローチ（既知の信頼できる宛先）

アプリケーションが識別された信頼できるアプリケーションとのみ通信する場合、厳格な許可リストを使用します。

#### アプリケーション層の保護

バイパス試行を防ぐため、Webクライアントで常にHTTPリダイレクトを無効化します。

#### 文字列検証
シンプルな形式には正規表現を使用し、複雑な検証にはライブラリを使用します：

```java
//Regex validation for a data having a simple format
if(Pattern.matches("[a-zA-Z0-9\\s\\-]{1,50}", userInput)){
    //Continue the processing because the input data is valid
}else{
    //Stop the processing and reject the request
}
```

#### IPアドレス検証
IPフォーマットを検証し、エンコーディングバイパスを防ぐため、実績のあるライブラリを使用します：

- Java: Apache Commons Validatorの`InetAddressValidator.isValid()`
- .NET: SDKの`IPAddress.TryParse()`
- JavaScript: `ip-address`ライブラリ
- Ruby: SDKの`IPAddr`クラス

すべての信頼できるアプリケーションIP（IPv4とIPv6）の許可リストを作成します。許可リストとの厳密な文字列比較には、検証ライブラリからの出力値を使用します。

#### ドメイン名検証
DNS解決なしでフォーマットを検証するライブラリを使用します：

- Java: Apache Commons Validatorの`DomainValidator.isValid()`
- .NET: SDKの`Uri.CheckHostName()`
- JavaScript: `is-valid-domain`ライブラリ
- Python: `validators.domain`モジュール
- Ruby: 正規表現`^(((?!-))(xn--|_{1,1})?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*(xn--)?([a-z0-9][a-z0-9\-]{0,60}|[a-z0-9-]{1,30}\.[a-z]{2,})$`を使用

DNS Pinning攻撃に対して許可リストドメインを監視 - ドメインがローカル/内部IPアドレスに解決された場合にアラートを発行します。

#### URL処理
ユーザーから完全なURLを受け入れないでください。URLは検証が困難で、パーサーが悪用される可能性があります。検証済みのIPアドレスまたはドメイン名のみを受け入れます。

#### ネットワーク層の保護
- ファイアウォールを使用して、アプリケーションのネットワークアクセスを必要な宛先のみに制限
- 不正な呼び出しをネットワークレベルでブロックするためにネットワークセグメンテーションを実装
- 正当なフローを定義し、それ以外をすべてブロック

### ケース2: 動的な外部宛先（ブロックリストアプローチ）

アプリケーションが任意の外部リソース（Webhook）にアクセスする必要がある場合、ブロックリスト検証を使用します。

#### 検証フロー
1. ケース1のライブラリを使用して入力フォーマットを検証
2. IPアドレスの場合：パブリックであることを確認（プライベート、localhost、リンクローカルではない）
3. ドメインの場合：
   - 内部名のみを解決する内部DNSリゾルバを使用して外部であることを確認
   - ドメインをIPに解決し、返されたすべてのアドレスがパブリックであることを検証
4. 許可リストを使用してHTTP/HTTPSのみにプロトコルを制限
5. セキュアトークンによる正当なリクエストの証明を要求

#### セキュアトークン要件
- ターゲットアプリケーションがランダムな20文字の英数字トークンを生成
- `[a-z]{1,10}`文字のみを使用する名前のPOSTパラメータとしてトークンを渡す
- エンドポイントはHTTP POSTリクエストのみを受け入れる
- 検証済み情報のみを使用してリクエストを構築

#### Python監視スクリプトの例
DNS Pinningのために許可リストドメインを監視：

```python
# Dependencies: pip install ipaddress dnspython
import ipaddress
import dns.resolver

# Configure the allowlist to check
DOMAINS_ALLOWLIST = ["owasp.org", "labslinux"]

# Configure the DNS resolver to use for all DNS queries
DNS_RESOLVER = dns.resolver.Resolver()
DNS_RESOLVER.nameservers = ["1.1.1.1"]

def verify_dns_records(domain, records, type):
    """
    Verify if one of the DNS records resolve to a non public IP address.
    Return a boolean indicating if any error has been detected.
    """
    error_detected = False
    if records is not None:
        for record in records:
            value = record.to_text().strip()
            try:
                ip = ipaddress.ip_address(value)
                # See https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address.is_global
                if not ip.is_global:
                    print("[!] DNS record type '%s' for domain name '%s' resolve to a non public IP address '%s'!" % (type, domain, value))
                    error_detected = True
            except ValueError:
                error_detected = True
                print("[!] '%s' is not valid IP address!" % value)
    return error_detected

def check():
    """
    Perform the check of the allowlist of domains.
    Return a boolean indicating if any error has been detected.
    """
    error_detected = False
    for domain in DOMAINS_ALLOWLIST:
        # Get the IPs of the current domain
        # See https://en.wikipedia.org/wiki/List_of_DNS_record_types
        try:
            # A = IPv4 address record
            ip_v4_records = DNS_RESOLVER.query(domain, "A")
        except Exception as e:
            ip_v4_records = None
            print("[i] Cannot get A record for domain '%s': %s\n" % (domain,e))
        try:
            # AAAA = IPv6 address record
            ip_v6_records = DNS_RESOLVER.query(domain, "AAAA")
        except Exception as e:
            ip_v6_records = None
            print("[i] Cannot get AAAA record for domain '%s': %s\n" % (domain,e))
        # Verify the IPs obtained
        if verify_dns_records(domain, ip_v4_records, "A") or verify_dns_records(domain, ip_v6_records, "AAAA"):
            error_detected = True
    return error_detected

if __name__== "__main__":
    if check():
        exit(1)
    else:
        exit(0)
```

### クラウド固有の保護

#### AWS IMDSv2
クラウド環境では、SSRFはメタデータサービスをターゲットとして認証情報を盗みます。IMDSv2に移行し、AWS Instance Metadata ServiceへのSSRFアクセスに対する追加保護のためにIMDSv1を無効化します。

### 必須の実装ガイドライン

1. ユーザーから生のURLを受け入れない - IPアドレスまたはドメイン名のみを検証
2. エンコーディングバイパスを防ぐため、確立されたライブラリをIP/ドメイン検証に使用
3. 信頼できる宛先に対して、大文字小文字を区別する完全一致の厳格な許可リストを実装
4. すべての送信HTTPクライアントでHTTPリダイレクトを無効化
5. 動的な宛先の場合、プライベート/内部IP範囲をブロックし、DNS解決を検証
6. プロトコルをHTTP/HTTPSのみに制限
7. リクエスト正当性検証のためにセキュアトークンを要求
8. ファイアウォールとセグメンテーションによりネットワーク層の制限を適用
9. DNS Pinning攻撃のために許可リストドメインを監視
10. AWS IMDSv2のようなクラウド固有の保護を使用
