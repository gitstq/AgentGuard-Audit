<div align="center">

# 🛡️ AgentGuard-Audit

**AI Agent Runtime Behavior Compliance Audit Engine**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

</div>

---

<a name="简体中文"></a>
## 🎉 项目介绍

**AgentGuard-Audit** 是一款专为 AI Agent 打造的运行时行为合规审计引擎。在 AI Agent 日益普及的今天，如何确保它们的行为符合预期、不泄露敏感信息、不被恶意利用，成为开发者和企业面临的重要挑战。

### 💡 核心价值

- 🔍 **实时监控**：在 Agent 运行时实时拦截和审计每一个行为
- ⚠️ **风险预警**：多维度风险检测，提前发现潜在问题
- 📊 **合规报告**：生成详细的审计报告，满足合规要求
- 🔌 **零侵入集成**：通过拦截器模式，无需修改现有代码

### ✨ 灵感来源

本项目灵感来源于 GitHub Trending 上的 [parlant](https://github.com/emcie-co/parlant) 和微软的 [ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners)，专注于解决 AI Agent 在生产环境中的行为合规审计问题。

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🛡️ **6+ 内置合规规则** | 敏感数据泄露、提示词注入、幻觉检测等 |
| 🧠 **高级启发式检测** | 基于模式识别的智能风险发现 |
| 📈 **多维度风险评分** | CRITICAL / HIGH / MEDIUM / LOW / INFO 五级风险 |
| 📄 **多种报告格式** | 控制台（彩色）、HTML（交互式）、JSON（机器可读）|
| 🔌 **拦截器模式** | 零侵入式集成，装饰器一键接入 |
| 🎯 **实时回调机制** | 风险实时通知，支持自定义处理逻辑 |
| 🪶 **零依赖设计** | 纯 Python 标准库实现，无外部依赖 |
| 🐍 **Python 3.8+** | 支持 Python 3.8 至 3.12 |

---

## 🚀 快速开始

### 环境要求

- Python >= 3.8
- 无其他依赖要求

### 安装

```bash
# 从 PyPI 安装（即将发布）
pip install agentguard-audit

# 或从源码安装
git clone https://github.com/gitstq/AgentGuard-Audit.git
cd AgentGuard-Audit
pip install -e .
```

### 基础用法

```python
from agentguard_audit import AuditEngine
from agentguard_audit.reporters import ConsoleReporter

# 1. 初始化审计引擎
engine = AuditEngine(
    agent_id="my-agent-001",
    agent_name="My AI Assistant",
)

# 2. 审计工具调用
event = engine.audit_tool_call(
    tool_name="weather-api",
    tool_input={"location": "Beijing"},
    tool_output={"temp": 25, "condition": "sunny"},
    latency_ms=150,
)

# 3. 审计 LLM 请求
event = engine.audit_llm_request(
    prompt="What's the weather?",
    response="It's sunny today.",
    token_count=150,
    latency_ms=500,
)

# 4. 生成报告
report = engine.generate_report()
reporter = ConsoleReporter()
print(reporter.generate(report))
```

### 拦截器模式（推荐）

```python
from agentguard_audit import AuditEngine, AgentInterceptor

engine = AuditEngine(agent_id="demo", agent_name="Demo Agent")
interceptor = AgentInterceptor(engine)

# 使用装饰器自动审计
@interceptor.intercept_tool(tool_name="search")
def search_web(query: str):
    return {"results": [f"Result for {query}"]}

@interceptor.intercept_llm()
def generate_response(prompt: str):
    return f"Response to: {prompt}"

# 调用函数时会自动审计
result = search_web("Python tutorials")
```

---

## 📖 详细使用指南

### CLI 工具

```bash
# 运行交互式演示
agentguard-audit demo

# 导出默认规则
agentguard-audit rules export --output rules.json

# 验证事件数据
agentguard-audit validate --rules rules.json --events events.json

# 生成报告
agentguard-audit report --input events.json --format html --output report.html
```

### 内置合规规则

| 规则 ID | 名称 | 风险级别 | 描述 |
|---------|------|----------|------|
| `sensitive_data_exposure` | 敏感数据泄露 | HIGH | 检测 PII、凭证、API Key 等 |
| `excessive_token_usage` | 超额 Token 使用 | MEDIUM | 监控 Token 消耗 |
| `unauthorized_tool_access` | 未授权工具访问 | CRITICAL | 控制工具权限 |
| `prompt_injection` | 提示词注入 | CRITICAL | 检测注入攻击 |
| `hallucination_risk` | 幻觉风险 | MEDIUM | 识别不确定性指标 |
| `response_latency` | 响应延迟 | LOW | 监控性能 |

### 自定义规则

```python
from agentguard_audit.models.compliance_rule import ComplianceRule, RuleCategory
from agentguard_audit.models.audit_event import RiskLevel

# 创建自定义规则
custom_rule = ComplianceRule(
    rule_id="no_external_apis",
    name="No External API Calls",
    description="禁止调用外部 API",
    category=RuleCategory.SECURITY,
    risk_level=RiskLevel.HIGH,
    config={"allowed_apis": ["weather-api"]},
)

engine.add_rule(custom_rule)
```

---

## 💡 设计思路与迭代规划

### 设计理念

1. **零侵入**：通过拦截器模式，不修改现有 Agent 代码
2. **零依赖**：纯 Python 标准库，降低集成成本
3. **可扩展**：插件化规则引擎，支持自定义检测逻辑
4. **实时性**：运行时审计，非事后分析

### 技术选型

- **纯 Python 实现**：无外部依赖，兼容性强
- **Dataclass 模型**：类型安全，性能优异
- **策略模式**：规则引擎易于扩展

### 后续迭代计划

- [ ] v1.1.0: 异步支持、Webhook 通知、LangChain 集成
- [ ] v1.2.0: 机器学习异常检测、SIEM 集成、合规模板
- [ ] v2.0.0: 多 Agent 编排审计、联邦合规报告

---

## 📦 打包与部署

### 作为库使用

```python
# requirements.txt
agentguard-audit>=1.0.0
```

### 开发安装

```bash
git clone https://github.com/gitstq/AgentGuard-Audit.git
cd AgentGuard-Audit
pip install -e ".[dev]"
```

### 运行测试

```bash
python -m pytest tests/
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

---

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

<a name="繁體中文"></a>
## 🎉 專案介紹（繁體中文）

**AgentGuard-Audit** 是一款專為 AI Agent 打造的執行時期行為合規審計引擎。在 AI Agent 日益普及的今天，如何確保它們的行為符合預期、不洩露敏感資訊、不被惡意利用，成為開發者和企業面臨的重要挑戰。

### 💡 核心價值

- 🔍 **即時監控**：在 Agent 執行時即時攔截和審計每一個行為
- ⚠️ **風險預警**：多維度風險檢測，提前發現潛在問題
- 📊 **合規報告**：生成詳細的審計報告，滿足合規要求
- 🔌 **零侵入整合**：通過攔截器模式，無需修改現有程式碼

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🛡️ **6+ 內建合規規則** | 敏感資料洩露、提示詞注入、幻覺檢測等 |
| 🧠 **進階啟發式檢測** | 基於模式識別的智慧風險發現 |
| 📈 **多維度風險評分** | CRITICAL / HIGH / MEDIUM / LOW / INFO 五級風險 |
| 📄 **多種報告格式** | 控制台（彩色）、HTML（互動式）、JSON（機器可讀）|
| 🔌 **攔截器模式** | 零侵入式整合，裝飾器一鍵接入 |
| 🎯 **即時回呼機制** | 風險即時通知，支援自定義處理邏輯 |
| 🪶 **零依賴設計** | 純 Python 標準庫實現，無外部依賴 |
| 🐍 **Python 3.8+** | 支援 Python 3.8 至 3.12 |

---

## 🚀 快速開始

### 環境要求

- Python >= 3.8
- 無其他依賴要求

### 安裝

```bash
pip install agentguard-audit
```

### 基礎用法

```python
from agentguard_audit import AuditEngine
from agentguard_audit.reporters import ConsoleReporter

# 初始化審計引擎
engine = AuditEngine(
    agent_id="my-agent-001",
    agent_name="My AI Assistant",
)

# 審計工具調用
event = engine.audit_tool_call(
    tool_name="weather-api",
    tool_input={"location": "Taipei"},
    tool_output={"temp": 28, "condition": "sunny"},
    latency_ms=150,
)

# 生成報告
report = engine.generate_report()
reporter = ConsoleReporter()
print(reporter.generate(report))
```

---

## 📄 開源協議

本專案採用 [MIT](LICENSE) 協議開源。

---

<a name="english"></a>
## 🎉 Project Introduction (English)

**AgentGuard-Audit** is a runtime behavior compliance audit engine designed specifically for AI Agents. As AI Agents become increasingly prevalent, ensuring they behave as expected, don't leak sensitive information, and aren't maliciously exploited has become a critical challenge for developers and enterprises.

### 💡 Core Values

- 🔍 **Real-time Monitoring**: Intercept and audit every behavior in real-time during Agent execution
- ⚠️ **Risk Alerting**: Multi-dimensional risk detection to identify potential issues early
- 📊 **Compliance Reporting**: Generate detailed audit reports to meet compliance requirements
- 🔌 **Zero-intrusion Integration**: Interceptor pattern requires no changes to existing code

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🛡️ **6+ Built-in Rules** | Sensitive data exposure, prompt injection, hallucination detection |
| 🧠 **Advanced Heuristics** | Pattern-based intelligent risk discovery |
| 📈 **Multi-dimensional Scoring** | CRITICAL / HIGH / MEDIUM / LOW / INFO risk levels |
| 📄 **Multiple Report Formats** | Console (colored), HTML (interactive), JSON (machine-readable) |
| 🔌 **Interceptor Pattern** | Zero-intrusion integration with decorator support |
| 🎯 **Real-time Callbacks** | Instant risk notifications with custom handling |
| 🪶 **Zero Dependencies** | Pure Python standard library, no external deps |
| 🐍 **Python 3.8+** | Supports Python 3.8 through 3.12 |

---

## 🚀 Quick Start

### Requirements

- Python >= 3.8
- No other dependencies required

### Installation

```bash
pip install agentguard-audit
```

### Basic Usage

```python
from agentguard_audit import AuditEngine
from agentguard_audit.reporters import ConsoleReporter

# Initialize audit engine
engine = AuditEngine(
    agent_id="my-agent-001",
    agent_name="My AI Assistant",
)

# Audit tool call
event = engine.audit_tool_call(
    tool_name="weather-api",
    tool_input={"location": "London"},
    tool_output={"temp": 15, "condition": "rainy"},
    latency_ms=150,
)

# Generate report
report = engine.generate_report()
reporter = ConsoleReporter()
print(reporter.generate(report))
```

### Interceptor Pattern (Recommended)

```python
from agentguard_audit import AuditEngine, AgentInterceptor

engine = AuditEngine(agent_id="demo", agent_name="Demo Agent")
interceptor = AgentInterceptor(engine)

# Use decorator for automatic auditing
@interceptor.intercept_tool(tool_name="search")
def search_web(query: str):
    return {"results": [f"Result for {query}"]}

@interceptor.intercept_llm()
def generate_response(prompt: str):
    return f"Response to: {prompt}"

# Calling functions automatically audits them
result = search_web("Python tutorials")
```

---

## 📖 Detailed Usage

### CLI Tool

```bash
# Run interactive demo
agentguard-audit demo

# Export default rules
agentguard-audit rules export --output rules.json

# Validate events
agentguard-audit validate --rules rules.json --events events.json

# Generate report
agentguard-audit report --input events.json --format html --output report.html
```

### Built-in Compliance Rules

| Rule ID | Name | Risk Level | Description |
|---------|------|------------|-------------|
| `sensitive_data_exposure` | Sensitive Data Exposure | HIGH | Detects PII, credentials, API keys |
| `excessive_token_usage` | Excessive Token Usage | MEDIUM | Monitors token consumption |
| `unauthorized_tool_access` | Unauthorized Tool Access | CRITICAL | Controls tool permissions |
| `prompt_injection` | Prompt Injection | CRITICAL | Detects injection attacks |
| `hallucination_risk` | Hallucination Risk | MEDIUM | Identifies uncertainty indicators |
| `response_latency` | Response Latency | LOW | Monitors performance |

---

## 💡 Design Philosophy

### Core Principles

1. **Zero-intrusion**: Interceptor pattern requires no changes to existing Agent code
2. **Zero-dependencies**: Pure Python standard library for easy integration
3. **Extensible**: Plugin-based rule engine supports custom detection logic
4. **Real-time**: Runtime auditing, not post-hoc analysis

### Roadmap

- [ ] v1.1.0: Async support, Webhook notifications, LangChain integration
- [ ] v1.2.0: ML-based anomaly detection, SIEM integration, compliance templates
- [ ] v2.0.0: Multi-agent orchestration auditing, federated compliance reporting

---

## 📄 License

This project is licensed under the [MIT](LICENSE) License.

---

<div align="center">

**Made with ❤️ by the Lobster Team**

⭐ Star us on GitHub — it motivates us a lot!

</div>
