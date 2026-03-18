# -*- coding: utf-8 -*-
"""
MemoryX Cloud Sync - 云端同步
"""
import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from .config import Config


class CloudSync:
    """Cloud synchronization for MemoryX"""
    
    def __init__(self, config: Config):
        self.config = config
        self.storage_path = config.storage_path
        self._init_client()
    
    def _init_client(self):
        """Initialize cloud client"""
        self.s3_client = None
        self.gcs_client = None
        
        # Try S3
        if self._has_aws_credentials():
            try:
                import boto3
                self.s3_client = boto3.client('s3')
                print("[MemoryX] S3 client initialized")
            except:
                pass
        
        # Try GCS
        if self._has_gcs_credentials():
            try:
                from google.cloud import storage
                self.gcs_client = storage.Client()
                print("[MemoryX] GCS client initialized")
            except:
                pass
    
    def _has_aws_credentials(self) -> bool:
        return bool(os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"))
    
    def _has_gcs_credentials(self) -> bool:
        return bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GCS_PROJECT"))
    
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
            else:
                print(f"[MemoryX] Unsupported cloud provider: {remote_path}")
                return False
        except Exception as e:
            print(f"[MemoryX] Cloud sync failed: {e}")
            return False
    
    def _sync_to_s3(self, remote_path: str) -> bool:
        """Sync to AWS S3"""
        if not self.s3_client:
            print("[MemoryX] S3 client not initialized")
            return False
        
        path = remote_path.replace("s3://", "")
        bucket, prefix = path.split("/", 1)
        
        # Upload all files
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                key = f"{prefix}/{file.relative_to(self.storage_path)}"
                self.s3_client.upload_file(str(file), bucket, key)
        
        print(f"[MemoryX] Synced to S3: {bucket}/{prefix}")
        return True
    
    def _sync_to_gcs(self, remote_path: str) -> bool:
        """Sync to Google Cloud Storage"""
        if not self.gcs_client:
            print("[MemoryX] GCS client not initialized")
            return False
        
        path = remote_path.replace("gs://", "")
        bucket_name, prefix = path.split("/", 1)
        
        bucket = self.gcs_client.bucket(bucket_name)
        
        for file in self.storage_path.rglob("*"):
            if file.is_file():
                key = f"{prefix}/{file.relative_to(self.storage_path)}"
                blob = bucket.blob(key)
                blob.upload_from_filename(str(file))
        
        print(f"[MemoryX] Synced to GCS: {bucket_name}/{prefix}")
        return True
    
    def sync_from_cloud(self, remote_path: str = None) -> bool:
        """Sync from cloud to local"""
        remote_path = remote_path or self.config.remote_backup_path
        
        if not remote_path:
            return False
        
        try:
            if remote_path.startswith("s3://"):
                return self._sync_from_s3(remote_path)
            elif remote_path.startswith("gs://"):
                return self._sync_from_gcs(remote_path)
        except Exception as e:
            print(f"[MemoryX] Cloud restore failed: {e}")
            return False
    
    def _sync_from_s3(self, remote_path: str) -> bool:
        """Restore from S3"""
        if not self.s3_client:
            return False
        
        path = remote_path.replace("s3://", "")
        bucket, prefix = path.split("/", 1)
        
        # List objects
        response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
        for obj in response.get("Contents", []):
            key = obj["Key"]
            local_key = key.replace(prefix, "").lstrip("/")
            local_path = self.storage_path / local_key
            
            local_path.parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(bucket, key, str(local_path))
        
        print(f"[MemoryX] Restored from S3")
        return True
    
    def _sync_from_gcs(self, remote_path: str) -> bool:
        """Restore from GCS"""
        if not self.gcs_client:
            return False
        
        path = remote_path.replace("gs://", "")
        bucket_name, prefix = path.split("/", 1)
        
        bucket = self.gcs_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        
        for blob in blobs:
            local_key = blob.name.replace(prefix, "").lstrip("/")
            local_path = self.storage_path / local_key
            
            local_path.parent.mkdir(parents=True, exist_ok=True)
            blob.download_to_filename(str(local_path))
        
        print(f"[MemoryX] Restored from GCS")
        return True
    
    def get_sync_status(self) -> Dict:
        """Get sync status"""
        return {
            "s3_available": self.s3_client is not None,
            "gcs_available": self.gcs_client is not None,
            "last_sync": None
        }
