---
description: Kubernetesセキュリティのベストプラクティス
languages:
- javascript
- shell
- yaml
alwaysApply: false
---

## Kubernetesセキュリティガイドライン

安全なKubernetesクラスタのデプロイと管理のための必須セキュリティプラクティス。

### ホストとコンポーネントのセキュリティ

Kubernetesコンポーネントを最新の安定バージョンに更新します。Kubernetesプロジェクトは、セキュリティ修正を含む最新の3つのマイナーリリースのリリースブランチを維持しています。

重要なコンポーネントを保護：
- 相互TLS認証とファイアウォール分離でetcdへのアクセスを制限
- APIサーバーとetcd間で強力な認証情報を使用
- 機密ポートへのネットワークアクセスを制御（APIサーバーは6443、etcdは2379-2380）
- Kubelet認証と認可を有効化して、未認証アクセスを防止

### ビルドフェーズのセキュリティ

信頼できるレジストリから承認済み・スキャン済みコンテナイメージを使用：
- プライベートレジストリに承認済みイメージを保存
- CIパイプラインに脆弱性スキャンを統合して、脆弱なイメージをブロック
- 攻撃対象領域を減らすため、最小限のベースイメージ（可能な場合はdistroless）を使用
- ランタイムコンテナからシェルとパッケージマネージャーを削除

### デプロイフェーズのセキュリティ

#### Podセキュリティ設定

セキュリティコンテキストを適用してPodセキュリティパラメータを制御：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-world
spec:
  containers:
  # specification of the pod's containers
  # ...
  # Security Context
  securityContext:
    readOnlyRootFilesystem: true
    runAsNonRoot: true
```

#### Podセキュリティ標準

ネームスペースレベルの強制でPod Security Admission Controllerを使用：

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: policy-test
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

利用可能な3つのセキュリティプロファイル：
- **Privileged**: 無制限（システムワークロードのみ）
- **Baseline**: 最小限の制限、既知の権限昇格を防止
- **Restricted**: 最も制限的、現在のPodハードニングプラクティスを強制

#### ネットワークセキュリティ

Pod間通信を制御するネットワークポリシーを実装：

```json
POST /apis/net.alpha.kubernetes.io/v1alpha1/namespaces/tenant-a/networkpolicys
{
  "kind": "NetworkPolicy",
  "metadata": {
    "name": "pol1"
  },
  "spec": {
    "allowIncoming": {
      "from": [{
        "pods": { "segment": "frontend" }
      }],
      "toPorts": [{
        "port": 80,
        "protocol": "TCP"
      }]
    },
    "podSelector": {
      "segment": "backend"
    }
  }
}
```

#### リソース管理

DoS攻撃を防ぐためにリソースクォータを定義：

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
spec:
  hard:
    pods: "4"
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
```

### シークレット管理

- 環境変数ではなく読み取り専用ボリュームとしてシークレットをマウント
- イメージとPodからシークレットを分離して保存
- etcd内のSecretリソースの保存時暗号化を有効化
- マルチクラスタ環境には外部シークレットマネージャーを検討

### ランタイムフェーズのセキュリティ

#### 監視と検出

セキュリティ異常のためにコンテナの動作を監視：
- コンテナ内のシェル実行
- 機密ファイルアクセス（例：/etc/shadow）
- 予期しないネットワーク接続
- レプリカ間のプロセスアクティビティの逸脱

#### 監査ログ

APIリクエストを追跡するためにKubernetes監査ログを有効化：

```json
{
  "kind":"Event",
  "apiVersion":"audit.k8s.io/v1beta1",
  "metadata":{ "creationTimestamp":"2019-08-22T12:00:00Z" },
  "level":"Metadata",
  "timestamp":"2019-08-22T12:00:00Z",
  "auditID":"23bc44ds-2452-242g-fsf2-4242fe3ggfes",
  "stage":"RequestReceived",
  "requestURI":"/api/v1/namespaces/default/persistentvolumeclaims",
  "verb":"list",
  "user": {
    "username":"user@example.org",
    "groups":[ "system:authenticated" ]
  },
  "sourceIPs":[ "172.12.56.1" ]
}
```

### アクセス制御

- 最小権限の原則でRBACを実装
- 多要素認証を使用する外部認証（OIDC）を使用
- 本番クラスタでは組み込み認証方法を避ける
- 認証リバースプロキシでKubernetes Dashboardを保護

### 主要なセキュリティ要件

- 常に最新の安定したKubernetesバージョンを実行
- ワークロードを分離するためにネームスペースを使用
- 特権コンテナ実行を防ぐためにセキュリティコンテキストを適用
- トラフィック分離のためにネットワークポリシーを実装
- 包括的な監査ログと監視を有効化
- 認証情報を頻繁にローテーションし、ブートストラップトークンを迅速に取り消す
- セキュリティポリシーを強制するためにアドミッションコントローラーを使用
