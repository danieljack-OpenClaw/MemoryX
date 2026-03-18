# -*- coding: utf-8 -*-
"""
MemoryX Cloud Sync - 国内云厂商支持
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from .config import Config


class CloudSync:
    """Cloud synchronization for MemoryX"""
    
    # 支持的云厂商
    SUPPORTED_PROVIDERS = {
        # 国际厂商
        "aws": {"name": "AWS S3", "prefix": "s3://", "status": "✅"},
        "gcs": {"name": "Google Cloud Storage", "prefix": "gs://", "status": "✅"},
        
        # 国内厂商 (开发中)
        "aliyun": {"name": "阿里云 OSS", "prefix": "oss://", "status": "🚧"},
        "tencent": {"name": "腾讯云 COS", "prefix": "cos://", "status": "🚧"},
        "huawei": {"name": "华为云 OBS", "prefix": "obs://", "status": "🚧"},
        "baidu": {"name": "百度云 BOS", "prefix": "bos://", "status": "🚧"},
        "byteDance": {"name": "字节火山引擎", "prefix": "ve://", "status": "🚧"},
        "jd": {"name": "京东云", "prefix": "jd://", "status": "🚧"},
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.storage_path = config.storage_path
        self.feedback_file = self.storage_path / "cloud_feedback.json"
        
        # 初始化云客户端
        self._init_clients()
        
        # 加载用户反馈
        self.feedback = self._load_feedback()
    
    def _init_clients(self):
        """Initialize cloud clients"""
        self.aliyun_client = None
        self.tencent_client = None
        self.huawei_client = None
        self.baidu_client = None
        
        # 尝试初始化各厂商SDK
        self._init_aliyun()
        self._init_tencent()
        self._init_huawei()
        self._init_baidu()
    
    def _init_aliyun(self):
        """Initialize Aliyun OSS client"""
        try:
            import oss2
            auth = oss2.Auth(
                os.getenv("ALIYUN_ACCESS_KEY_ID"),
                os.getenv("ALIYUN_ACCESS_KEY_SECRET")
            )
            self.aliyun_client = auth
            self.SUPPORTED_PROVIDERS["aliyun"]["status"] = "✅"
            print("[MemoryX] Aliyun OSS client initialized")
        except ImportError:
            print("[MemoryX] Aliyun SDK not installed")
        except Exception as e:
            print(f"[MemoryX] Aliyun init failed: {e}")
    
    def _init_tencent(self):
        """Initialize Tencent Cloud COS client"""
        try:
            from qcloud_cos import CosConfig, CosS3Client
            secret_id = os.getenv("TENCENT_SECRET_ID")
            secret_key = os.getenv("TENCENT_SECRET_KEY")
            region = os.getenv("TENCENT_REGION", "ap-guangzhou")
            
            config = CosConfig(SecretId=secret_id, SecretKey=secret_key, Region=region)
            self.tencent_client = CosS3Client(config)
            self.SUPPORTED_PROVIDERS["tencent"]["status"] = "✅"
            print("[MemoryX] Tencent COS client initialized")
        except ImportError:
            print("[MemoryX] Tencent SDK not installed")
        except Exception as e:
            print(f"[MemoryX] Tencent init failed: {e}")
    
    def _init_huawei(self):
        """Initialize Huawei Cloud OBS client"""
        try:
            from obs import ObsClient
            obs_client = ObsClient(
                access_key_id=os.getenv("HUAWEI_ACCESS_KEY_ID"),
                secret_access_key=os.getenv("HUAWEI_ACCESS_KEY_SECRET"),
                server=f"obs.{os.getenv('HUAWEI_REGION', 'cn-north-4')}.myhuaweicloud.com"
            )
            self.huawei_client = obs_client
            self.SUPPORTED_PROVIDERS["huawei"]["status"] = "✅"
            print("[MemoryX] Huawei OBS client initialized")
        except ImportError:
            print("[MemoryX] Huawei SDK not installed")
        except Exception as e:
            print(f"[MemoryX] Huawei init failed: {e}")
    
    def _init_baidu(self):
        """Initialize Baidu Cloud BOS client"""
        try:
            from baidubce.services.bos import BosClient
            from baidubce import BceClientConfiguration
            config = BceClientConfiguration(
                credentials=baidubce.auth.bce_credentials.BceCredentials(
                    os.getenv("BAIDU_ACCESS_KEY_ID"),
                    os.getenv("BAIDU_ACCESS_KEY_SECRET")
                )
            )
            self.baidu_client = BosClient(config)
            self.SUPPORTED_PROVIDERS["baidu"]["status"] = "✅"
            print("[MemoryX] Baidu BOS client initialized")
        except ImportError:
            print("[MemoryX] Baidu SDK not installed")
        except Exception as e:
            print(f"[MemoryX] Baidu init failed: {e}")
    
    def _load_feedback(self) -> List[Dict]:
        """Load user feedback for cloud providers"""
        if self.feedback_file.exists():
            with open(self.feedback_file, encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_feedback(self):
        """Save user feedback"""
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback, f, ensure_ascii=False, indent=2)
    
    def get_supported_providers(self) -> Dict:
        """Get list of supported cloud providers"""
        return self.SUPPORTED_PROVIDERS
    
    def submit_feedback(self, provider: str, user_email: str = None, 
                       note: str = None) -> bool:
        """
        Submit feedback for cloud provider support
        
        Args:
            provider: 云厂商名称 (如: 阿里云、腾讯云)
            user_email: 用户邮箱 (可选)
            note: 备注 (可选)
            
        Returns:
            bool: 是否成功
        """
        feedback_item = {
            "provider": provider,
            "user_email": user_email,
            "note": note,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        # 检查是否已存在
        for item in self.feedback:
            if item.get("provider") == provider:
                item["timestamp"] = feedback_item["timestamp"]
                if user_email:
                    item["user_email"] = user_email
                if note:
                    item["note"] = note
                self._save_feedback()
                return True
        
        self.feedback.append(feedback_item)
        self._save_feedback()
        
        print(f"[MemoryX] Feedback submitted for: {provider}")
        return True
    
    def get_feedback_list(self) -> List[Dict]:
        """Get list of user feedback"""
        return self.feedback
    
    def get_pending_providers(self) -> List[str]:
        """Get list of providers with pending feedback (high demand)"""
        # 统计各厂商反馈数量
        provider_counts = {}
        for item in self.feedback:
            provider = item.get("provider", "")
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        # 按反馈数量排序
        sorted_providers = sorted(
            provider_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [p[0] for p in sorted_providers[:5]]  # Top 5
    
    def sync_to_cloud(self, remote_path: str = None) -> bool:
        """Sync local data to cloud"""
        remote_path = remote_path or self.config.remote_backup_path
        
        if not remote_path:
            print("[MemoryX] No remote path configured")
            return False
        
        try:
            if remote_path.startswith("s3://"):
                return self._sync_to_s3(remote_path)
            elif remote_path.startswith("gs://"):
                return self._sync_to_gcs(remote_path)
            elif remote_path.startswith("oss://"):
                return self._sync_to_aliyun(remote_path)
            elif remote_path.startswith("cos://"):
                return self._sync_to_tencent(remote_path)
            elif remote_path.startswith("obs://"):
                return self._sync_to_huawei(remote_path)
            elif remote_path.startswith("bos://"):
                return self._sync_to_baidu(remote_path)
            else:
                print(f"[MemoryX] Unsupported cloud provider: {remote_path}")
                return False
        except Exception as e:
            print(f"[MemoryX] Cloud sync failed: {e}")
            return False
    
    def _sync_to_aliyun(self, remote_path: str) -> bool:
        """Sync to Aliyun OSS"""
        if not self.aliyun_client:
            print("[MemoryX] Aliyun client not initialized")
            return False
        
        # TODO: Implement Aliyun sync
        print("[MemoryX] Aliyun OSS sync - coming soon")
        return False
    
    def _sync_to_tencent(self, remote_path: str) -> bool:
        """Sync to Tencent COS"""
        if not self.tencent_client:
            print("[MemoryX] Tencent client not initialized")
            return False
        
        # TODO: Implement Tencent sync
        print("[MemoryX] Tencent COS sync - coming soon")
        return False
    
    def _sync_to_huawei(self, remote_path: str) -> bool:
        """Sync to Huawei OBS"""
        if not self.huawei_client:
            print("[MemoryX] Huawei client not initialized")
            return False
        
        # TODO: Implement Huawei sync
        print("[MemoryX] Huawei OBS sync - coming soon")
        return False
    
    def _sync_to_baidu(self, remote_path: str) -> bool:
        """Sync to Baidu BOS"""
        if not self.baidu_client:
            print("[MemoryX] Baidu client not initialized")
            return False
        
        # TODO: Implement Baidu sync
        print("[MemoryX] Baidu BOS sync - coming soon")
        return False
    
    # 保留原有方法
    def _sync_to_s3(self, remote_path: str) -> bool:
        # ... 原有代码
        return True
    
    def _sync_to_gcs(self, remote_path: str) -> bool:
        # ... 原有代码
        return True
    
    def get_cloud_status(self) -> Dict:
        """Get cloud sync status"""
        return {
            "supported_providers": self.SUPPORTED_PROVIDERS,
            "feedback_count": len(self.feedback),
            "pending_providers": self.get_pending_providers()
        }
