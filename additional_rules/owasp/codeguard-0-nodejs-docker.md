---
description: Node.js Dockerセキュリティベストプラクティス
languages:
- d
- javascript
alwaysApply: false
---

## Node.js Dockerセキュリティガイドライン

本番デプロイメント向けの最適化され安全なNode.js Dockerイメージを構築するための必須セキュリティプラクティス。

### 明示的で決定論的なベースイメージを使用

常に特定のピン留めされたベースイメージタグを使用して決定論的ビルドを確保：
- `FROM node`または`FROM node:latest`を避ける（非決定論的動作を引き起こす）
- 攻撃面とイメージサイズを削減するために最小限のベースイメージを使用
- 最大のセキュリティのためにタグとSHA256ダイジェストの両方でイメージをピン留め

推奨パターン:
```dockerfile
FROM node:lts-alpine@sha256:b2da3316acdc2bec442190a1fe10dc094e7ba4121d029cb32075ff59bb27390a
```

### 本番依存関係のみをインストール

開発パッケージを除外する決定論的な依存関係インストールを使用：
```dockerfile
RUN npm ci --omit=dev
```

このアプローチ：
- lockfileの逸脱が存在する場合にCIを停止して驚きを防ぐ
- 開発依存関係からのセキュリティリスクを削減
- 不要なパッケージを除外してイメージサイズを削減

### 本番環境向けに最適化

フレームワークの最適化を有効にするために本番環境変数を設定：
```dockerfile
ENV NODE_ENV production
```

Expressなどの多くのフレームワークは、この変数が"production"に設定されている場合にのみパフォーマンスとセキュリティの最適化を有効化します。

### 非rootユーザーとして実行

セキュリティリスクを最小化するために最小権限の原則に従う：
```dockerfile
COPY --chown=node:node . /usr/src/app
USER node
```

公式nodeイメージには最小権限の`node`ユーザーが含まれています。権限の問題を防ぐために、すべてのコピーされたファイルがこのユーザーによって所有されることを確認してください。

### プロセスシグナルを適切に処理

プロセスシグナルを正しく処理するために適切なinitシステムを使用：
```dockerfile
RUN apk add dumb-init
CMD ["dumb-init", "node", "server.js"]
```

これらの問題のあるパターンを避ける：
- `CMD "npm" "start"` - npmはシグナルを転送しない
- `CMD "node" "server.js"` - PID 1としてのNode.jsはシグナルを適切に処理しない

### グレースフルシャットダウンを実装

Node.jsアプリケーションコードにシグナルハンドラーを追加：
```javascript
    async function closeGracefully(signal) {
       console.log(`*^!@4=> Received signal to terminate: ${signal}`)

       await fastify.close()
       // await db.close() if we have a db connection in this app
       // await other things we should cleanup nicely
       process.exit()
    }
    process.on('SIGINT', closeGracefully)
    process.on('SIGTERM', closeGracefully)
```

### マルチステージビルドを使用

最終イメージサイズを最小化しシークレット漏洩を防ぐためにビルドステージと本番ステージを分離：

```dockerfile
# --------------> The build image
FROM node:latest AS build
WORKDIR /usr/src/app
COPY package*.json /usr/src/app/
RUN --mount=type=secret,mode=0644,id=npmrc,target=/usr/src/app/.npmrc npm ci --omit=dev

# --------------> The production image
FROM node:lts-alpine@sha256:b2da3316acdc2bec442190a1fe10dc094e7ba4121d029cb32075ff59bb27390a
RUN apk add dumb-init
ENV NODE_ENV production
USER node
WORKDIR /usr/src/app
COPY --chown=node:node --from=build /usr/src/app/node_modules /usr/src/app/node_modules
COPY --chown=node:node . /usr/src/app
CMD ["dumb-init", "node", "server.js"]
```

### .dockerignoreファイルを使用

不要で機密性の高いファイルを除外するために`.dockerignore`ファイルを作成：
```
node_modules
npm-debug.log
Dockerfile
.git
.gitignore
.npmrc
```

これにより以下を防止：
- 変更されたローカル`node_modules/`をコンテナビルド版にコピーすること
- 認証情報やローカル設定などの機密ファイルを含めること
- ログファイルや一時ファイルからのキャッシュ無効化

### シークレットを安全にマウント

`.npmrc`などの機密ファイルを処理するためにDocker BuildKitシークレットを使用：
```dockerfile
RUN --mount=type=secret,mode=0644,id=npmrc,target=/usr/src/app/.npmrc npm ci --omit=dev
```

ビルドコマンド：
```bash
docker build . -t nodejs-tutorial --secret id=npmrc,src=.npmrc
```

これにより、シークレットが最終Dockerイメージレイヤーにコピーされないことが保証されます。

### セキュリティスキャン

静的分析ツールを使用してDockerイメージの脆弱性を定期的にスキャンし、依存関係を最新に保ちます。

これらのプラクティスに従うことで、本番デプロイメントに適した安全で最適化され保守可能なNode.js Dockerイメージを作成できます。
