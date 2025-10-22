---
description: XMLセキュリティと安全なデシリアライゼーション（DTD/XXE強化、スキーマ検証、安全でないネイティブデシリアライゼーションの禁止）
languages:
- c
- go
- java
- php
- python
- ruby
- xml
alwaysApply: false
---

## XML・シリアライゼーション強化

XMLとシリアライズされたデータの安全な解析と処理；XXE、エンティティ展開、SSRF、DoS、プラットフォーム全体での安全でないデシリアライゼーションを防止。

### XMLパーサー強化
- デフォルトでDTDと外部エンティティを無効化；DOCTYPE宣言を拒否。
- ローカルの信頼されたXSDで厳格に検証；明示的な制限（サイズ、深さ、要素数）を設定。
- リゾルバアクセスをサンドボックス化またはブロック；解析中のネットワークフェッチなし；予期しないDNSアクティビティを監視。

#### Java
一般原則：
```java
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
```

DTDを無効化することで、XXEとBillion Laughs攻撃から保護。DTDを無効化できない場合、パーサー固有のメソッドで外部エンティティを無効化。

### Java

JavaパーサーはデフォルトでXXEが有効。

DocumentBuilderFactory/SAXParserFactory/DOM4J：

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
String FEATURE = null;
try {
    // 主要な防御 - DTDを完全に禁止
    FEATURE = "http://apache.org/xml/features/disallow-doctype-decl";
    dbf.setFeature(FEATURE, true);
    dbf.setXIncludeAware(false);
} catch (ParserConfigurationException e) {
    logger.info("ParserConfigurationException was thrown. The feature '" + FEATURE
    + "' is not supported by your XML processor.");
}
```

DTDを完全に無効化できない場合：

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
String[] featuresToDisable = {
    "http://xml.org/sax/features/external-general-entities",
    "http://xml.org/sax/features/external-parameter-entities",
    "http://apache.org/xml/features/nonvalidating/load-external-dtd"
};

for (String feature : featuresToDisable) {
    try {
        dbf.setFeature(feature, false);
    } catch (ParserConfigurationException e) {
        logger.info("ParserConfigurationException was thrown. The feature '" + feature
        + "' is probably not supported by your XML processor.");
    }
}
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
dbf.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
```

#### .NET
```csharp
var settings = new XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit, XmlResolver = null };
var reader = XmlReader.Create(stream, settings);
```

#### Python
```python
from defusedxml import ElementTree as ET
ET.parse('file.xml')
# または lxml
from lxml import etree
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.parse('filename.xml', parser)
```

### 安全なXSLT/Transformer使用
- `ACCESS_EXTERNAL_DTD`と`ACCESS_EXTERNAL_STYLESHEET`を空に設定；リモートリソースの読み込みを避ける。

### デシリアライゼーション安全性
- 信頼できないネイティブオブジェクトをデシリアライズしない。スキーマ検証付きJSONを優先。
- 解析前にサイズ/構造制限を強制。厳格に許可リスト化されていない限り、ポリモーフィック型を拒否。
- 言語固有：
  - PHP：`unserialize()`を避ける；`json_decode()`を使用。
  - Python：`pickle`と安全でないYAMLを避ける（`yaml.safe_load`のみ）。
  - Java：許可リストのため`ObjectInputStream#resolveClass`をオーバーライド；Jacksonでデフォルト型付けを有効化しない；XStream許可リストを使用。
  - .NET：`BinaryFormatter`を避ける；`DataContractSerializer`または`System.Text.Json`を優先（JSON.NETでは`TypeNameHandling=None`）。
- 該当する場合、シリアライズされたペイロードに署名して検証；デシリアライゼーション失敗と異常をログに記録してアラート。

### 実装チェックリスト
- DTDオフ；外部エンティティ無効化；厳格なスキーマ検証；パーサー制限設定。
- 解析中のネットワークアクセスなし；リゾルバ制限；監査実施。
- 安全でないネイティブデシリアライゼーションなし；サポートされている形式の厳格な許可リストとスキーマ検証。
- 定期的なライブラリ更新とXXE/デシリアライゼーションペイロードのテスト。
