---
description: デシリアライゼーションセキュリティベストプラクティス
languages:
- c
- java
- javascript
- php
- python
- xml
- yaml
alwaysApply: false
---

## 信頼できないデータの安全でないデシリアライゼーションを避ける

信頼できない入力のデシリアライゼーションは、リモートコード実行、サービス拒否、権限昇格などの重大な脆弱性につながる可能性があります。このルールは、開発者がシリアライゼーションとデシリアライゼーション操作を安全に処理するためのベストプラクティスに従うことを保証します。

要件：

- 信頼できないソースからの受信シリアライズデータは常に敵対的なものとして扱います。
- デシリアライゼーション前に入力サイズ、構造、内容を検証します。
- ネイティブシリアライゼーション形式よりも、型メタデータのないJSONやXMLのような標準化された安全なデータ形式を優先します。
- XMLの場合：XXE攻撃を防ぐためDTDと外部エンティティを無効化します。
- 信頼できない入力に対する安全でないネイティブシリアライゼーションAPIの使用を避けます：
  - PHP：`unserialize()`を避け、代わりに`json_decode()`/`json_encode()`を使用します。
  - Python：`pickle.loads`、`yaml.load`（`safe_load`を使用）、`jsonpickle`を信頼できないデータに対して避けます。
  - Java：`ObjectInputStream#resolveClass()`をオーバーライドしてクラスを許可リスト化、機密フィールドを`transient`としてマーク、厳密に許可リスト化しない限り多態的デシリアライゼーションを避けます。
  - .NET：`BinaryFormatter`を避ける、`DataContractSerializer`または`XmlSerializer`を使用、JSON.Netで`TypeNameHandling = None`を設定、デシリアライズされた型を盲目的に信頼しません。
- シリアライズされたデータに署名し、デシリアライゼーション前に署名を検証して整合性を確保します。
- シリアライゼーションライブラリを安全に設定します：
  - Jackson：`mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL)`は危険
  - fastjson：セーフモードを有効化、autotypeを無効化
  - XStream：`XStream.allowTypes()`で許可リストを使用
  - SnakeYAML：`yaml.load()`の代わりに`yaml.safe_load()`を使用
  - 依存関係を修正バージョンに最新化します。
- 信頼できないソースからの多態的または複雑なオブジェクトのデシリアライゼーションを拒否または安全に処理します。
- 堅牢化されたデシリアライゼーションエージェント/ツール（例：SerialKiller、堅牢化されたObjectInputStreamサブクラス、JVMエージェント）を使用します。
- デシリアライゼーション試行をログに記録し、疑わしい活動を監視します。
- 静的および動的解析ツールを使用して、安全でないデシリアライゼーションパターンをコードと依存関係で定期的にスキャンします。

セキュリティへの影響：

デシリアライゼーション攻撃は、深刻なセキュリティ影響をもたらす頻繁に悪用されるベクトルです。これらのプラクティスに従うことで、攻撃者がアプリケーションが実行する可能性のある悪意のあるオブジェクトやペイロードを注入することを防ぎます。

例：

避けるべき：
- PHP：外部入力に対して`unserialize($data)`を呼び出す。
- Java：厳密な許可リストや型検証なしでクラスをデシリアライズする。
- Python：信頼できないデータに対して`yaml.load()`でYAMLを読み込む。
- .NET：信頼できない入力に対して`BinaryFormatter.Deserialize()`を使用する。
- XML：DTDが有効または外部エンティティ解決でXMLを処理する。

推奨：
- PHP：`json_decode()`を使用し、JSONスキーマを検証する。
- Java：安全なクラスを許可リスト化するため`resolveClass()`をオーバーライドする：
  ```java
  @Override
  protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
      if (!allowedClasses.contains(desc.getName())) {
          throw new InvalidClassException("Unauthorized class", desc.getName());
      }
      return super.resolveClass(desc);
  }
  ```
- Python：安全なYAML読み込みを使用する：
  ```python
  import yaml
  data = yaml.safe_load(input)  # 安全
  # 決してしないこと：yaml.load(input)     # 危険
  ```
- .NET：型制御を伴うDataContractSerializerを使用する：
  ```csharp
  // 安全なアプローチ
  var serializer = new DataContractSerializer(typeof(SafeType));
  var obj = serializer.ReadObject(stream);

  // JSON.NETの安全性
  JsonConvert.DeserializeObject<SafeType>(json, new JsonSerializerSettings {
      TypeNameHandling = TypeNameHandling.None
  });
  ```
- XML：パーサーを安全に設定する：
  ```java
  // Java：DTDと外部エンティティを無効化
  factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
  factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
  ```
  ```csharp
  // .NET：DTD処理を無効化
  XmlReaderSettings settings = new XmlReaderSettings();
  settings.DtdProcessing = DtdProcessing.Prohibit;
  ```

監視要件：
- データサイズと型情報を含むすべてのデシリアライゼーション試行をログに記録
- デシリアライゼーション失敗または予期しないデータパターンにアラート
- 既知の悪意のあるペイロード（例：`AC ED 00 05`、`rO0`、`AAEAAAD`）を監視
- 「billion laughs」攻撃を検出するためデシリアライゼーションパフォーマンスを追跡
