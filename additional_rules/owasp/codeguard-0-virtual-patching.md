---
description: 仮想パッチングセキュリティ
languages:
- c
- go
- java
- javascript
- php
- python
- ruby
- typescript
- xml
alwaysApply: false
---

## 仮想パッチングセキュリティ

セキュリティポリシー実施レイヤーを通じて、恒久的なコード修正を開発しながら既知の脆弱性から保護するための一時的なセキュリティ制御を実装。

### 仮想パッチングの定義

既知の脆弱性の悪用の試行を防止し報告するセキュリティポリシー実施レイヤー。仮想パッチはトランザクションを分析し転送中の攻撃を傍受するため、悪意のあるトラフィックがWebアプリケーションに決して到達せず、実際のソースコードは変更されないまま保護を提供します。

### 仮想パッチングが必要な場合

仮想パッチングは、即時のコード修正が実現可能でない現実のシナリオに対応：

- リソース不足：開発者が他のプロジェクトに割り当てられている
- サードパーティソフトウェア：ユーザーがコードを変更できない
- アウトソース開発：変更に新しいプロジェクト承認が必要

重要：コードレベルの修正と仮想パッチングは相互に排他的ではありません。異なるチーム（開発者対セキュリティ運用）によって実行され、並行して実行できます。

### 仮想パッチングの目標

- Time-to-Fixの最小化：コード修正が開発されている間、できるだけ早く軽減策を実装
- 攻撃面の削減：完全な削減ではなく攻撃ベクトルの最小化に焦点（48時間で100%より10分で50%）

### 仮想パッチングツール

仮想パッチを実装するために利用可能なツール：
- WAFやIPSアプライアンスなどの中間デバイス
- ModSecurityなどのWebサーバープラグイン
- ESAPI WAFなどのアプリケーション層フィルター

### 仮想パッチング手法

一貫性のある再現可能な仮想パッチングのための構造化ワークフロー：

1. 準備
2. 識別
3. 分析
4. 仮想パッチ作成
5. 実装/テスト
6. 復旧/フォローアップ

### 準備フェーズ

インシデント発生前の重要な準備項目：

- 公開/ベンダー脆弱性モニタリング：商用ソフトウェアのベンダーアラートメーリングリストを購読
- 仮想パッチング事前承認：仮想パッチはソースコードを変更しないためガバナンスプロセスを迅速化
- 仮想パッチングツールを事前に配置：ModSecurity WAFまたは類似ツールをアクティベーション準備完了でインストール
- HTTP監査ログの増加：インシデント分析のためにリクエストURI、完全ヘッダー、リクエスト/レスポンスボディをキャプチャ

### 分析フェーズ

推奨される分析ステップ：

1. 脆弱性タイプの仮想パッチング適用可能性を判断
2. 脆弱性情報管理にバグ追跡システムを利用
3. 脆弱性識別子（CVE名/番号）を確認
4. 適切な優先順位付けのために影響レベルを指定
5. 影響を受けるソフトウェアバージョンを指定
6. 脆弱性をトリガーする設定要件をリスト
7. 分析とテストのためにProof of Concept（PoC）エクスプロイトコードを収集

### 仮想パッチ作成の原則

正確な仮想パッチの2つの主要要件：
- 偽陽性なし：正当なトラフィックをブロックしない
- 偽陰性なし：回避の試行があっても攻撃を見逃さない

### ポジティブセキュリティ（許可リスト）仮想パッチ（推奨）

ポジティブセキュリティモデルは、有効な入力特性を指定し非準拠のものを拒否することで包括的な入力検証を提供。

SQLインジェクション保護のためのModSecurity仮想パッチの例：

