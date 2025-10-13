# Project CodeGuard: Security Rules for AI Coding Assistants

Project CodeGuard is an open-source, model-agnostic security framework that embeds secure-by-default practices into AI coding workflows. It provides comprehensive security rules that guide AI assistants to generate more secure code automatically.

## Why Project CodeGuard?

AI-powered IDEs and coding agents are transforming software development, but this speed can introduce security gaps:

- ❌ Skipping input validation
- ❌ Hardcoding secrets and credentials
- ❌ Using weak cryptographic algorithms
- ❌ Relying on unsafe functions
- ❌ Missing authentication/authorization checks

**Project CodeGuard solves this by embedding security best practices directly into AI coding workflows.**

## Key Features

<div class="grid cards" markdown>

-   :material-shield-check: **Comprehensive Coverage**

    ---

    Security rules covering cryptography, input validation, authentication, authorization, and more

-   :material-robot: **Model-Agnostic**

    ---

    Works with any AI coding assistant - Cursor, Windsurf, GitHub Copilot, and more

-   :material-speedometer: **Zero Friction**

    ---

    No developer overhead or workflow changes required - works transparently in the background

-   :material-open-source-initiative: **Open Source**

    ---

    Apache 2.0 licensed, community-driven, and extensible for your specific needs

</div>

## Security Coverage

Our rules cover essential security domains:

- **🔐 Cryptography**: Safe algorithms (AES-256, SHA-256+), secure key management, certificate validation
- **🛡️ Input Validation**: SQL injection prevention, XSS protection, command injection defense
- **🔑 Authentication**: MFA best practices, OAuth/OIDC, secure session management
- **⚡ Authorization**: RBAC/ABAC, access control, IDOR prevention
- **📦 Supply Chain**: Dependency security, SBOM generation, vulnerability management
- **☁️ Cloud Security**: IaC hardening, container security, Kubernetes best practices
- **📱 Platform Security**: Mobile apps, web services, API security
- **🔍 Data Protection**: Privacy, encryption at rest/transit, secure storage

## Quick Start

Get started in minutes:

1. **Download the rules** from our [releases page](https://github.com/project-codeguard/rules/releases)
2. **Copy to your project** - Place IDE-specific rules in your repository
3. **Start coding** - AI assistants will automatically follow security best practices

[Get Started →](getting-started.md){ .md-button .md-button--primary }
[View on GitHub :material-github:](https://github.com/project-codeguard/rules){ .md-button }

## How It Works

1. **Security rules** are written in a unified markdown format
2. **Conversion tools** translate rules to IDE-specific formats
3. **AI assistants** reference these rules when generating or reviewing code
4. **Secure code** is produced automatically without developer intervention

## Community

- **📋 Issues**: [Report bugs or request features](https://github.com/project-codeguard/rules/issues)
- **💬 Discussions**: [Join the conversation](https://github.com/project-codeguard/rules/discussions)
- **🤝 Contributing**: [Learn how to contribute](https://github.com/project-codeguard/rules/blob/main/CONTRIBUTING.md)

## License

Project CodeGuard is released under the [Apache License](https://github.com/project-codeguard/rules/blob/main/LICENSE).

