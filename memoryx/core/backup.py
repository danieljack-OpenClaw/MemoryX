# -*- coding: utf-8 -*-
"""
MemoryX 增量备份模块
实现增量备份和恢复
"""
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any


class IncrementalBackup:
    """
    增量备份管理器
    
    支持:
    - 增量备份
    - 全量备份
    - 定时备份
    - 备份恢复
    - 备份验证
    """
    
    def __init__(self, storage_path: str = None, backup_path: str = None):
        if storage_path is None:
            from memoryx.core.config import Config
            config = Config()
            storage_path = str(config.storage_path)
        
        self.storage_path = Path(storage_path)
        
        if backup_path is None:
            backup_path = str(self.storage_path.parent / "memoryx_backup")
        
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # 备份元数据
        self.manifest_file = self.backup_path / "manifest.json"
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> dict:
        if self.manifest_file.exists():
            try:
                return json.loads(self.manifest_file.read_text(encoding='utf-8'))
            except:
                pass
        return {
            "backups": [],
            "last_full_backup": None,
            "last_incremental_backup": None
        }
    
    def _save_manifest(self):
        self.manifest_file.write_text(json.dumps(self.manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    def _get_source_files(self) -> List[Path]:
        """获取需要备份的源文件"""
        files = []
        
        # 记忆文件
        memory_dir = self.storage_path / "memories"
        if memory_dir.exists():
            files.extend(memory_dir.rglob("*.json"))
            files.extend(memory_dir.rglob("*.db"))
        
        # 向量存储
        vector_dir = self.storage_path / "vectors"
        if vector_dir.exists():
            files.extend(vector_dir.rglob("*.json"))
        
        # 图谱数据
        graph_dir = self.storage_path / "graph"
        if graph_dir.exists():
            files.extend(graph_dir.rglob("*.json"))
        
        # 配置
        config_file = self.storage_path / "config.json"
        if config_file.exists():
            files.append(config_file)
        
        # 统计
        stats_dir = self.storage_path / "stats"
        if stats_dir.exists():
            files.extend(stats_dir.rglob("*.json"))
        
        return files
    
    def create_full_backup(self, label: str = None) -> str:
        """
        创建全量备份
        
        Args:
            label: 备份标签
        
        Returns:
            backup_id
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"full_{timestamp}"
        
        if label:
            backup_id = f"{label}_{backup_id}"
        
        backup_dir = self.backup_path / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        files_backed = []
        files_failed = []
        
        for source_file in self._get_source_files():
            try:
                relative_path = source_file.relative_to(self.storage_path)
                target_file = backup_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(source_file, target_file)
                
                # 计算哈希
                file_hash = self._calculate_file_hash(source_file)
                
                files_backed.append({
                    "path": str(relative_path),
                    "hash": file_hash,
                    "size": source_file.stat().st_size
                })
            except Exception as e:
                files_failed.append({
                    "path": str(source_file),
                    "error": str(e)
                })
        
        # 创建元数据
        metadata = {
            "backup_id": backup_id,
            "type": "full",
            "created_at": datetime.now().isoformat(),
            "files": files_backed,
            "failed_files": files_failed,
            "total_size": sum(f["size"] for f in files_backed),
            "file_count": len(files_backed)
        }
        
        metadata_file = backup_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # 更新清单
        self.manifest["backups"].append(metadata)
        self.manifest["last_full_backup"] = backup_id
        self._save_manifest()
        
        return backup_id
    
    def create_incremental_backup(self, base_backup_id: str = None) -> str:
        """
        创建增量备份
        
        Args:
            base_backup_id: 基准备份 ID（从哪个备份开始增量）
        
        Returns:
            backup_id
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"incr_{timestamp}"
        
        # 确定基准备份
        if base_backup_id is None:
            base_backup_id = self.manifest.get("last_full_backup") or self.manifest.get("last_incremental_backup")
        
        # 获取基准备份的文件状态
        base_files = {}
        if base_backup_id:
            base_metadata = self._get_backup_metadata(base_backup_id)
            if base_metadata:
                base_files = {f["path"]: f["hash"] for f in base_metadata.get("files", [])}
        
        backup_dir = self.backup_path / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        files_backed = []
        files_changed = []
        files_failed = []
        
        # 备份自上次备份以来有变化的文件
        for source_file in self._get_source_files():
            try:
                relative_path = source_file.relative_to(self.storage_path)
                file_hash = self._calculate_file_hash(source_file)
                
                # 检查文件是否有变化
                path_str = str(relative_path)
                if path_str in base_files and base_files[path_str] == file_hash:
                    continue  # 没有变化，跳过
                
                # 有变化，备份
                target_file = backup_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                
                change_type = "added" if path_str not in base_files else "modified"
                files_backed.append({
                    "path": path_str,
                    "hash": file_hash,
                    "size": source_file.stat().st_size,
                    "change_type": change_type
                })
                
                if change_type == "modified":
                    files_changed.append(path_str)
                    
            except Exception as e:
                files_failed.append({
                    "path": str(source_file),
                    "error": str(e)
                })
        
        # 创建元数据
        metadata = {
            "backup_id": backup_id,
            "type": "incremental",
            "base_backup_id": base_backup_id,
            "created_at": datetime.now().isoformat(),
            "files": files_backed,
            "failed_files": files_failed,
            "total_size": sum(f["size"] for f in files_backed),
            "file_count": len(files_backed),
            "changed_files": files_changed
        }
        
        metadata_file = backup_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # 更新清单
        self.manifest["backups"].append(metadata)
        self.manifest["last_incremental_backup"] = backup_id
        self._save_manifest()
        
        return backup_id
    
    def _get_backup_metadata(self, backup_id: str) -> Optional[dict]:
        """获取备份元数据"""
        backup_dir = self.backup_path / backup_id
        metadata_file = backup_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            return json.loads(metadata_file.read_text(encoding='utf-8'))
        except:
            return None
    
    def restore_backup(self, backup_id: str, target_path: str = None) -> dict:
        """
        恢复备份
        
        Args:
            backup_id: 备份 ID
            target_path: 目标路径（恢复到哪里）
        
        Returns:
            恢复结果
        """
        if target_path is None:
            target_path = str(self.storage_path)
        
        target_path = Path(target_path)
        
        metadata = self._get_backup_metadata(backup_id)
        if not metadata:
            return {"success": False, "error": "Backup not found"}
        
        backup_dir = self.backup_path / backup_id
        
        result = {
            "backup_id": backup_id,
            "restored_at": datetime.now().isoformat(),
            "files_restored": [],
            "files_failed": [],
            "total_size": 0
        }
        
        # 如果是增量备份，需要先恢复基准备份
        if metadata.get("type") == "incremental":
            base_id = metadata.get("base_backup_id")
            if base_id:
                base_result = self.restore_backup(base_id, target_path)
                result["files_restored"].extend(base_result.get("files_restored", []))
        
        # 恢复当前备份的文件
        for file_info in metadata.get("files", []):
            try:
                source_file = backup_dir / file_info["path"]
                if not source_file.exists():
                    continue
                
                target_file = target_path / file_info["path"]
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                
                result["files_restored"].append(file_info["path"])
                result["total_size"] += file_info["size"]
            except Exception as e:
                result["files_failed"].append({
                    "path": file_info["path"],
                    "error": str(e)
                })
        
        return result
    
    def verify_backup(self, backup_id: str) -> dict:
        """
        验证备份完整性
        
        Args:
            backup_id: 备份 ID
        
        Returns:
            验证结果
        """
        metadata = self._get_backup_metadata(backup_id)
        if not metadata:
            return {"valid": False, "error": "Backup not found"}
        
        backup_dir = self.backup_path / backup_id
        
        result = {
            "backup_id": backup_id,
            "verified_at": datetime.now().isoformat(),
            "valid": True,
            "files_checked": 0,
            "files_failed": [],
            "total_size": 0
        }
        
        for file_info in metadata.get("files", []):
            try:
                file_path = backup_dir / file_info["path"]
                if not file_path.exists():
                    result["files_failed"].append({
                        "path": file_info["path"],
                        "error": "File missing"
                    })
                    result["valid"] = False
                    continue
                
                # 验证哈希
                current_hash = self._calculate_file_hash(file_path)
                if current_hash != file_info["hash"]:
                    result["files_failed"].append({
                        "path": file_info["path"],
                        "error": "Hash mismatch"
                    })
                    result["valid"] = False
                    continue
                
                result["files_checked"] += 1
                result["total_size"] += file_info["size"]
                
            except Exception as e:
                result["files_failed"].append({
                    "path": file_info["path"],
                    "error": str(e)
                })
                result["valid"] = False
        
        return result
    
    def list_backups(self, include_invalid: bool = False) -> List[dict]:
        """列出所有备份"""
        backups = []
        
        for backup_info in self.manifest.get("backups", []):
            if not include_invalid:
                # 验证备份是否有效
                backup_dir = self.backup_path / backup_info["backup_id"]
                if not backup_dir.exists():
                    continue
            
            backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        backup_dir = self.backup_path / backup_id
        
        if not backup_dir.exists():
            return False
        
        # 删除目录
        shutil.rmtree(backup_dir)
        
        # 从清单中移除
        self.manifest["backups"] = [
            b for b in self.manifest.get("backups", [])
            if b.get("backup_id") != backup_id
        ]
        
        if self.manifest.get("last_full_backup") == backup_id:
            self.manifest["last_full_backup"] = None
        
        if self.manifest.get("last_incremental_backup") == backup_id:
            self.manifest["last_incremental_backup"] = None
        
        self._save_manifest()
        
        return True
    
    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10) -> dict:
        """
        清理旧备份
        
        Args:
            keep_days: 保留多少天
            keep_count: 至少保留多少个
        
        Returns:
            清理结果
        """
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        backups = self.list_backups(include_invalid=True)
        
        deleted = []
        kept = []
        
        for backup in backups:
            created_at = datetime.fromisoformat(backup.get("created_at", "2000-01-01"))
            
            # 删除超过期限且超过保留数量的
            if created_at < cutoff_date and len(backups) - len(deleted) > keep_count:
                if self.delete_backup(backup.get("backup_id")):
                    deleted.append(backup.get("backup_id"))
            else:
                kept.append(backup.get("backup_id"))
        
        return {
            "deleted": deleted,
            "kept": kept,
            "deleted_count": len(deleted),
            "kept_count": len(kept)
        }
    
    def get_stats(self) -> dict:
        """获取备份统计"""
        backups = self.list_backups()
        
        total_size = sum(b.get("total_size", 0) for b in backups)
        total_files = sum(b.get("file_count", 0) for b in backups)
        
        return {
            "total_backups": len(backups),
            "total_size": total_size,
            "total_files": total_files,
            "last_full_backup": self.manifest.get("last_full_backup"),
            "last_incremental_backup": self.manifest.get("last_incremental_backup")
        }


# ============ 导出 ============

__all__ = [
    "IncrementalBackup"
]
