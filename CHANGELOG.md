# MemoryX 更新日志

All notable changes to this project will be documented in this file.

---

## [1.0.2] - 2026-03-18

### 新增
- ☁️ **本地+云端双存储模式** (核心功能)
  - 默认本地存储
  - 配置云端后自动双写
  - 添加记忆时同时保存到本地和云端
- 🌐 Web Dashboard 云端存储配置 UI
- 📡 Settings API
- 🔧 云厂商连接测试
- 📖 云端配置文档

### 优化
- StorageManager 支持自动云同步
- CloudSync 支持单记忆上传/下载

---

## [1.0.1] - 2026-03-18

### 新增
- 🌐 Web Dashboard 多语言支持 (简体中文/繁体中文/English/Español/Português/Deutsch)
- ☁️ 云厂商反馈表单
- 🔧 端口配置支持

### 优化
- 默认端口调整

---

## [1.0.0] - 2026-03-18

### 新增
- 🎉 初始版本发布
- 🧠 多层级记忆系统
- ⚡ 90% Token 压缩
- 🔍 语义搜索
- 💾 自动备份
- ☁️ 云端同步 (6家厂商)

### 新增
- 🎉 **初始版本发布**
- 🧠 多层级记忆系统 (User/Session/Agent/Skill/Project)
- ⚡ **90% Token 压缩** (无需 LLM)
- 🔍 语义搜索 (paraphrase-multilingual-MiniLM, 384维, 83% 准确率)
- 💾 自动备份系统
- ☁️ 云端同步 (AWS S3 / Google Cloud Storage / 阿里云 OSS / 腾讯云 COS / 华为云 OBS / 百度云 BOS)
- 🎨 Web Dashboard 管理界面
- 🔄 技能进化引擎 (GEP 协议)
- 🤖 多 Agent 管理与记忆共享

### 技术特性
- 向量数据库: ChromaDB 支持
- 嵌入模型: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- LLM 集成: OpenAI GPT 支持 (可选)
- 存储: SQLite + 向量存储
- 多语言: 支持中英文语义

### 参考项目
- mem0 - Token 节省方案
- MemOS - OpenClaw 集成
- Evolver - GEP 进化协议
- sentence-transformers - 向量嵌入
- ChromaDB - 向量数据库

---

## [0.9.0] - 2026-03-17

### 开发中
- 基础框架搭建
- 核心记忆功能
- 压缩算法优化

---

*更多版本持续更新中...*
