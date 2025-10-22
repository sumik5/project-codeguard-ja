---
description: GraphQLセキュリティのベストプラクティス
languages:
- javascript
- typescript
alwaysApply: false
---

## GraphQLセキュリティガイドライン

このルールは、インジェクション、DoS、不正アクセス、情報漏洩を防ぐための安全なGraphQL API開発についてアドバイスします：

- 入力検証とインジェクション防止
  - すべての入力検証に特定のGraphQLデータ型（スカラー、列挙型）を使用。
  - 複雑な検証にはカスタムGraphQLバリデータを定義し、カスタムスカラーを使用。
  - ミューテーション入力に厳格な検証ルールを持つスキーマを定義。
  - 文字検証には許可リストアプローチを使用（拒否リストを避ける）。
  - リゾルバーでのデータベースクエリにパラメータ化されたステートメントと安全なAPIを適用。
  - ORMインジェクション脆弱性を避けるためORM/ODMを適切に使用。
  - 内部API詳細を明かさずに無効な入力を適切に拒否。

- DoS防止とクエリ制限
  - graphql-depth-limit（JavaScript）やMaxQueryDepthInstrumentation（Java）などのライブラリを使用してクエリ深度制限を実装。
  - graphql-cost-analysisやMaxQueryComplexityInstrumentationを使用してクエリ複雑度分析を追加。
  - graphql-input-numberなどのライブラリでクエリ量制限を強制。
  - 単一レスポンスで返されるデータを制限するためページネーションを実装。
  - カスタムインストルメンテーションを使用してアプリケーションレベルでクエリタイムアウトを追加。
  - 基本的なDoS攻撃を防ぐためIPまたはユーザーごとのレート制限を適用。
  - 効率化のためサーバーサイドバッチングとキャッシング（FacebookのDataLoaderなど）を使用。

- アクセス制御と認可
  - すべてのデータ閲覧とミューテーション操作でリクエスト者の認可を検証。
  - IDOR/BOLA脆弱性を防ぐため適切なオブジェクトレベル認可を実装。
  - GraphQLスキーマのエッジとノードの両方で認可チェックを強制。
  - 権限に基づいて異なるオブジェクトプロパティを返すためInterfaceとUnionを使用。
  - RBACミドルウェアでQueryとMutationリゾルバーにアクセス制御検証を追加。
  - IDによる直接オブジェクトアクセスを許可する意図しないnode/nodesフィールドをチェック。
  - 機密データに対するフィールドレベルのアクセス制御を実装。

- バッチング攻撃防止
  - バッチ化して同時実行できるクエリ数を制限。
  - インスタンスリクエストを追跡するためコードレベルでオブジェクトリクエストレート制限を追加。
  - 機密オブジェクト（ユーザー名、パスワード、トークン、OTP）のバッチングを防止。
  - 重要な操作のバッチングを無効化するカスタムソリューションを実装。
  - セキュリティ分析のためバッチング試行を監視しログ記録。

- 安全な設定管理
  - 本番環境でNoIntrospectionGraphqlFieldVisibility（Java）または検証ルール（JavaScript）を使用してGraphQLイントロスペクションを無効化。
  - 本番環境でGraphiQLと類似の探索ツールを無効化。
  - スタックトレースとデバッグ情報の露出を防ぐためエラーマスキングを設定。
  - NODE_ENVを'production'に設定するか、Apollo Server設定でdebug: falseを使用。
  - イントロスペクションが無効の場合、フィールド提案ヒントを無効化。

- 認証とセッション管理
  - すべてのGraphQLエンドポイントに認証を要求（明示的に公開でない限り）。
  - 安全なトークン検証を伴う適切なセッション管理を実装。
  - リゾルバーで適切な検証を伴うJWTまたはセッションベース認証を使用。
  - Cookieベース認証を使用する場合、GraphQLミューテーションにCSRF保護を適用。
  - クエリやミューテーションを処理する前に認証状態を検証。

コード例（OWASPより）：

イントロスペクション無効化 - Java：
```java
GraphQLSchema schema = GraphQLSchema.newSchema()
    .query(StarWarsSchema.queryType)
    .fieldVisibility( NoIntrospectionGraphqlFieldVisibility.NO_INTROSPECTION_FIELD_VISIBILITY )
    .build();
```

イントロスペクションとGraphiQL無効化 - JavaScript：
```javascript
app.use('/graphql', graphqlHTTP({
  schema: MySessionAwareGraphQLSchema,
+ validationRules: [NoIntrospection]
  graphiql: process.env.NODE_ENV === 'development',
}));
```

クエリ深度の例：
```javascript
query evil {            # 深度: 0
  album(id: 42) {       # 深度: 1
    songs {             # 深度: 2
      album {           # 深度: 3
        songs {         # 深度: 4
          album {id: N} # 深度: N
        }
      }
    }
  }
}
```

過剰量リクエストの例：
```javascript
query {
  author(id: "abc") {
    posts(first: 99999999) {
      title
    }
  }
}
```

バッチング攻撃の例：
```javascript
[
  {
    query: < query 0 >,
    variables: < variables for query 0 >,
  },
  {
    query: < query 1 >,
    variables: < variables for query 1 >,
  },
  {
    query: < query n >
    variables: < variables for query n >,
  }
]
```

要約：
包括的な入力検証、クエリ制限、適切なアクセス制御、バッチング攻撃防止、安全な設定管理、堅牢な認証メカニズムを通じてGraphQL APIを保護し、インジェクション、DoS、不正データアクセスなどの一般的な攻撃ベクターを防止します。
