---
description: Dockerセキュリティのベストプラクティス
languages:
- docker
- yaml
alwaysApply: false
---

## Dockerセキュリティガイドライン

このルールは、一般的なリスクから保護するための重要なDockerコンテナセキュリティプラクティスを推奨します：

- コンテナユーザーセキュリティ
  - Dockerfileで`USER`ディレクティブを使用して常に非rootユーザーを指定。
  - コンテナを決してrootとして実行しない。`docker run -u <user>`またはKubernetesの`securityContext.runAsUser`を使用。
  - Dockerfileで`USER root`または`USER`ディレクティブの欠落を避ける。

- Dockerデーモンソケット保護
  - ボリュームマウントを介してコンテナに`/var/run/docker.sock`を決して公開しない。
  - TLSなしでTCP Dockerデーモンソケット（`-H tcp://0.0.0.0:XXX`）を有効化しない。
  - docker-composeファイルで`- "/var/run/docker.sock:/var/run/docker.sock"`を避ける。

- ケーパビリティと権限管理
  - すべてのケーパビリティをドロップ（`--cap-drop all`）し、必要なもののみを追加（`--cap-add`）。
  - コンテナ設定で`--privileged`フラグを使用しない。
  - Kubernetesセキュリティコンテキストで`allowPrivilegeEscalation: false`を設定。
  - 権限昇格を防ぐために`--security-opt=no-new-privileges`を使用。

- Dockerfileセキュリティプラクティス
  - ベースイメージのバージョンを固定（本番では`latest`タグを避ける）。
  - アーカイブを抽出しない場合は`ADD`の代わりに`COPY`を使用。
  - Dockerfileにシークレット、パスワード、APIキーを含めない。
  - `RUN`ディレクティブでcurl bashingを避ける。可能な場合はパッケージマネージャーを使用。
  - コンテナヘルスモニタリングのために`HEALTHCHECK`命令を含める。

- リソースとファイルシステムセキュリティ
  - docker-composeまたはKubernetes仕様でコンテナリソース（メモリ、CPU）を制限。
  - 読み取り専用ルートファイルシステムを使用（`--read-only`または`readOnlyRootFilesystem: true`）。
  - 書き込みアクセスが不要な場合、ボリュームを読み取り専用（`:ro`）でマウント。
  - 永続ボリュームの代わりに一時的な書き込み可能ストレージに`--tmpfs`を使用。

- ネットワークとランタイムセキュリティ
  - デフォルトのブリッジネットワークを避ける。カスタムDockerネットワークを定義。
  - ホストネットワーク名前空間を共有しない（`--net=host`）。
  - Dockerfileまたはコンテナ設定で不必要なポートを公開しない。
  - デフォルトのセキュリティプロファイル（seccomp、AppArmor、SELinux）を有効化。無効化しない。

- シークレット管理
  - 機密データにはDocker SecretsまたはKubernetes暗号化シークレットを使用。
  - 環境変数またはDockerfileレイヤーにシークレットを埋め込まない。
  - コンテナ設定にハードコーディングされた認証情報を避ける。

- コンテナイメージセキュリティ
  - デプロイ前にイメージの脆弱性をスキャン。
  - 攻撃対象領域を減らすために最小限のベースイメージ（alpine、distroless）を使用。
  - 本番イメージからパッケージマネージャーと不要なツールを削除。

要約：
常にコンテナを非rootユーザーとして実行し、Dockerデーモンソケットを決して公開せず、不要なケーパビリティをドロップし、安全なDockerfileプラクティスを使用し、リソース制限と読み取り専用ファイルシステムを実装し、適切なネットワークを設定し、シークレットを安全に管理し、イメージの脆弱性をスキャンします。
