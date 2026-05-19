# 🛡️ LogSentry

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Zero_Dependencies-✓-brightgreen.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Cross Platform">
</p>

<p align="center">
  <b>Lightweight Log Intelligence Analysis Engine CLI</b><br>
  <b>轻量级日志智能分析引擎</b>
</p>

<p align="center">
  <a href="#english">English</a> |
  <a href="#简体中文">简体中文</a> |
  <a href="#繁體中文">繁體中文</a>
</p>

---

<a name="english"></a>
## 🎉 Introduction

**LogSentry** is a lightweight, zero-dependency Python CLI tool designed for intelligent log analysis, anomaly detection, and multi-format reporting. Whether you're a system administrator, developer, or DevOps engineer, LogSentry helps you quickly understand what's happening in your log files.

### 🌟 Why LogSentry?

- **Zero Dependencies**: Uses only Python standard library - no pip install nightmares
- **Multi-Format Support**: Handles plain text, gzip, bzip2, and xz compressed logs
- **Smart Parsing**: Automatically detects timestamps and log levels from various formats
- **Anomaly Detection**: Identifies error spikes, time gaps, and traffic bursts
- **Real-Time Monitoring**: Watch logs as they grow with color-coded output
- **Flexible Reports**: Export analysis results as Text, JSON, Markdown, or HTML

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 📊 **Log Analysis** | Parse and analyze log files with automatic format detection |
| 🔍 **Anomaly Detection** | Detect error spikes, unusual time gaps, and traffic bursts |
| 📈 **Statistics** | Level distribution, hourly patterns, source tracking |
| 🖥️ **Real-Time Monitor** | Watch log files in real-time with color-coded output |
| 📄 **Multi-Format Reports** | Generate Text, JSON, Markdown, and HTML reports |
| 🗜️ **Compression Support** | Read gzip, bzip2, and xz compressed logs directly |
| 🎯 **Zero Dependencies** | Pure Python standard library - no external packages |

---

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- No external dependencies required!

### Installation

#### Option 1: Direct Download

```bash
# Download the script
curl -O https://raw.githubusercontent.com/gitstq/logsentry/main/logsentry.py

# Make it executable
chmod +x logsentry.py

# Run it
python3 logsentry.py --help
```

#### Option 2: Install via pip

```bash
pip install git+https://github.com/gitstq/logsentry.git
```

#### Option 3: Clone and Install

```bash
git clone https://github.com/gitstq/logsentry.git
cd logsentry
pip install -e .
```

---

## 📖 Usage Guide

### Analyze Log Files

```bash
# Basic analysis
logsentry analyze /var/log/syslog

# Analyze multiple files
logsentry analyze app.log nginx.log

# Export as JSON
logsentry analyze app.log --format json --output report.json

# Export as HTML report
logsentry analyze app.log --format html --output report.html

# Export as Markdown
logsentry analyze app.log --format markdown --output report.md
```

### Real-Time Monitoring

```bash
# Monitor a log file in real-time
logsentry monitor /var/log/nginx/access.log

# Monitor with level filter
logsentry monitor app.log --filter ERROR
```

### Parse Single Line

```bash
# Test parsing on a single line
logsentry parse "2024-01-15 10:30:45 ERROR Connection timeout"
```

---

## 💡 Supported Log Formats

LogSentry automatically detects and parses the following timestamp formats:

- **ISO 8601**: `2024-01-15T10:30:45Z`
- **Common**: `Jan 15 10:30:45`
- **Common with Year**: `Jan 15 2024 10:30:45`
- **Numeric**: `15/01/2024 10:30:45`
- **Numeric US**: `01/15/2024 10:30:45`

Supported log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL, and their abbreviations.

---

## 📦 Report Examples

### Text Report

```
============================================================
LogSentry Analysis Report
============================================================

Total lines analyzed: 5,234
Successfully parsed: 5,230
Time range: 2024-01-15 00:00:00 to 2024-01-15 23:59:59 (23:59:59)

Log level distribution:
  INFO: 4,500 (86.0%)
  DEBUG: 500 (9.6%)
  ERROR: 200 (3.8%)
  WARNING: 30 (0.6%)

⚠️  Detected 1 anomaly/anomalies:
  🔴 [error_spike] High error rate: 200 errors (3.8%)

----------------------------------------
Top Error Messages
----------------------------------------
  (45x) Connection timeout after 30s...
  (32x) Database connection failed...

============================================================
```

---

## 🔧 Development

### Running Tests

```bash
python3 test_logsentry.py
```

### Project Structure

