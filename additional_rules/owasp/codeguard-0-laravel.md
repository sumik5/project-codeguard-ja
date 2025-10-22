---
description: Laravelセキュリティベストプラクティス
languages:
- c
- javascript
- php
- typescript
- yaml
alwaysApply: false
---

## Laravelセキュリティガイドライン

セキュアなLaravelアプリケーション構築のための重要なセキュリティプラクティス。

### 基本設定

本番環境でデバッグモードを無効化し、アプリケーションキーを生成します：

```ini
APP_DEBUG=false
```

```bash
php artisan key:generate
```

セキュアなファイル権限を設定：ディレクトリ`775`、ファイル`664`、実行可能ファイル`775`。

### Cookieセキュリティとセッション管理

`App\Http\Kernel`でCookie暗号化ミドルウェアを有効化します：

```php
protected $middlewareGroups = [
    'web' => [
        \App\Http\Middleware\EncryptCookies::class,
        ...
    ],
    ...
];
```

`config/session.php`でセキュアなセッション設定を構成します：

```php
'http_only' => true,
'domain' => null,
'same_site' => 'lax',
'secure' => null,
'lifetime' => 15,
```

### Mass Assignment保護

Mass Assignment脆弱性から保護します：

```php
// 脆弱：任意のフィールドの変更を許可
Route::any('/profile', function (Request $request) {
    $request->user()->forceFill($request->all())->save();
    return response()->json(compact('user'));
})->middleware('auth');
```

`$request->all()`の代わりに`$request->only()`または`$request->validated()`を使用します。

### SQLインジェクション防止

EloquentORMパラメータ化クエリをデフォルトで使用します。生クエリには必ずバインディングを使用します：

```php
// 脆弱：SQLバインディングなし
User::whereRaw('email = "'.$request->input('email').'"')->get();

// 安全：SQLバインディングを使用
User::whereRaw('email = ?', [$request->input('email')])->get();

// 安全：名前付きバインディング
User::whereRaw('email = :email', ['email' => $request->input('email')])->get();
```

カラム名インジェクションを防ぐためカラム名を検証します：

```php
$request->validate(['sortBy' => 'in:price,updated_at']);
User::query()->orderBy($request->validated()['sortBy'])->get();
```

### XSS防止

すべての信頼できないデータにBladeの自動エスケープを使用します：

```blade
{{-- 安全：自動的にエスケープ --}}
{{ request()->input('somedata') }}

{{-- 脆弱：エスケープされないデータ --}}
{!! request()->input('somedata') !!}
```

### ファイルアップロードセキュリティ

常にファイルタイプとサイズを検証します：

```php
$request->validate([
    'photo' => 'file|size:100|mimes:jpg,bmp,png'
]);
```

パストラバーサルを防ぐためファイル名をサニタイズします：

```php
Route::post('/upload', function (Request $request) {
    $request->file('file')->storeAs(auth()->id(), basename($request->input('filename')));
    return back();
});
```

### パストラバーサル防止

ディレクトリ情報を削除するため`basename()`を使用します：

```php
Route::get('/download', function(Request $request) {
    return response()->download(storage_path('content/').basename($request->input('filename')));
});
```

### CSRF保護

CSRFミドルウェアを有効化し、フォームでトークンを使用します：

```php
protected $middlewareGroups = [
    'web' => [
        ...
         \App\Http\Middleware\VerifyCsrfToken::class,
         ...
    ],
];
```

```html
<form method="POST" action="/profile">
    @csrf
    <input type="hidden" name="_token" value="{{ csrf_token() }}" />
</form>
```

### コマンドインジェクション防止

ユーザー入力を伴うシェルコマンドをエスケープします：

```php
public function verifyDomain(Request $request)
{
    exec('whois '.$request->input('domain'));
}
```

適切なエスケープのため`escapeshellcmd`と`escapeshellarg`を使用します。

### レート制限

悪用から保護するためスロットリングを適用します：

```php
Route::get('/profile', function () {
    return 'User profile';
})->middleware('throttle:10,1'); // 1分あたり10リクエスト

// カスタムレート制限
RateLimiter::for('custom-limit', function ($request) {
    return Limit::perMinute(5)->by($request->user()?->id ?: $request->ip());
});
```

### その他のインジェクション防止

信頼できない入力で危険な関数を避けます：

```php
unserialize($request->input('data'));
eval($request->input('data'));
extract($request->all());
```

### セキュリティ監査

脆弱性をスキャンし、依存関係を最新に保つため、Enlightn Security Checkerを使用します。
