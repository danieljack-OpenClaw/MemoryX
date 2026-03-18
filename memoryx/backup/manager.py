"""
MemoryX 备份管理
支持本地和远程自动备份
"""

import json
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import zipfile

from ..core.config import Config


class BackupManager:
    """备份管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.backup_path = config.storage_path / "backups"
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def backup(self, remote: bool = False, incremental: bool = False) -> str:
        """
        创建备份
        
        Args:
            remote: 是否远程备份
            incremental: 是否增量备份
            
        Returns:
            str: 备份 ID
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}"
        
        if incremental:
            backup_file = self.backup_path / f"{backup_id}.zip"
            self._incremental_backup(backup_file)
        else:
            backup_file = self.backup_path / f"{backup_id}.zip"
            self._full_backup(backup_file)
        
        # 计算校验和
        checksum = self._calculate_checksum(backup_file)
        
        # 记录元数据
        metadata = {
            "id": backup_id,
            "file": str(backup_file),
            "checksum": checksum,
            "size": backup_file.stat().st_size,
            "created_at": datetime.utcnow().isoformat(),
            "type": "incremental" if incremental else "full",
            "status": "completed"
        }
        
        self._save_metadata(metadata)
        
        # 远程备份
        if remote and self.config.remote_backup_enabled:
            self._remote_backup(backup_file, backup_id)
        
        # 清理旧备份
        self._cleanup_old_backups()
        
        return backup_id
    
    def _full_backup(self, backup_file: Path):
        """完整备份"""
        with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zf:
            # 备份数据库
            db_path = self.config.storage_path / "memoryx.db"
            if db_path.exists():
                zf.write(db_path, "memoryx.db")
            
            # 备份向量数据
            vector_path = self.config.storage_path / "vector_db"
            if vector_path.exists():
                for file in vector_path.rglob("*"):
                    if file.is_file():
                        zf.write(file, f"vector_db/{file.name}")
            
            # 备份图数据
            graph_path = self.config.storage_path / "graph"
            if graph_path.exists():
                for file in graph_path.rglob("*"):
                    if file.is_file():
                        zf.write(file, f"graph/{file.name}")
            
            # 备份进化数据
            evolution_path = self.config.storage_path / "evolution"
            if evolution_path.exists():
                for file in evolution_path.rglob("*"):
                    if file.is_file():
                        zf.write(file, f"evolution/{file.name}")
    
    def _incremental_backup(self, backup_file: Path):
        """增量备份"""
        # 获取上次备份时间
        last_backup = self._get_last_backup()
        
        with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zf:
            # 备份数据库变更
            db_path = self.config.storage_path / "memoryx.db"
            if db_path.exists():
                # 只备份修改过的文件
                if last_backup:
                    # 简单处理：直接备份完整数据库
                    zf.write(db_path, "memoryx.db")
                else:
                    zf.write(db_path, "memoryx.db")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _save_metadata(self, metadata: Dict):
        """保存备份元数据"""
        metadata_file = self.backup_path / "metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file) as f:
                all_metadata = json.load(f)
        else:
            all_metadata = []
        
        all_metadata.append(metadata)
        
        with open(metadata_file, "w") as f:
            json.dump(all_metadata, f, indent=2)
    
    def _get_last_backup(self) -> Optional[Dict]:
        """获取上次备份信息"""
        metadata_file = self.backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file) as f:
            all_metadata = json.load(f)
        
        if all_metadata:
            return all_metadata[-1]
        
        return None
    
    def restore(self, backup_id: str) -> bool:
        """
        恢复备份
        
        Args:
            backup_id: 备份 ID
            
        Returns:
            bool: 是否成功
        """
        # 查找备份文件
        backup_file = self.backup_path / f"{backup_id}.zip"
        
        if not backup_file.exists():
            # 尝试远程恢复
            if self.config.remote_backup_enabled:
                if self._remote_restore(backup_id):
                    backup_file = self.backup_path / f"{backup_id}.zip"
                else:
                    return False
            else:
                return False
        
        # 验证校验和
        checksum = self._calculate_checksum(backup_file)
        metadata = self._get_backup_metadata(backup_id)
        
        if metadata and checksum != metadata.get("checksum"):
            return False
        
        # 解压到临时目录
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(backup_file, "r") as zf:
                zf.extractall(temp_dir)
            
            # 备份当前数据
            current_backup = self.backup_path / "pre_restore"
            if self.config.storage_path.exists():
                shutil.copytree(self.config.storage_path, current_backup)
            
            try:
                # 恢复数据
                temp_path = Path(temp_dir)
                
                # 恢复数据库
                db_file = temp_path / "memoryx.db"
                if db_file.exists():
                    shutil.copy(db_file, self.config.storage_path / "memoryx.db")
                
                # 恢复向量数据
                vector_dir = temp_path / "vector_db"
                if vector_dir.exists():
                    target_vector = self.config.storage_path / "vector_db"
                    if target_vector.exists():
                        shutil.rmtree(target_vector)
                    shutil.copytree(vector_dir, target_vector)
                
                # 恢复图数据
                graph_dir = temp_path / "graph"
                if graph_dir.exists():
                    target_graph = self.config.storage_path / "graph"
                    if target_graph.exists():
                        shutil.rmtree(target_graph)
                    shutil.copytree(graph_dir, target_graph)
                
                # 恢复进化数据
                evolution_dir = temp_path / "evolution"
                if evolution_dir.exists():
                    target_evolution = self.config.storage_path / "evolution"
                    if target_evolution.exists():
                        shutil.rmtree(target_evolution)
                    shutil.copytree(evolution_dir, target_evolution)
                
                return True
            
            except Exception as e:
                print(f"Restore failed: {e}")
                # 恢复失败时，可以使用 pre_restore 恢复
                return False
    
    def _get_backup_metadata(self, backup_id: str) -> Optional[Dict]:
        """获取备份元数据"""
        metadata_file = self.backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file) as f:
            all_metadata = json.load(f)
        
        for metadata in all_metadata:
            if metadata["id"] == backup_id:
                return metadata
        
        return None
    
    def _remote_backup(self, backup_file: Path, backup_id: str):
        """远程备份"""
        # 支持 S3, GCS, Azure Blob 等
        # 这里以 S3 为例
        remote_path = self.config.remote_backup_path
        
        if not remote_path:
            return
        
        try:
            if remote_path.startswith("s3://"):
                self._backup_to_s3(backup_file, remote_path)
            elif remote_path.startswith("gs://"):
                self._backup_to_gcs(backup_file, remote_path)
            else:
                print(f"Unsupported remote path: {remote_path}")
        except Exception as e:
            print(f"Remote backup failed: {e}")
    
    def _backup_to_s3(self, backup_file: Path, remote_path: str):
        """备份到 S3"""
        try:
            import boto3
            
            # 解析 S3 路径
            path = remote_path.replace("s3://", "")
            bucket, key = path.split("/", 1)
            key = f"{key}/{backup_file.name}"
            
            s3 = boto3.client("s3")
            s3.upload_file(str(backup_file), bucket, key)
        except ImportError:
            print("boto3 not installed, skipping S3 backup")
    
    def _backup_to_gcs(self, backup_file: Path, remote_path: str):
        """备份到 GCS"""
        try:
            from google.cloud import storage
            
            path = remote_path.replace("gs://", "")
            bucket, prefix = path.split("/", 1)
            blob_name = f"{prefix}/{backup_file.name}"
            
            client = storage.Client()
            bucket = client.bucket(bucket)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(str(backup_file))
        except ImportError:
            print("google-cloud-storage not installed, skipping GCS backup")
    
    def _remote_restore(self, backup_id: str) -> bool:
        """从远程恢复"""
        # 类似 remote_backup 的逆向操作
        return False
    
    def _cleanup_old_backups(self):
        """清理旧备份"""
        retention_days = self.config.backup_retention_days
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        
        metadata_file = self.backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return
        
        with open(metadata_file) as f:
            all_metadata = json.load(f)
        
        # 过滤保留的备份
        kept = []
        for metadata in all_metadata:
            created = datetime.fromisoformat(metadata["created_at"])
            if created > cutoff:
                kept.append(metadata)
            else:
                # 删除旧备份文件
                backup_file = Path(metadata["file"])
                if backup_file.exists():
                    backup_file.unlink()
        
        # 保存更新后的元数据
        with open(metadata_file, "w") as f:
            json.dump(kept, f, indent=2)
    
    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        metadata_file = self.backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return []
        
        with open(metadata_file) as f:
            return json.load(f)
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        metadata = self._get_backup_metadata(backup_id)
        
        if not metadata:
            return False
        
        # 删除文件
        backup_file = Path(metadata["file"])
        if backup_file.exists():
            backup_file.unlink()
        
        # 更新元数据
        metadata_file = self.backup_path / "metadata.json"
        with open(metadata_file) as f:
            all_metadata = json.load(f)
        
        all_metadata = [m for m in all_metadata if m["id"] != backup_id]
        
        with open(metadata_file, "w") as f:
            json.dump(all_metadata, f, indent=2)
        
        return True