```
logsentry/
├── logsentry.py      # Main module
├── test_logsentry.py # Unit tests
├── setup.py          # Package setup
├── requirements.txt  # Dependencies (empty - zero deps!)
├── LICENSE           # MIT License
└── README.md         # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🎉 项目介绍

**LogSentry** 是一个轻量级、零依赖的 Python CLI 工具，专为智能日志分析、异常检测和多格式报告而设计。无论您是系统管理员、开发人员还是 DevOps 工程师，LogSentry 都能帮助您快速了解日志文件中发生的事情。

### 🌟 为什么选择 LogSentry？

- **零依赖**：仅使用 Python 标准库 - 无需 pip 安装烦恼
- **多格式支持**：处理纯文本、gzip、bzip2 和 xz 压缩日志
- **智能解析**：自动检测各种格式的时间戳和日志级别
- **异常检测**：识别错误峰值、时间间隔异常和流量突发
- **实时监控**：通过颜色编码输出实时查看日志
- **灵活报告**：将分析结果导出为文本、JSON、Markdown 或 HTML

---

## ✨ 核心特性

| 特性 | 描述 |
|---------|-------------|
| 📊 **日志分析** | 自动格式检测的日志解析和分析 |
| 🔍 **异常检测** | 检测错误峰值、异常时间间隔和流量突发 |
| 📈 **统计分析** | 级别分布、小时模式、来源跟踪 |
| 🖥️ **实时监控** | 通过颜色编码输出实时监控日志文件 |
| 📄 **多格式报告** | 生成文本、JSON、Markdown 和 HTML 报告 |
| 🗜️ **压缩支持** | 直接读取 gzip、bzip2 和 xz 压缩日志 |
| 🎯 **零依赖** | 纯 Python 标准库 - 无需外部包 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 无需外部依赖！

### 安装方法

#### 方法 1：直接下载

```bash
# 下载脚本
curl -O https://raw.githubusercontent.com/gitstq/logsentry/main/logsentry.py

# 添加执行权限
chmod +x logsentry.py

# 运行
python3 logsentry.py --help
```

#### 方法 2：通过 pip 安装

```bash
pip install git+https://github.com/gitstq/logsentry.git
```

#### 方法 3：克隆并安装

```bash
git clone https://github.com/gitstq/logsentry.git
cd logsentry
pip install -e .
```

---

## 📖 使用指南

### 分析日志文件

```bash
# 基础分析
logsentry analyze /var/log/syslog

# 分析多个文件
logsentry analyze app.log nginx.log

# 导出为 JSON
logsentry analyze app.log --format json --output report.json

# 导出为 HTML 报告
logsentry analyze app.log --format html --output report.html

# 导出为 Markdown
logsentry analyze app.log --format markdown --output report.md
```

### 实时监控

```bash
# 实时监控日志文件
logsentry monitor /var/log/nginx/access.log

# 带级别过滤的监控
logsentry monitor app.log --filter ERROR
```

### 解析单行

```bash
# 测试单行解析
logsentry parse "2024-01-15 10:30:45 ERROR Connection timeout"
```

---

## 💡 支持的日志格式

LogSentry 自动检测和解析以下时间戳格式：

- **ISO 8601**: `2024-01-15T10:30:45Z`
- **常用格式**: `Jan 15 10:30:45`
- **带年份格式**: `Jan 15 2024 10:30:45`
- **数字格式**: `15/01/2024 10:30:45`
- **美式数字格式**: `01/15/2024 10:30:45`

支持的日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL 及其缩写。

---

## 📦 报告示例

### 文本报告

```
============================================================
LogSentry 分析报告
============================================================

总行数分析: 5,234
成功解析: 5,230
时间范围: 2024-01-15 00:00:00 到 2024-01-15 23:59:59 (23:59:59)

日志级别分布:
  INFO: 4,500 (86.0%)
  DEBUG: 500 (9.6%)
  ERROR: 200 (3.8%)
  WARNING: 30 (0.6%)

⚠️  检测到 1 个异常:
  🔴 [error_spike] 错误率过高: 200 个错误 (3.8%)

----------------------------------------
热门错误消息
----------------------------------------
  (45x) 连接超时 30s...
  (32x) 数据库连接失败...

