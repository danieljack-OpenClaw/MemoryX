# -*- coding: utf-8 -*-
"""
MemoryX 技能进化引擎
基于 GEP (Gene Evolution Protocol) 协议的自动进化
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class GeneType:
    """基因类型定义"""
    MEMORY = "memory"           # 记忆优化
    SKILL = "skill"            # 技能改进
    WORKFLOW = "workflow"      # 流程优化
    PERSONALITY = "personality" # 人格调整
    CONTEXT = "context"        # 上下文优化


class EvolutionEngine:
    """
    技能进化引擎
    
    基于 GEP 协议实现:
    1. 分析运行历史
    2. 提取进化信号
    3. 选择基因
    4. 生成进化方案
    5. 执行并审计
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            from memoryx.core.config import Config
            config = Config()
            storage_path = str(config.storage_path / "evolution")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 检查点目录
        self.checkpoints_dir = self.storage_path / "checkpoints"
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        # 基因库
        self.genes_file = self.storage_path / "genes.json"
        self.genes = self._load_genes()
        
        # 进化历史
        self.history_file = self.storage_path / "history.json"
        self.history = self._load_history()
    
    def _load_genes(self) -> dict:
        if self.genes_file.exists():
            try:
                return json.loads(self.genes_file.read_text(encoding='utf-8'))
            except:
                pass
        return self._default_genes()
    
    def _load_history(self) -> list:
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text(encoding='utf-8'))
            except:
                pass
        return []
    
    def _save_genes(self):
        self.genes_file.write_text(json.dumps(self.genes, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _save_history(self):
        self.history_file.write_text(json.dumps(self.history, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _default_genes(self) -> dict:
        """默认基因库"""
        return {
            "memory_optimization": {
                "type": GeneType.MEMORY,
                "name": "记忆优化基因",
                "description": "优化记忆存储和检索策略",
                "variants": [
                    {"id": "mem_v1", "name": "高频优先", "weight": 0.3},
                    {"id": "mem_v2", "name": "语义聚类", "weight": 0.4},
                    {"id": "mem_v3", "name": "时间衰减", "weight": 0.3}
                ]
            },
            "skill_improvement": {
                "type": GeneType.SKILL,
                "name": "技能改进基因",
                "description": "改进技能调用策略",
                "variants": [
                    {"id": "skill_v1", "name": "快速响应", "weight": 0.4},
                    {"id": "skill_v2", "name": "深度分析", "weight": 0.3},
                    {"id": "skill_v3", "name": "多步推理", "weight": 0.3}
                ]
            },
            "workflow_optimization": {
                "type": GeneType.WORKFLOW,
                "name": "流程优化基因",
                "description": "优化工作流程",
                "variants": [
                    {"id": "wf_v1", "name": "串行处理", "weight": 0.3},
                    {"id": "wf_v2", "name": "并行处理", "weight": 0.4},
                    {"id": "wf_v3", "name": "条件分支", "weight": 0.3}
                ]
            },
            "context_optimization": {
                "type": GeneType.CONTEXT,
                "name": "上下文优化基因",
                "description": "优化上下文管理",
                "variants": [
                    {"id": "ctx_v1", "name": "压缩优先", "weight": 0.5},
                    {"id": "ctx_v2", "name": "完整性优先", "weight": 0.3},
                    {"id": "ctx_v3", "name": "平衡策略", "weight": 0.2}
                ]
            }
        }
    
    def analyze_signals(self, agent_id: str, metrics: dict) -> dict:
        """
        分析进化信号
        
        Args:
            agent_id: Agent ID
            metrics: 运行指标 {
                "success_rate": float,
                "avg_response_time": float,
                "token_usage": float,
                "memory_hit_rate": float,
                "skill_accuracy": float
            }
        
        Returns:
            分析结果
        """
        signals = {
            "needs_memory_optimization": False,
            "needs_skill_improvement": False,
            "needs_workflow_optimization": False,
            "needs_context_optimization": False,
            "urgency": "low",  # low, medium, high
            "reason": []
        }
        
        # 分析指标并生成信号
        if metrics.get("memory_hit_rate", 1.0) < 0.5:
            signals["needs_memory_optimization"] = True
            signals["reason"].append(f"记忆命中率低: {metrics['memory_hit_rate']:.1%}")
        
        if metrics.get("success_rate", 1.0) < 0.7:
            signals["needs_skill_improvement"] = True
            signals["reason"].append(f"成功率低: {metrics['success_rate']:.1%}")
        
        if metrics.get("avg_response_time", 0) > 10.0:
            signals["needs_workflow_optimization"] = True
            signals["reason"].append(f"响应时间过长: {metrics['avg_response_time']:.1f}s")
        
        if metrics.get("token_usage", 0) > 150000:
            signals["needs_context_optimization"] = True
            signals["reason"].append(f"Token消耗过高: {metrics['token_usage']:,}")
        
        # 计算紧急程度
        signal_count = sum([
            signals["needs_memory_optimization"],
            signals["needs_skill_improvement"],
            signals["needs_workflow_optimization"],
            signals["needs_context_optimization"]
        ])
        
        if signal_count >= 3:
            signals["urgency"] = "high"
        elif signal_count >= 2:
            signals["urgency"] = "medium"
        else:
            signals["urgency"] = "low"
        
        return signals
    
    def select_genes(self, signals: dict) -> List[dict]:
        """
        根据信号选择基因
        
        Args:
            signals: 分析信号
        
        Returns:
            选中的基因列表
        """
        selected = []
        
        if signals.get("needs_memory_optimization"):
            gene = self.genes.get("memory_optimization", {})
            if gene:
                selected.append({
                    "gene_id": "memory_optimization",
                    "gene": gene,
                    "selected_variant": self._select_variant(gene)
                })
        
        if signals.get("needs_skill_improvement"):
            gene = self.genes.get("skill_improvement", {})
            if gene:
                selected.append({
                    "gene_id": "skill_improvement",
                    "gene": gene,
                    "selected_variant": self._select_variant(gene)
                })
        
        if signals.get("needs_workflow_optimization"):
            gene = self.genes.get("workflow_optimization", {})
            if gene:
                selected.append({
                    "gene_id": "workflow_optimization",
                    "gene": gene,
                    "selected_variant": self._select_variant(gene)
                })
        
        if signals.get("needs_context_optimization"):
            gene = self.genes.get("context_optimization", {})
            if gene:
                selected.append({
                    "gene_id": "context_optimization",
                    "gene": gene,
                    "selected_variant": self._select_variant(gene)
                })
        
        return selected
    
    def _select_variant(self, gene: dict) -> dict:
        """选择基因变体（基于权重随机）"""
        import random
        
        variants = gene.get("variants", [])
        if not variants:
            return {}
        
        total_weight = sum(v.get("weight", 0) for v in variants)
        if total_weight <= 0:
            return variants[0]
        
        r = random.random() * total_weight
        cumsum = 0
        
        for variant in variants:
            cumsum += variant.get("weight", 0)
            if cumsum >= r:
                return variant
        
        return variants[0]
    
    def generate_evolution_plan(self, agent_id: str, genes: List[dict]) -> dict:
        """
        生成进化方案
        
        Args:
            agent_id: Agent ID
            genes: 选中的基因
        
        Returns:
            进化方案
        """
        plan = {
            "agent_id": agent_id,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "genes": genes,
            "changes": [],
            "expected_improvement": {},
            "rollback_id": None
        }
        
        for gene_data in genes:
            gene = gene_data["gene"]
            variant = gene_data["selected_variant"]
            
            change = {
                "gene_id": gene_data["gene_id"],
                "gene_name": gene.get("name", ""),
                "variant_id": variant.get("id", ""),
                "variant_name": variant.get("name", ""),
                "type": gene.get("type", ""),
                "actions": self._generate_actions(gene.get("type", ""), variant)
            }
            
            plan["changes"].append(change)
        
        # 创建回滚点
        rollback_id = self.create_checkpoint(agent_id, f"pre_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        plan["rollback_id"] = rollback_id
        
        return plan
    
    def _generate_actions(self, gene_type: str, variant: dict) -> List[str]:
        """生成进化动作"""
        actions = []
        
        if gene_type == GeneType.MEMORY:
            if variant.get("id") == "mem_v1":
                actions = ["增加高频记忆权重", "调整检索算法"]
            elif variant.get("id") == "mem_v2":
                actions = ["启用语义聚类", "优化向量索引"]
            elif variant.get("id") == "mem_v3":
                actions = ["启用时间衰减", "调整遗忘曲线"]
        
        elif gene_type == GeneType.SKILL:
            if variant.get("id") == "skill_v1":
                actions = ["简化决策流程", "减少推理步骤"]
            elif variant.get("id") == "skill_v2":
                actions = ["增加深度分析", "启用多角度思考"]
            elif variant.get("id") == "skill_v3":
                actions = ["启用多步推理", "增加验证步骤"]
        
        elif gene_type == GeneType.CONTEXT:
            if variant.get("id") == "ctx_v1":
                actions = ["提高压缩率", "减少上下文长度"]
            elif variant.get("id") == "ctx_v2":
                actions = ["保留完整上下文", "增加关键信息"]
            elif variant.get("id") == "ctx_v3":
                actions = ["平衡压缩与完整", "智能选择性保留"]
        
        return actions
    
    def execute_evolution(self, plan: dict) -> dict:
        """
        执行进化方案
        
        Args:
            plan: 进化方案
        
        Returns:
            执行结果
        """
        result = {
            "plan": plan,
            "executed_at": datetime.now().isoformat(),
            "status": "success",
            "applied_changes": [],
            "errors": []
        }
        
        # 应用每个变更
        for change in plan.get("changes", []):
            try:
                # 这里应该实际应用变更到系统
                # 目前只是记录
                result["applied_changes"].append({
                    "gene_id": change["gene_id"],
                    "variant_id": change["variant_id"],
                    "status": "applied"
                })
            except Exception as e:
                result["errors"].append({
                    "gene_id": change["gene_id"],
                    "error": str(e)
                })
                result["status"] = "partial"
        
        # 记录历史
        self.history.append({
            "plan": plan,
            "result": result,
            "executed_at": result["executed_at"]
        })
        self._save_history()
        
        return result
    
    def create_checkpoint(self, agent_id: str, checkpoint_name: str) -> str:
        """
        创建检查点（回滚点）
        
        Args:
            agent_id: Agent ID
            checkpoint_name: 检查点名称
        
        Returns:
            checkpoint_id
        """
        checkpoint_id = hashlib.md5(
            f"{agent_id}_{checkpoint_name}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        
        checkpoint_path = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        checkpoint_data = {
            "id": checkpoint_id,
            "agent_id": agent_id,
            "name": checkpoint_name,
            "created_at": datetime.now().isoformat(),
            "genes": self.genes.copy()
        }
        
        checkpoint_path.write_text(json.dumps(checkpoint_data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        return checkpoint_id
    
    def rollback(self, checkpoint_id: str) -> bool:
        """
        回滚到检查点
        
        Args:
            checkpoint_id: 检查点 ID
        
        Returns:
            是否成功
        """
        checkpoint_path = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_path.exists():
            return False
        
        try:
            checkpoint_data = json.loads(checkpoint_path.read_text(encoding='utf-8'))
            self.genes = checkpoint_data.get("genes", self._default_genes())
            self._save_genes()
            return True
        except:
            return False
    
    def list_checkpoints(self, agent_id: str = None) -> List[dict]:
        """列出检查点"""
        checkpoints = []
        
        for f in self.checkpoints_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                if agent_id is None or data.get("agent_id") == agent_id:
                    checkpoints.append({
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "agent_id": data.get("agent_id"),
                        "created_at": data.get("created_at")
                    })
            except:
                pass
        
        return sorted(checkpoints, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def evolve(self, agent_id: str, metrics: dict) -> dict:
        """
        执行完整的进化流程
        
        Args:
            agent_id: Agent ID
            metrics: 运行指标
        
        Returns:
            进化结果
        """
        # 1. 分析信号
        signals = self.analyze_signals(agent_id, metrics)
        
        # 2. 选择基因
        genes = self.select_genes(signals)
        
        if not genes:
            return {
                "status": "no_evolution_needed",
                "signals": signals,
                "message": "没有检测到需要进化的问题"
            }
        
        # 3. 生成方案
        plan = self.generate_evolution_plan(agent_id, genes)
        
        # 4. 执行
        result = self.execute_evolution(plan)
        
        return {
            "status": "evolved",
            "signals": signals,
            "plan": plan,
            "result": result
        }
    
    def get_stats(self) -> dict:
        """获取进化统计"""
        return {
            "total_genes": len(self.genes),
            "total_evolutions": len(self.history),
            "checkpoints": len(list(self.checkpoints_dir.glob("*.json"))),
            "gene_types": {
                gene_id: gene.get("type", "")
                for gene_id, gene in self.genes.items()
            }
        }


# ============ 导出 ============

__all__ = [
    "GeneType",
    "EvolutionEngine"
]
