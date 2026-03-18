"""
MemoryX 技能进化引擎
基于 GEP (Genome Evolution Protocol)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from ..core.config import Config
from ..core.memory import MemoryLevel


# 基因类型
class GeneType:
    MEMORY = "memory"      # 记忆优化
    SKILL = "skill"        # 技能改进
    WORKFLOW = "workflow"  # 流程优化
    PERSONALITY = "personality"  # 人格调整


@dataclass
class Gene:
    """基因"""
    id: str
    name: str
    description: str
    type: str
    payload: Dict
    validation: List[str] = field(default_factory=list)


@dataclass
class EvolutionEvent:
    """进化事件"""
    id: str
    agent_id: str
    genes: List[str]
    changes: Dict
    status: str  # pending / applied / validated / failed
    created_at: str
    applied_at: Optional[str] = None


class EvolutionEngine:
    """进化引擎"""
    
    # 内置基因库
    DEFAULT_GENES = {
        "memory_compress": Gene(
            id="memory_compress",
            name="记忆压缩优化",
            description="优化记忆压缩算法，减少token使用",
            type=GeneType.MEMORY,
            payload={"compression_level": "aggressive"},
            validation=["run_test", "check_token_usage"]
        ),
        "context_window": Gene(
            id="context_window",
            name="上下文窗口扩展",
            description="扩展上下文窗口以处理更长的任务",
            type=GeneType.MEMORY,
            payload={"window_size": 8000},
            validation=["test_long_context"]
        ),
        "semantic_search": Gene(
            id="semantic_search",
            name="语义搜索增强",
            description="改进语义搜索算法以提高准确率",
            type=GeneType.SKILL,
            payload={"search_depth": 10, "rerank": True},
            validation=["run_benchmark"]
        ),
        "skill_auto_update": Gene(
            id="skill_auto_update",
            name="技能自动更新",
            description="启用技能自动更新机制",
            type=GeneType.SKILL,
            payload={"enabled": True, "interval_hours": 24},
            validation=["check_update"]
        ),
        "error_recovery": Gene(
            id="error_recovery",
            name="错误恢复机制",
            description="添加自动错误检测和恢复",
            type=GeneType.WORKFLOW,
            payload={"retry_count": 3, "fallback": True},
            validation=["test_error_handling"]
        ),
        "personality_consistency": Gene(
            id="personality_consistency",
            name="人格一致性",
            description="强化人格特征的一致性",
            type=GeneType.PERSONALITY,
            payload={"strictness": 0.8},
            validation=["check_consistency"]
        ),
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.storage_path = config.storage_path / "evolution"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 加载基因库
        self.genes = dict(self.DEFAULT_GENES)
        self._load_genes()
    
    def _load_genes(self):
        """加载自定义基因"""
        genes_file = self.storage_path / "genes.json"
        
        if genes_file.exists():
            with open(genes_file) as f:
                custom_genes = json.load(f)
                for gene_data in custom_genes:
                    gene = Gene(**gene_data)
                    self.genes[gene.id] = gene
    
    def _save_genes(self):
        """保存基因"""
        genes_file = self.storage_path / "genes.json"
        
        genes_data = [gene.__dict__ for gene in self.genes.values()]
        with open(genes_file, "w") as f:
            json.dump(genes_data, f, ensure_ascii=False, indent=2)
    
    def evolve(self, agent_id: str, strategy: str = None) -> Dict:
        """
        执行进化
        
        Args:
            agent_id: Agent ID
            strategy: 进化策略 (balanced / innovate / harden / repair)
            
        Returns:
            Dict: 进化结果
        """
        strategy = strategy or self.config.evolution_strategy
        
        # 1. 分析运行历史
        signals = self._analyze_signals(agent_id)
        
        # 2. 选择基因
        selected_genes = self._select_genes(signals, strategy)
        
        # 3. 生成进化方案
        evolution_plan = self._generate_plan(agent_id, selected_genes)
        
        # 4. 创建进化事件
        event = EvolutionEvent(
            id=f"ev_{agent_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent_id=agent_id,
            genes=[g.id for g in selected_genes],
            changes=evolution_plan,
            status="pending",
            created_at=datetime.utcnow().isoformat()
        )
        
        # 5. 保存事件
        self._save_event(event)
        
        # 6. 执行进化 (可选)
        if self.config.evolution_strategy != "review_only":
            applied = self._apply_evolution(event)
            if applied:
                event.status = "applied"
                event.applied_at = datetime.utcnow().isoformat()
                self._save_event(event)
        
        return {
            "event_id": event.id,
            "strategy": strategy,
            "signals": signals,
            "genes": [g.id for g in selected_genes],
            "changes": evolution_plan,
            "status": event.status
        }
    
    def _analyze_signals(self, agent_id: str) -> Dict:
        """分析运行信号"""
        # 读取记忆/日志分析
        # 实际应分析真实运行数据
        
        return {
            "error_rate": 0.05,
            "token_usage": 0.7,
            "task_completion": 0.85,
            "response_quality": 0.75,
            "recent_issues": ["context_overflow", "slow_retrieval"]
        }
    
    def _select_genes(self, signals: Dict, strategy: str) -> List[Gene]:
        """选择基因"""
        selected = []
        
        if strategy == "innovate":
            # 创新模式: 选择更多新基因
            selected.extend([
                self.genes["semantic_search"],
                self.genes["skill_auto_update"]
            ])
        
        elif strategy == "harden":
            # 稳固模式: 强调稳定性
            selected.extend([
                self.genes["error_recovery"],
                self.genes["personality_consistency"]
            ])
        
        elif strategy == "repair":
            # 修复模式: 修复问题
            if signals.get("error_rate", 0) > 0.1:
                selected.append(self.genes["error_recovery"])
            if "context_overflow" in signals.get("recent_issues", []):
                selected.append(self.genes["memory_compress"])
        
        else:  # balanced
            # 平衡模式
            selected.extend([
                self.genes["memory_compress"],
                self.genes["semantic_search"]
            ])
        
        return selected
    
    def _generate_plan(self, agent_id: str, genes: List[Gene]) -> Dict:
        """生成进化计划"""
        changes = {}
        
        for gene in genes:
            changes[gene.id] = {
                "description": gene.description,
                "payload": gene.payload,
                "validation": gene.validation
            }
        
        return {
            "description": f"Apply {len(genes)} gene changes",
            "changes": changes,
            "expected_improvement": "TBD"
        }
    
    def _apply_evolution(self, event: EvolutionEvent) -> bool:
        """应用进化"""
        # 实际应根据 changes 执行
        return True
    
    def _save_event(self, event: EvolutionEvent):
        """保存进化事件"""
        events_file = self.storage_path / "events.jsonl"
        
        with open(events_file, "a") as f:
            f.write(json.dumps(event.__dict__, ensure_ascii=False) + "\n")
    
    def get_evolution_history(self, agent_id: str) -> List[Dict]:
        """获取进化历史"""
        events_file = self.storage_path / "events.jsonl"
        
        if not events_file.exists():
            return []
        
        events = []
        with open(events_file) as f:
            for line in f:
                event_data = json.loads(line)
                if event_data["agent_id"] == agent_id:
                    events.append(event_data)
        
        return events
    
    def checkpoint(self, agent_id: str) -> str:
        """创建检查点"""
        import shutil
        
        checkpoint_id = f"cp_{agent_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        checkpoint_path = self.storage_path / "checkpoints" / checkpoint_id
        
        # 复制当前状态
        if checkpoint_path.parent.exists():
            shutil.copytree(self.config.storage_path, checkpoint_path)
        
        return checkpoint_id
    
    def rollback(self, checkpoint_id: str) -> bool:
        """回滚到检查点"""
        checkpoint_path = self.storage_path / "checkpoints" / checkpoint_id
        
        if not checkpoint_path.exists():
            return False
        
        # 恢复状态
        import shutil
        shutil.copytree(checkpoint_path, self.config.storage_path, dirs_exist_ok=True)
        
        return True
    
    def register_gene(self, gene: Gene):
        """注册新基因"""
        self.genes[gene.id] = gene
        self._save_genes()
