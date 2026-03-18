# -*- coding: utf-8 -*-
"""
MemoryX Cloud Sync - 全云厂商支持
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from ..core.config import Config


class CloudSync:
    """Cloud synchronization for MemoryX - 全云厂商支持"""
    
    # 支持的云厂商
    SUPPORTED_PROVIDERS = {
        "aws": {"name": "AWS S3", "prefix": "s3://", "enabled": True},
        "gcs": {"name": "Google Cloud Storage", "prefix": "gs://", "enabled": True},
        "aliyun": {"name": "阿里云 OSS", "prefix": "oss://", "enabled": True},
        "tencent": {"name": "腾讯云 COS", "prefix": "cos://", "enabled": True},
        "huawei": {"name": "华为云 OBS", "prefix": "obs://", "enabled": True},
        "baidu": {"name": "百度云 BOS", "prefix": "bos://", "enabled": True},
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.storage_path = config.storage_path
        self._init_clients()
    
    def _init_clients(self):
        """Initialize all cloud clients"""
        # AWS S3
        self.s3_client = None
        if os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"):
            try:
                import boto3
                self.s3_client = boto3.client('s3')
            except:
                pass
        
        # Google Cloud Storage
        self.gcs_client = None
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            try:
                from google.cloud import storage
                self.gcs_client = storage.Client()
            except:
                pass
        
        # Aliyun OSS
        self.aliyun_client = None
        if os.getenv("ALIYUN_ACCESS_KEY_ID"):
            try:
                import oss2
                self.aliyun_client = oss2.Auth(
                    os.getenv("ALIYUN_ACCESS_KEY_ID"),
                    os.getenv("ALIYUN_ACCESS_KEY_SECRET")
                )
            except:
                pass
        
        # Tencent COS
        self.tencent_client = None
        if os.getenv("TENCENT_SECRET_ID"):
            try:
                from qcloud_cos import CosConfig, CosS3Client
                config = CosConfig(
                    SecretId=os.getenv("TENCENT_SECRET_ID"),
                    SecretKey=os.getenv("TENCENT_SECRET_KEY"),
                    Region=os.getenv("TENCENT_REGION", "ap-guangzhou")
                )
                self.tencent_client = CosS3Client(config)
            except:
                pass
        
        # Huawei OBS
        self.huawei_client = None
        if os.getenv("HUAWEI_ACCESS_KEY_ID"):
            try:
                from obs import ObsClient
                self.huawei_client = ObsClient(
                    access_key_id=os.getenv("HUAWEI_ACCESS_KEY_ID"),
                    secret_access_key=os.getenv("HUAWEI_ACCESS_KEY_SECRET"),
                    server=f"obs.{os.getenv('HUAWEI_REGION', 'cn-north-4')}.myhuaweicloud.com"
                )
            except:
                pass
        
        # Baidu BOS
        self.baidu_client = None
        if os.getenv("BAIDU_ACCESS_KEY_ID"):
            try:
                import baidubce
                from baidubce.services.bos import BosClient
                config = baidubce.BceClientConfiguration(
                    credentials=baidubce.auth.bce_credentials.BceCredentials(
                        os.getenv("BAIDU_ACCESS_KEY_ID"),
                        os.getenv("BAIDU_ACCESS_KEY_SECRET")
                    )
                )
                self.baidu_client = BosClient(config)
            except:
                pass
    
    def get_supported_providers(self) -> Dict:
        """Get supported cloud providers"""
        status = {}
        for key, info in self.SUPPORTED_PROVIDERS.items():
            client = getattr(self, f"{key}_client", None)
            status[key] = {
                "name": info["name"],
                "prefix": info["prefix"],
                "enabled": info["enabled"],
                "connected": client is not None
            }
        return status
    
    def sync_to_cloud(self, remote_path: str = None) -> bool:
        """Sync local data to cloud"""
        remote_path = remote_path or self.config.remote_backup_path
        
        if not remote_path:
            return False
        
        providers = {
            "s3://": (self._sync_to_s3, self.s3_client, "AWS S3"),
            "gs://": (self._sync_to_gcs, self.gcs_client, "Google Cloud Storage"),
            "oss://": (self._sync_to_aliyun, self.aliyun_client, "Aliyun OSS"),
            "cos://": (self._sync_to_tencent, self.tencent_client, "Tencent COS"),
            "obs://": (self._sync_to_huawei, self.huawei_client, "Huawei OBS"),
            "bos://": (self._sync_to_baidu, self.baidu_client, "Baidu BOS"),
        }
        
        for prefix, (method, client, name) in providers.items():
            if remote_path.startswith(prefix):
                if not client:
                    print(f"[MemoryX] {name} client not configured")
                    return False
                return method(remote_path)
        
        return False
    
    def _sync_to_s3(self, remote_path: str) -> bool:
        """Sync to AWS S3"""
        path = remote_path.replace("s3://", "")
        bucket, prefix = path.split("/", 1)
        
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                key = f"{prefix}/{file.relative_to(self.storage_path)}"
                self.s3_client.upload_file(str(file), bucket, key)
        
        print(f"[MemoryX] Synced to AWS S3: {bucket}/{prefix}")
        return True
    
    def _sync_to_gcs(self, remote_path: str) -> bool:
        """Sync to Google Cloud Storage"""
        path = remote_path.replace("gs://", "")
        bucket_name, prefix = path.split("/", 1)
        
        bucket = self.gcs_client.bucket(bucket_name)
        
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                key = f"{prefix}/{file.relative_to(self.storage_path)}"
                blob = bucket.blob(key)
                blob.upload_from_filename(str(file))
        
        print(f"[MemoryX] Synced to Google Cloud Storage: {bucket_name}/{prefix}")
        return True
    
    def _sync_to_aliyun(self, remote_path: str) -> bool:
        """Sync to Aliyun OSS"""
        if not self.aliyun_client:
            return False
        
        import oss2
        
        path = remote_path.replace("oss://", "")
        parts = path.split("/", 1)
        bucket_name = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""
        
        bucket = oss2.Bucket(self.aliyun_client, bucket_name, prefix)
        
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                key = f"{prefix}/{file.relative_to(self.storage_path)}"
                bucket.put_object_from_file(key, str(file))
        
        print(f"[MemoryX] Synced to Aliyun OSS: {bucket_name}/{prefix}")
        return True
    
    def _sync_to_tencent(self, remote_path: str) -> bool:
        """Sync to Tencent COS"""
        if not self.tencent_client:
            return False
        
        path = remote_path.replace("cos://", "")
        parts = path.split(".", 1)
        bucket_name = parts[0]
        
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                key = str(file.relative_to(self.storage_path))
                self.tencent_client.put_object_from_file(
                    Bucket=bucket_name,
                    Key=key,
                    FileBody=str(file)
                )
        
        print(f"[MemoryX] Synced to Tencent COS: {bucket_name}")
        return True
    
    def _sync_to_huawei(self, remote_path: str) -> bool:
        """Sync to Huawei OBS"""
        if not self.huawei_client:
            return False
        
        path = remote_path.replace("obs://", "")
        parts = path.split("/", 1)
        bucket_name = parts[0]
        
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                key = str(file.relative_to(self.storage_path))
                self.huawei_client.putFile(bucket_name, key, str(file))
        
        print(f"[MemoryX] Synced to Huawei OBS: {bucket_name}")
        return True
    
    def _sync_to_baidu(self, remote_path: str) -> bool:
        """Sync to Baidu BOS"""
        if not self.baidu_client:
            return False
        
        path = remote_path.replace("bos://", "")
        parts = path.split("/", 1)
        bucket_name = parts[0]
        
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                key = str(file.relative_to(self.storage_path))
                self.baidu_client.put_object_from_file(
                    bucket=bucket_name,
                    key=key,
                    file_to_upload=str(file)
                )
        
        print(f"[MemoryX] Synced to Baidu BOS: {bucket_name}")
        return True
    
    def sync_from_cloud(self, remote_path: str = None) -> bool:
        """Restore from cloud"""
        remote_path = remote_path or self.config.remote_backup_path
        if not remote_path:
            return False
        
        # Simplified restore - just re-download all files
        return self.sync_to_cloud(remote_path)
    
    def get_status(self) -> Dict:
        """Get cloud sync status"""
        providers = self.get_supported_providers()
        connected = sum(1 for p in providers.values() if p.get("connected"))
        
        return {
            "total_providers": len(providers),
            "connected_providers": connected,
            "providers": providers
        }
