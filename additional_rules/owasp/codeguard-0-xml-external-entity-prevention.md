---
description: XML外部エンティティ（XXE）防止
languages:
- c
- java
- matlab
- php
- python
- swift
- xml
alwaysApply: false
---

## XML外部エンティティ（XXE）防止

XMLパーサーでDTDと外部エンティティを無効にすることでXML外部エンティティ（XXE）攻撃を防止します。最も安全なアプローチ: DTDを完全に無効化します。

### 一般原則

```java
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
```

DTDを無効にすることで、XXE攻撃とBillion Laughs攻撃から保護されます。DTDを無効にできない場合は、パーサー固有のメソッドを使用して外部エンティティを無効にしてください。

### Java

JavaパーサーはデフォルトでXXEが有効になっています。

DocumentBuilderFactory/SAXParserFactory/DOM4J:

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
String FEATURE = null;
try {
    // 主要な防御 - DTDを完全に無効化
    FEATURE = "http://apache.org/xml/features/disallow-doctype-decl";
    dbf.setFeature(FEATURE, true);
    dbf.setXIncludeAware(false);
} catch (ParserConfigurationException e) {
    logger.info("ParserConfigurationException was thrown. The feature '" + FEATURE
    + "' is not supported by your XML processor.");
}
```

DTDを完全に無効化できない場合:

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

XMLInputFactory (StAX):
```java
xmlInputFactory.setProperty(XMLInputFactory.SUPPORT_DTD, false);
// またはDTDが必要な場合:
xmlInputFactory.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
xmlInputFactory.setProperty("javax.xml.stream.isSupportingExternalEntities", false);
```

TransformerFactory:
```java
TransformerFactory tf = TransformerFactory.newInstance();
tf.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
tf.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
```

XMLReader:
```java
XMLReader reader = XMLReaderFactory.createXMLReader();
reader.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
reader.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
reader.setFeature("http://xml.org/sax/features/external-general-entities", false);
reader.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

SAXBuilder:
```java
SAXBuilder builder = new SAXBuilder();
builder.setFeature("http://apache.org/xml/features/disallow-doctype-decl",true);
Document doc = builder.build(new File(fileName));
```

No-op EntityResolver:
```java
public final class NoOpEntityResolver implements EntityResolver {
    public InputSource resolveEntity(String publicId, String systemId) {
        return new InputSource(new StringReader(""));
    }
}
xmlReader.setEntityResolver(new NoOpEntityResolver());
documentBuilder.setEntityResolver(new NoOpEntityResolver());
```

信頼できないコンテンツに対してjava.beans.XMLDecoderを絶対に使用しないでください - 任意のコードを実行できます。

### .NET

XmlReader (.NET 4.5.2以降はデフォルトで安全):
```csharp
XmlReaderSettings settings = new XmlReaderSettings();
settings.DtdProcessing = DtdProcessing.Prohibit;
settings.XmlResolver = null;
XmlReader reader = XmlReader.Create(stream, settings);
```

XmlTextReader (.NET 4.0以前):
```csharp
XmlTextReader reader = new XmlTextReader(stream);
reader.ProhibitDtd = true;
```

XmlTextReader (.NET 4.0 - 4.5.2):
```csharp
XmlTextReader reader = new XmlTextReader(stream);
reader.DtdProcessing = DtdProcessing.Prohibit;
```

XmlDocument (4.5.2以前):
```csharp
XmlDocument xmlDoc = new XmlDocument();
xmlDoc.XmlResolver = null;
xmlDoc.LoadXml(xml);
```

XPathNavigator (4.5.2以前):
```csharp
XmlReader reader = XmlReader.Create("example.xml");
XPathDocument doc = new XPathDocument(reader);
XPathNavigator nav = doc.CreateNavigator();
string xml = nav.InnerXml.ToString();
```

### C/C++

libxml2: XML_PARSE_NOENTとXML_PARSE_DTDLOADオプションを避けてください。

libxerces-c:
```cpp
XercesDOMParser *parser = new XercesDOMParser;
parser->setCreateEntityReferenceNodes(true);
parser->setDisableDefaultEntityResolution(true);

SAXParser* parser = new SAXParser;
parser->setDisableDefaultEntityResolution(true);

SAX2XMLReader* reader = XMLReaderFactory::createXMLReader();
parser->setFeature(XMLUni::fgXercesDisableDefaultEntityResolution, true);
```

### PHP

PHP 8.0以降はデフォルトでXXEを防止します。それ以前のバージョン:
```php
libxml_set_external_entity_loader(null);
```

### Python

```python
from defusedxml import ElementTree as ET
tree = ET.parse('filename.xml')

# またはlxmlの場合:
from lxml import etree
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.parse('filename.xml', parser)
```

### iOS/macOS

```swift
let options: NSXMLNodeOptions = .documentTidyXML
let xmlDoc = try NSXMLDocument(data: data, options: options.union(.nodeLoadExternalEntitiesNever))
```

### ColdFusion

Adobe ColdFusion:
```
<cfset parseroptions = structnew()>
<cfset parseroptions.ALLOWEXTERNALENTITIES = false>
<cfscript>
a = XmlParse("xml.xml", false, parseroptions);
</cfscript>
```

Lucee (Application.cfc):
```
this.xmlFeatures = {
     externalGeneralEntities: false,
     secure: true,
     disallowDoctypeDecl: true
};
```

### 追加措置

- XMLライブラリを定期的に更新してください
- 解析前にXML入力を検証してください
- XXE検出のために静的解析ツールを使用してください
- 安全な環境でXXEペイロードを使用してテストしてください

### DTDが必要な場合

DTDが絶対に必要な場合:
- 制限されたエンティティを持つカスタムEntityResolverを使用してください
- 厳密なエンティティホワイトリストを実装してください
- 危険なDOCTYPE宣言を除去するためにXMLを前処理してください
