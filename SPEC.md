# MemoryX - 下一代 AI Agent 记忆系统

> 整合 mem0 + MemOS + Evolver 三大方案的优点

## 📌 项目信息

- **项目名称**: MemoryX
- **定位**: 适用于 AI Agent 的下一代长期记忆系统
- **GitHub**: https://github.com/memoryX-ai/MemoryX
- **文档**: https://memoryx-ai.github.io/MemoryX

## 🎯 核心目标

1. **90% Token 节省** - 智能记忆压缩
2. **+40% 准确率提升** - 语义+图谱混合检索
3. **Skill 进化** - 基于 GEP 协议的自动进化
4. **多 Agent 协作** - 记忆共享与隔离
5. **生产级稳定性** - 自动备份、故障自愈

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      MemoryX                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   MemoryX Core                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ Token       │  │ Semantic    │  │ Graph       │  │  │
│  │  │ Compressor  │  │ Search      │  │ Memory      │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │         │                │                │           │  │
│  │         └────────────────┼────────────────┘           │  │
│  │                          ▼                            │  │
│  │  ┌─────────────────────────────────────────────┐      │  │
│  │  │           Memory Manager                     │      │  │
│  │  │  • 记忆存储 (SQLite + Vector)               │      │  │
│  │  │  • 智能压缩                                  │      │  │
│  │  │  • 自动过期                                  │      │  │
│  │  └─────────────────────────────────────────────┘      │  │
│  └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌───────────────────────┼───────────────────────┐       │
│  ▼                       ▼                       ▼       │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│ │  Evolution  │    │   Backup    │    │   Dashboard │   │
│ │   Engine    │    │   Manager   │    │   (Web UI)  │   │
│ │ (GEP Proto) │    │ (Auto/S3)   │    │             │   │
│ └─────────────┘    └─────────────┘    └─────────────┘   │
│                          │                                  │
│  ┌───────────────────────┴───────────────────────┐         │
│  ▼                                               ▼         │
│ ┌─────────────┐                           ┌─────────────┐ │
│ │   OpenClaw  │                           │   Multi     │ │
│ │   Plugin    │                           │   Agent     │ │
│ └─────────────┘                           └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 核心功能

### 1. 多层级记忆系统

| 层级 | 作用域 | 生命周期 | 用途 |
|------|--------|----------|------|
| **User** | 用户级别 | 永久 | 用户偏好、长期目标 |
| **Session** | 会话级别 | 会话期间 | 当前任务上下文 |
| **Agent** | Agent 级别 | 永久 | Agent 技能、知识 |
| **Skill** | 技能级别 | 技能存在期间 | 技能特定记忆 |
| **Project** | 项目级别 | 项目期间 | 项目特定记忆 |

### 2. Token 智能压缩

```python
class TokenCompressor:
    """90% Token 节省的智能压缩"""
    
    def compress(self, messages: list) -> str:
        """压缩对话历史"""
        # 1. 提取关键信息
        # 2. 去除冗余
        # 3. 语义摘要
        # 4. 保留核心要点
        
    def expand(self, memory: str, query: str) -> str:
        """根据查询展开记忆"""
        # 1. 语义检索相关记忆
        # 2. 补充上下文
```

### 3. 技能进化引擎 (GEP Protocol)

```python
class EvolutionEngine:
    """基于 GEP 协议的技能进化"""
    
    # 基因类型
    GENES = {
        "memory": "记忆优化",
        "skill": "技能改进",
        "workflow": "流程优化",
        "personality": "人格调整",
    }
    
    def evolve(self, agent_id: str):
        """执行进化"""
        # 1. 分析运行历史
        # 2. 提取进化信号
        # 3. 选择基因
        # 4. 生成进化方案
        # 5. 执行并审计
        
    def checkpoint(self):
        """创建检查点"""
        
    def rollback(self, checkpoint_id: str):
        """回滚到检查点"""
```

### 4. 向量 + 图谱混合存储

