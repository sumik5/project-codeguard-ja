---
description: Symfonyセキュリティベストプラクティス
languages:
- php
- yaml
alwaysApply: false
---

## Symfonyセキュリティベストプラクティス

セキュアなSymfonyアプリケーション開発のための重要なセキュリティプラクティス、一般的な脆弱性とフレームワーク固有の保護をカバー。

### クロスサイトスクリプティング（XSS）防止

すべての変数にTwigのデフォルト`{{ }}`出力エスケープを使用します。HTML描画が必要な信頼できるコンテンツにのみ`|raw`フィルタを使用します。

```twig
<p>Hello {{name}}</p>
{# 'name' が '<script>alert('hello!')</script>' の場合、Twigは以下を出力します:
'<p>Hello &lt;script&gt;alert(&#39;hello!&#39;)&lt;/script&gt;</p>' #}

<p>{{ product.title|raw }}</p>
{# 'product.title' が 'Lorem <strong>Ipsum</strong>' の場合、Twigは
'Lorem &lt;strong&gt;Ipsum&lt;/strong&gt;' の代わりに正確にそれを出力します #}
```

### CSRF保護

Symfonyフォームは自動的にCSRFトークンを含みます。手動処理には`csrf_token()`と`isCsrfTokenValid()`を使用します。

```php
class PostForm extends AbstractType
{
    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            // ...
            'csrf_protection' => true,  // このフォームのCSRF保護を有効/無効化
            'csrf_field_name' => '_csrf_token',
            'csrf_token_id'   => 'post_item', // 生成に使用される任意の文字列を変更
        ]);
    }
}
```

手動CSRFトークン処理：
```twig
<form action="{{ url('delete_post', { id: post.id }) }}" method="post">
    <input type="hidden" name="token" value="{{ csrf_token('delete-post') }}">
    <button type="submit">Delete post</button>
</form>
```

```php
class ExampleController extends AbstractController
{
    #[Route('/posts/{id}', methods: ['DELETE'], name: 'delete_post')]
    public function delete(Post $post, Request $request): Response
    {
        $token = $request->request->get('token');
        if($this->isCsrfTokenValid($token)) {
            // ...
        }
        // ...
    }
}
```

### SQLインジェクション防止

Doctrine ORMでパラメータ化クエリを使用します。ユーザー入力をSQL文字列に連結しません。

```php
// リポジトリメソッド
$post = $em->getRepository(Post::class)->findOneBy(['id' => $id]);

// パラメータ付きDQL
$query = $em->createQuery("SELECT p FROM App\Entity\Post p WHERE p.id = :id");
$query->setParameter('id', $id);
$post = $query->getSingleResult();

// DBALクエリビルダー
$qb = $em->createQueryBuilder();
$post = $qb->select('p')
            ->from('posts','p')
            ->where('id = :id')
            ->setParameter('id', $id)
            ->getQuery()
            ->getSingleResult();
```

### コマンドインジェクション防止

ユーザー入力と共に`exec()`、`shell_exec()`、`system()`を避けます。SymfonyファイルシステムコンポーネントまたはネイティブPHP関数を使用します。

```php
// 脆弱な例
$filename = $request->request->get('filename');
exec(sprintf('rm %s', $filename));

// セキュアな代替案 - ネイティブPHPまたはSymfony Filesystemを使用
unlink($filename);

// またはSymfony Filesystemコンポーネント
use Symfony\Component\Filesystem\Filesystem;
$filesystem = new Filesystem();
$filesystem->remove($filename);
```

### ファイルアップロードセキュリティ

Symfonyバリデータ制約でファイルアップロードを検証します。一意の名前を持つ公開ディレクトリ外にファイルを保存します。

```php
class UploadDto
{
    public function __construct(
        #[File(
            maxSize: '1024k',
            mimeTypes: ['application/pdf', 'application/x-pdf'],
        )]
        public readonly UploadedFile $file,
    ){}
}
```

### ディレクトリトラバーサル防止

`realpath()`と`basename()`を使用してファイルパスを検証およびサニタイズします。

```php
$storagePath = $this->getParameter('kernel.project_dir') . '/storage';
$filePath = $storagePath . '/' . $filename;

$realBase = realpath($storagePath);
$realPath = realpath($filePath);

if ($realPath === false || !str_starts_with($realPath, $realBase)) {
    //ディレクトリトラバーサル!
}

// 代替案: ディレクトリ情報を削除
$filePath = $storagePath . '/' . basename($filename);
```

### セキュリティ設定

セッションセキュリティ、認証、アクセス制御を適切に設定します。

```yaml
# セッション設定
framework:
    session:
        cookie_httponly: true
        cookie_lifetime: 5
        cookie_samesite: lax
        cookie_secure: auto

# 認証プロバイダー、ファイアウォール、アクセス制御
security:
    providers:
        app_user_provider:
            entity:
                class: App\Entity\User
                property: email
    firewalls:
        dev:
            pattern: ^/(_(profiler|wdt)|css|images|js)/
            security: false
        admin:
            lazy: true
            provider: app_user_provider
            pattern: ^/admin
            custom_authenticator: App\Security\AdminAuthenticator
            logout:
                path: app_logout
                target: app_login
        main:
            lazy: true
            provider: app_user_provider
    access_control:
        - { path: ^/admin, roles: ROLE_ADMIN }
        - { path: ^/login, roles: PUBLIC_ACCESS }
```

### 本番環境セキュリティ

- `APP_ENV=prod`を設定し、デバッグモードを無効化
- 定期的なセキュリティチェックを実行: `composer update`と`symfony check:security`
- 機密データにSymfonyシークレットを使用
- `nelmio/cors-bundle`でCORSを設定（ワイルドカードオリジンを避ける）
- セキュリティヘッダーを実装（HSTS、CSP、X-Frame-Options）
- HTTPSを強制し、適切なファイル権限を設定
