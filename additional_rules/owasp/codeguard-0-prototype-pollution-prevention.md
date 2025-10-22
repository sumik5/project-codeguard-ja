---
description: プロトタイプ汚染の防止
languages:
- javascript
- typescript
alwaysApply: false
---

# プロトタイプ汚染防止ガイドライン

## 説明

プロトタイプ汚染は、攻撃者がアプリケーションのJavaScriptオブジェクトとプロパティを操作し、データへの不正アクセス、権限昇格、さらにはリモートコード実行などの深刻なセキュリティ問題を引き起こす可能性がある重大な脆弱性です。

## 推奨される保護メカニズム

### "new Set()"または"new Map()"を使用

開発者はオブジェクトリテラルの代わりに`new Set()`または`new Map()`を使用すべきです:

```javascript
let allowedTags = new Set();
allowedTags.add('b');
if(allowedTags.has('b')){
  //...
}

let options = new Map();
options.set('spaces', 1);
let spaces = options.get('spaces')
```

### オブジェクトまたはオブジェクトリテラルが必要な場合

オブジェクトを使用する必要がある場合は、`Object.create(null)` APIを使用してObjectプロトタイプから継承しないようにして作成すべきです:

```javascript
let obj = Object.create(null);
```

オブジェクトリテラルが必要な場合は、最終手段として`__proto__`プロパティを使用できます:

```javascript
let obj = {__proto__:null};
```

### オブジェクトの"freeze"および"seal"メカニズムを使用

`Object.freeze()`および`Object.seal()` APIを使用して組み込みプロトタイプの変更を防ぐこともできますが、使用しているライブラリが組み込みプロトタイプを変更する場合、アプリケーションが壊れる可能性があります。

### Node.js設定フラグ

Node.jsでは`--disable-proto=delete`フラグを使用して`__proto__`プロパティを完全に削除するオプションも提供されています。これは多層防御の手段です。

プロトタイプ汚染は`constructor.prototype`プロパティを使用することで依然として可能ですが、`__proto__`を削除することで攻撃対象領域を減らし、特定の攻撃を防ぐのに役立ちます。

### その他のリソース

- [What is prototype pollution? (Portswigger Web Security Academy)](https://portswigger.net/web-security/prototype-pollution)
- [Prototype pollution (Snyk Learn)](https://learn.snyk.io/lessons/prototype-pollution/javascript/)

### クレジット

元の保護ガイダンスを[このコメント](https://github.com/OWASP/ASVS/issues/1563#issuecomment-1470027723)で提供してくれた[Gareth Hayes](https://garethheyes.co.uk/)氏に感謝します。
