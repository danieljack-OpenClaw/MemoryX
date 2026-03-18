# MemoryX 安装指南

## 环境要求

- Python 3.10+
- pip
- 至少 2GB 内存 (推荐 4GB+)

## 安装步骤

### 1. 基础安装

```bash
pip install memoryx
```

### 2. 可选依赖

**向量数据库** (至少选择一个):

```bash
# ChromaDB (推荐)
pip install chromadb

# Qdrant
pip install qdrant-client

# Pinecone
pip install pinecone-client
```

**语义嵌入模型**:

```bash
pip install sentence-transformers
```

**LLM 摘要** (可选):

```bash
# OpenAI
pip install openai

# Anthropic
pip install anthropic

# Cohere
pip install cohere
```

**云端存储** (可选):

```bash
# AWS S3
pip install boto3

# Google Cloud Storage
pip install google-cloud-storage
```

### 3. 完整安装

```bash
pip install memoryx[all]
```

---

## 验证安装

```bash
python -c "from memoryx import MemoryX; print('MemoryX installed successfully!')"
```

或运行测试:

```bash
python -m memoryx.test
```

---

## 常见问题

### Q: 导入失败

A: 确保 Python 版本 >= 3.10

```bash
python --version
```

### Q: chromadb 导入失败

A: 安装 Microsoft Visual C++ Redistributable

### Q: sentence-transformers 下载慢

A: 设置 HuggingFace 镜像:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

---

## 下一步

- [快速开始](quickstart.md)
- [API 参考](api.md)
- [OpenClaw 集成](openclaw.md)
