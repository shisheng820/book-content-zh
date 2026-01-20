# Keybase Book 中文镜像站构建指南

本项目是 Keybase Book 的中文镜像站点，旨在为中文用户提供无障碍的文档阅读体验。

## 目录结构
*   `content/`: 存放 Markdown 格式的文档内容（需翻译）。
*   `templates/`: Jinja2 模板文件（已汉化 UI）。
*   `static/`: 静态资源（图片、CSS、JS）。
*   `build.py`: 静态网站构建脚本。
*   `dist/`: 构建生成的静态网站文件。

## 快速开始

### 1. 环境准备
确保已安装 Python 3.x。
安装依赖：
```bash
pip install -r requirements.txt
```

### 2. 构建网站
运行构建脚本，将 Markdown 和模板编译为静态 HTML：
```bash
python build.py
```
构建产物将位于 `dist/` 目录下。

### 3. 本地预览
在 `dist` 目录下启动 HTTP 服务器：
```bash
python -m http.server -d dist 8000
```
访问 `http://localhost:8000` 即可预览。

## 翻译指南

### 翻译原则 (信、达、雅)
1.  **术语一致性**：请参考根目录下的 `GLOSSARY.md`。
2.  **保留原文**：代码块、文件路径、API 链接、特定专有名词（如 Keybase, Sigchain）不予翻译。
3.  **双语对照**：对于首次出现的生僻概念，建议使用“中文 (English)”格式。

### 修改 Markdown 文件
Markdown 文件通常包含元数据（Metadata），例如：
```jinja2
{% set section_title = "Your Account" %}
{% set section_subtitle = "..." %}
```
请翻译引号内的文本，**不要**修改变量名（如 `section_title`）。

正文部分的翻译请直接替换英文文本，保留 Markdown 标记（如 `**粗体**`, `[链接](url)`）。

## 贡献
欢迎提交 PR 修复翻译错误或改进文档质量。
