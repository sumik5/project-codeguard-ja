---
description: Ruby on Railsセキュリティガイドライン
languages:
- c
- javascript
- ruby
- typescript
- yaml
alwaysApply: false
---

## Ruby on Railsセキュリティガイドライン

セキュアなRuby on Railsアプリケーション開発のための重要なセキュリティプラクティス。

### コマンドインジェクション防止

ユーザー入力と共にこれらの危険なメソッドを避けます：

```ruby
eval("ruby code here")
system("os command here")
`ls -al /` # (バッククォートにOSコマンド)
exec("os command here")
spawn("os command here")
open("| os command here")
Process.exec("os command here")
Process.spawn("os command here")
IO.binread("| os command here")
IO.binwrite("| os command here", "foo")
IO.foreach("| os command here") {}
IO.popen("os command here")
IO.read("| os command here")
IO.readlines("| os command here")
IO.write("| os command here", "foo")
```

システムとのやり取りが必要な場合、許可リストと検証を使用します。

### SQLインジェクション防止

```ruby
# 危険 - インジェクション可能
name = params[:name]
@projects = Project.where("name like '" + name + "'");

# 安全 - パラメータ化クエリを使用
@projects = Project.where("name like ?", "%#{ActiveRecord::Base.sanitize_sql_like(params[:name])}%")
```

### XSS防止

Railsはデフォルトで自動エスケープします。保護のバイパスを避けます：

```ruby
# 危険 - これを行わない
<%= raw @product.name %>
<%== @product.name %>
<%= @product.name.html_safe %>
```

許可されたタグのみの限定的なHTMLには`sanitize`ヘルパーを使用します。

### セッション管理

より良いセキュリティのためデータベースバックアップされたセッションを使用します：

```ruby
Project::Application.config.session_store :active_record_store
```

### トランスポートセキュリティ

本番環境でHTTPSを強制します：

```ruby
# config/environments/production.rb
config.force_ssl = true
```

### Deviseによる認証

```bash
gem 'devise'
rails generate devise:install
```

ルートを設定します：

```ruby
Rails.application.routes.draw do
  authenticate :user do
    resources :something do  # これらのリソースは認証が必要
      ...
    end
  end

  devise_for :users # サインアップ/イン/アウトルート
  root to: 'static#home' # 認証不要
end
```

zxcvbnによるパスワード複雑性：

```ruby
class User < ApplicationRecord
  devise :database_authenticatable,
    # 他のdevise機能、その後
    :zxcvbnable
end
```

```ruby
# in config/initializers/devise.rb
Devise.setup do |config|
  config.min_password_score = 4 # ここで複雑性スコア
  ...
```

### トークン認証

```bash
gem 'devise_token_auth'
gem 'omniauth'
```

```ruby
mount_devise_token_auth_for 'User', at: 'auth'
```

### CSRF保護

```ruby
class ApplicationController < ActionController::Base
  protect_from_forgery
```

トークン認証はCSRF保護を必要としません。

### セキュアなリダイレクト

```ruby
# 危険
redirect_to params[:url]

# 安全
begin
  if path = URI.parse(params[:url]).path
    redirect_to path
  end
rescue URI::InvalidURIError
  redirect_to '/'
end
```

複数のリダイレクト先には許可リストを使用します：

```ruby
ACCEPTABLE_URLS = {
  'our_app_1' => "https://www.example_commerce_site.com/checkout",
  'our_app_2' => "https://www.example_user_site.com/change_settings"
}

def redirect
  url = ACCEPTABLE_URLS["#{params[:url]}"]
  redirect_to url if url
end
```

### CORS設定

```ruby
# Gemfile
gem 'rack-cors', :require => 'rack/cors'

# config/application.rb
module Sample
  class Application < Rails::Application
    config.middleware.use Rack::Cors do
      allow do
        origins 'someserver.example.com'
        resource %r{/users/\d+.json},
        :headers => ['Origin', 'Accept', 'Content-Type'],
        :methods => [:post, :get]
      end
    end
  end
end
```

### セキュリティヘッダー

```ruby
ActionDispatch::Response.default_headers = {
  'X-Frame-Options' => 'SAMEORIGIN',
  'X-Content-Type-Options' => 'nosniff',
  'X-XSS-Protection' => '0'
}
```

### 機密ファイルの保護

ソース管理から保護します：

```text
/config/database.yml                 -  本番環境の認証情報を含む可能性があります。
/config/initializers/secret_token.rb -  セッションCookieのハッシュ化に使用されるシークレットを含みます。
/db/seeds.rb                         -  ブートストラップ管理者ユーザーを含むシードデータを含む可能性があります。
/db/development.sqlite3              -  実データを含む可能性があります。
```

### パスワードハッシュ化

bcryptストレッチを設定します：

```ruby
config.stretches = Rails.env.test? ? 1 : 10
```

### セキュリティテスト

静的分析にBrakemanを使用します：

```bash
gem install brakeman
brakeman -o security_report.html
```

### 主要なセキュリティ原則

- ユーザー入力と共に危険なコマンド実行メソッドを決して使用しません
- 常にパラメータ化クエリとActiveRecordメソッドを使用します
- Railsの自動HTMLエスケープに依存します
- 機密性の高いアプリケーションにはデータベースバックアップされたセッションを使用します
- CSRF保護を有効化し、リダイレクトを検証します
- セキュリティヘッダーを設定し、CORSを慎重に構成します
- セキュアなルーティングと依存関係管理を維持します
- Brakemanによる定期的なセキュリティテスト

Railsはデフォルトで多くのセキュリティ機能を提供しますが、開発者はそれらを正しく使用する必要があります。
