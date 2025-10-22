---
description: Cookie盗難緩和のベストプラクティス
languages:
- java
- javascript
- php
- python
- ruby
- typescript
alwaysApply: false
---

## Cookie盗難緩和ガイドライン

このルールは、サーバー側監視を通じてセッションCookie盗難の検出と緩和についてアドバイスします：

- セッションフィンガープリント
  - セッション確立時にセッション環境情報を保存：IPアドレス、User-Agent、Accept-Language、Date。
  - 検出強化のため追加ヘッダーを保存：Accept、Accept-Encoding、sec-ch-uaヘッダー（利用可能な場合）。
  - 後続のリクエストで比較するため、フィンガープリントデータをセッションIDに関連付けます。

- Cookie盗難検出
  - リクエスト間でセッション環境情報の重大な変更を監視します。
  - 保存されたセッションフィンガープリントデータに対して現在のリクエストヘッダーを比較します。
  - 正当な変動（IPサブネット変更、ブラウザ更新）と疑わしい変更を区別します。
  - 単一のヘッダー変更に依存するのではなく、複数の検出ベクトルを使用します。

- 異常に対するリスクベースの対応
  - 高リスク操作の場合：疑わしい変更が検出された場合、再認証を要求します。
  - 中リスク操作の場合：CAPTCHAチャレンジまたは追加検証を実装します。
  - 低リスク操作の場合：疑わしいアクティビティをログに記録し監視を継続します。
  - 潜在的なハイジャックが検出された場合、常にセッションIDを再生成します。

- セッション検証実装
  - 機密操作の前に実行されるミドルウェアとして検出を実装します。
  - パフォーマンスへの影響を管理するため、高価値エンドポイントに選択的に検証を適用します。
  - 調査のため十分なコンテキストですべての疑わしいセッションアクティビティをログに記録します。
  - ユーザーエクスペリエンスを維持するため、誤検知を適切に処理します。

- 安全なセッションストレージ
  - セッションフィンガープリントデータをサーバー側に安全に保存（クライアント側には決して保存しない）。
  - フレームワークが提供する安全なセッションストレージメカニズムを使用します。
  - セッションデータが適切に暗号化され保護されていることを確認します。

コード例（OWASPより）：
```js
const session = SessionStorage.create()
session.save({
  ip: req.clientIP,
  user_agent: req.headers.userAgent,
  date: req.headers.date,
  accept_language: req.headers.acceptLanguage,
  // ...
})

function cookieTheftDetectionMiddleware(req, res) {
  const currentIP = req.clientIP
  const expectedIP = req.session.ip
  if (checkGeoIPRange(currentIP, expected) === false) {
     // Validation
  }
  const currentUA = req.userAgent
  const expectedUA = req.session.ua
  if (checkUserAgent(currentUA, expectedUA)) {
    // Validation
  }
  // ...
}
```

まとめ：
Cookie盗難を検出するためサーバー側セッションフィンガープリントを実装し、リクエスト間の環境変更を監視し、疑わしいアクティビティにリスクベースの対応を適用し、安全なセッションストレージを維持します。強化された保護のため、Device Bound Session Credentialsのような将来の標準を検討してください。