```python
class HybridStorage:
    """向量 + 知识图谱混合存储"""
    
    # 向量存储: 语义搜索
    vector_db: ChromaDB
    
    # 图谱存储: 关系推理
    graph_db: NetworkX / Neo4j
    
    # SQLite: 结构化数据
    sql_db: SQLite
```

### 5. 多 Agent 支持

```python
class MultiAgentManager:
    """多 Agent 记忆管理"""
    
    def share_memory(self, from_agent: str, to_agent: str, memory_id: str):
        """记忆共享"""
        
    def isolate_memory(self, agent_id: str):
        """记忆隔离"""
        
    def merge_knowledge(self, agent_ids: list):
        """知识合并"""
```

### 6. 自动备份系统

```python
class BackupManager:
    """自动备份管理"""
    
    # 本地备份
    local_backup: Path
    
    # 远程备份 (可选)
    remote_backup: S3 / GCS
    
    def auto_backup(self):
        """定时自动备份"""
        
    def restore(self, backup_id: str):
        """恢复备份"""
        
    def incremental_backup(self):
        """增量备份"""
```

---

## 📊 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| Token 节省 | 85-90% | 相比全上下文 |
| 检索延迟 | <100ms | 语义检索 |
| 准确率提升 | +40% | 相比无记忆 |
| 可用性 | 99.9% | 自动备份保障 |
| 存储效率 | 10x | 智能压缩 |

---

## 🔌 集成

### OpenClaw Plugin

```yaml
# openclaw 集成配置
plugins:
  memoryx:
    enabled: true
    api_key: ${MEMORYX_API_KEY}
    # 本地模式
    local:
      storage_path: ~/.memoryx
    # 云端模式
    cloud:
      endpoint: https://api.memoryx.ai
```

### API 接口

```bash
# 存储记忆
POST /memory
{
  "user_id": "user_123",
  "content": "用户喜欢在下午2点开会",
  "type": "preference"
}

# 检索记忆
GET /memory?user_id=user_123&query=会议时间

# 技能进化
POST /evolve
{
  "agent_id": "agent_456"
}

# 备份
POST /backup
```

---

## 📦 项目结构

```
MemoryX/
├── src/
│   ├── core/
│   │   ├── memory.py       # 核心记忆类
│   │   ├── compressor.py   # Token 压缩
│   │   ├── search.py       # 语义搜索
│   │   └── graph.py        # 知识图谱
│   ├── evolution/
│   │   ├── engine.py       # 进化引擎
│   │   ├── genes.py        # 基因定义
│   │   └── audit.py        # 进化审计
│   ├── backup/
│   │   ├── manager.py      # 备份管理
│   │   └── storage.py      # 存储后端
│   ├── agent/
│   │   ├── manager.py      # 多 Agent 管理
│   │   └── sharing.py      # 记忆共享
│   └── api/
│       ├── server.py       # REST API
│       └── openclaw.py    # OpenClaw 插件
├── web/
│   └── dashboard/          # Web 管理界面
├── tests/
├── docs/
├── SPEC.md
├── README.md
└── requirements.txt
```

---

## 🚀 快速开始

### 安装

```bash
pip install memoryx
```

### 使用

```python
from memoryx import MemoryX

# 初始化
memory = MemoryX(api_key="your-key")

# 存储记忆
memory.add(
    user_id="user_123",
    content="用户喜欢简洁的沟通风格"
)

# 检索记忆
results = memory.search(
    user_id="user_123",
    query="沟通偏好"
)

# 技能进化
memory.evolve(agent_id="agent_456")
```

---

## 📋 开发计划

### Phase 1: 核心功能 (MVP)
- [x] 项目初始化
- [x] 多层级记忆 CRUD
- [x] Token 压缩
- [x] 语义检索
- [x] 基础 API

### Phase 2: 高级功能
- [x] 技能进化引擎
- [x] 知识图谱
- [x] 多 Agent 支持
- [x] 自动备份

### Phase 3: 生态集成
- [x] OpenClaw 插件
- [x] Web Dashboard
- [x] 云端同步
- [x] 更多 Provider 支持

---

## 📜 License

Apache 2.0

---

*MemoryX - 让 AI Agent 拥有真正的长期记忆*