```text
##
## Verify we only receive 1 parameter called "reqID"
##
SecRule REQUEST_URI "@contains /wp-content/plugins/levelfourstorefront/scripts/administration/exportsubscribers.php" "chain,id:1,phase:2,t:none,t:Utf8toUnicode,t:urlDecodeUni,t:normalizePathWin,t:lowercase,block,msg:'Input Validation Error for \'reqID\' parameter - Duplicate Parameters Names Seen.',logdata:'%{matched_var}'"
  SecRule &ARGS:/reqID/ "!@eq 1"

##
## Verify reqID's payload only contains integers
##
SecRule REQUEST_URI "@contains /wp-content/plugins/levelfourstorefront/scripts/administration/exportsubscribers.php" "chain,id:2,phase:2,t:none,t:Utf8toUnicode,t:urlDecodeUni,t:normalizePathWin,t:lowercase,block,msg:'Input Validation Error for \'reqID\' parameter.',logdata:'%{args.reqid}'"
  SecRule ARGS:/reqID/ "!@rx ^[0-9]+$"
```

### ネガティブセキュリティ（ブロックリスト）仮想パッチ

ネガティブセキュリティモデルは有効なトラフィックのみを許可するのではなく、特定の既知の攻撃を検出。

PoC攻撃ペイロードの例：
```text
http://localhost/wordpress/wp-content/plugins/levelfourstorefront/scripts/administration/exportsubscribers.php?reqID=1' or 1='1
```

ModSecurityブロックリスト仮想パッチの例：
```text
SecRule REQUEST_URI "@contains /wp-content/plugins/levelfourstorefront/scripts/administration/exportsubscribers.php" "chain,id:1,phase:2,t:none,t:Utf8toUnicode,t:urlDecodeUni,t:normalizePathWin,t:lowercase,block,msg:'Input Validation Error for \'reqID\' parameter.',logdata:'%{args.reqid}'"
  SecRule ARGS:/reqID/ "@pm '"
```

### セキュリティモデルの比較

ポジティブ対ネガティブセキュリティの考慮事項：
- ネガティブセキュリティ：より迅速な実装だがより多くの回避可能性
- ポジティブセキュリティ：より良い保護だが手動プロセス、大規模/動的サイトではスケーラビリティが低い
- アラートで識別された特定の脆弱性の場所にはポジティブセキュリティを推奨

### エクスプロイト固有のパッチを避ける

正確なエクスプロイトペイロードのみをブロックするパッチの作成は避けてください。XSSの貧弱なアプローチの例：

```html
<script>
  alert('XSS Test')
</script>
```

この正確なペイロードのみをブロックしても、最小限の長期的保護価値しか提供しません。

### 自動化された仮想パッチ作成

脆弱性レポートからパッチを自動作成するツール：
- OWASP ModSecurity Core Rule Set (CRS) Scripts：ZAPなどのツールからXML出力を自動変換
- ThreadFix Virtual Patching：脆弱性XMLデータをModSecurityパッチに変換
- ダイレクトWAFインポート：商用WAF製品がDASTツールXMLレポートをインポート

### 実装とテスト

仮想パッチ検証のためのテストツール：
- Webブラウザ
- コマンドラインクライアント（Curl、Wget）
- ローカルプロキシサーバー（ZAP）
- ログ操作と再注入のためのModSecurity AuditViewer

テストステップ：
- 偽陽性を防ぐために最初は「Log Only」モードでパッチを実装
- 脆弱性識別チームに再テストを要求
- 再テスト中に回避が発生した場合は分析フェーズに戻る

### 復旧とフォローアップ

実装後のアクティビティ：
- 仮想パッチの詳細とルールIDでチケットシステムを更新
- 仮想パッチを削除できる時期を決定するために定期的な再評価を実施
- 保護価値を実証するために仮想パッチアラートレポートを実行
- 異なる脆弱性タイプのtime-to-fixメトリクスを追跡

### 開発者統合ガイドライン

1. 仮想パッチより恒久的なコード修正を優先
2. 仮想パッチ要件とテストについてセキュリティチームと協力
3. 仮想パッチの制限と一時的性質を理解
4. ポジティブセキュリティルールのために通常のアプリケーション動作に関する入力を提供
5. 安全なコーディングプラクティスに情報を提供する攻撃パターンの仮想パッチログをレビュー
6. 仮想パッチで保護された根本原因に対処するコード修正を計画
7. コード修正が展開されたら仮想パッチ削除プロセスに参加
8. 仮想パッチ作成のためのアプリケーション固有の要件を文書化