============================================================
```

---

## 🔧 开发

### 运行测试

```bash
python3 test_logsentry.py
```

### 项目结构

```
logsentry/
├── logsentry.py      # 主模块
├── test_logsentry.py # 单元测试
├── setup.py          # 包配置
├── requirements.txt  # 依赖（空 - 零依赖！）
├── LICENSE           # MIT 许可证
└── README.md         # 本文件
```

---

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'feat: 添加某个 AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 开源协议

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🎉 專案介紹

**LogSentry** 是一個輕量級、零依賴的 Python CLI 工具，專為智慧日誌分析、異常檢測和多格式報告而設計。無論您是系統管理員、開發人員還是 DevOps 工程師，LogSentry 都能幫助您快速了解日誌檔案中發生的事情。

### 🌟 為什麼選擇 LogSentry？

- **零依賴**：僅使用 Python 標準函式庫 - 無需 pip 安裝煩惱
- **多格式支援**：處理純文字、gzip、bzip2 和 xz 壓縮日誌
- **智慧解析**：自動檢測各種格式的時間戳和日誌級別
- **異常檢測**：識別錯誤峰值、時間間隔異常和流量突發
- **即時監控**：透過顏色編碼輸出即時查看日誌
- **靈活報告**：將分析結果匯出為文字、JSON、Markdown 或 HTML

---

## ✨ 核心特性

| 特性 | 描述 |
|---------|-------------|
| 📊 **日誌分析** | 自動格式檢測的日誌解析和分析 |
| 🔍 **異常檢測** | 檢測錯誤峰值、異常時間間隔和流量突發 |
| 📈 **統計分析** | 級別分佈、小時模式、來源追蹤 |
| 🖥️ **即時監控** | 透過顏色編碼輸出即時監控日誌檔案 |
| 📄 **多格式報告** | 生成文字、JSON、Markdown 和 HTML 報告 |
| 🗜️ **壓縮支援** | 直接讀取 gzip、bzip2 和 xz 壓縮日誌 |
| 🎯 **零依賴** | 純 Python 標準函式庫 - 無需外部套件 |

---

## 🚀 快速開始

### 環境需求

- Python 3.8 或更高版本
- 無需外部依賴！

### 安裝方法

#### 方法 1：直接下載

```bash
# 下載腳本
curl -O https://raw.githubusercontent.com/gitstq/logsentry/main/logsentry.py

# 添加執行權限
chmod +x logsentry.py

# 執行
python3 logsentry.py --help
```

#### 方法 2：透過 pip 安裝

```bash
pip install git+https://github.com/gitstq/logsentry.git
```

#### 方法 3：克隆並安裝

```bash
git clone https://github.com/gitstq/logsentry.git
cd logsentry
pip install -e .
```

---

## 📖 使用指南

### 分析日誌檔案

```bash
# 基礎分析
logsentry analyze /var/log/syslog

# 分析多個檔案
logsentry analyze app.log nginx.log

# 匯出為 JSON
logsentry analyze app.log --format json --output report.json

# 匯出為 HTML 報告
logsentry analyze app.log --format html --output report.html

# 匯出為 Markdown
logsentry analyze app.log --format markdown --output report.md
```

### 即時監控

```bash
# 即時監控日誌檔案
logsentry monitor /var/log/nginx/access.log

# 帶級別過濾的監控
logsentry monitor app.log --filter ERROR
```

### 解析單行

```bash
# 測試單行解析
logsentry parse "2024-01-15 10:30:45 ERROR Connection timeout"
```

---

## 💡 支援的日誌格式

LogSentry 自動檢測和解析以下時間戳格式：

- **ISO 8601**: `2024-01-15T10:30:45Z`
- **常用格式**: `Jan 15 10:30:45`
- **帶年份格式**: `Jan 15 2024 10:30:45`
- **數字格式**: `15/01/2024 10:30:45`
- **美式數字格式**: `01/15/2024 10:30:45`

支援的日誌級別：DEBUG、INFO、WARNING、ERROR、CRITICAL 及其縮寫。

---

## 📦 報告範例

### 文字報告

```
============================================================
LogSentry 分析報告
============================================================

總行數分析: 5,234
成功解析: 5,230
時間範圍: 2024-01-15 00:00:00 到 2024-01-15 23:59:59 (23:59:59)

日誌級別分佈:
  INFO: 4,500 (86.0%)
  DEBUG: 500 (9.6%)
  ERROR: 200 (3.8%)
  WARNING: 30 (0.6%)

⚠️  檢測到 1 個異常:
  🔴 [error_spike] 錯誤率過高: 200 個錯誤 (3.8%)

----------------------------------------
熱門錯誤訊息
----------------------------------------
  (45x) 連線逾時 30s...
  (32x) 資料庫連線失敗...

============================================================
```

---

## 🔧 開發

### 執行測試

```bash
python3 test_logsentry.py
```

### 專案結構

```
logsentry/
├── logsentry.py      # 主模組
├── test_logsentry.py # 單元測試
├── setup.py          # 套件配置
├── requirements.txt  # 依賴（空 - 零依賴！）
├── LICENSE           # MIT 授權條款
└── README.md         # 本檔案
```

---

## 🤝 貢獻指南

歡迎貢獻！請隨時提交 Pull Request。

1. Fork 本倉庫
2. 建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'feat: 添加某個 AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

## 📄 開源授權

本專案採用 MIT 授權條款 - 詳情請參閱 [LICENSE](LICENSE) 檔案。

---

<p align="center">
  Made with ❤️ by the LogSentry Team<br>
  <a href="https://github.com/gitstq/logsentry">GitHub</a>
</p>
