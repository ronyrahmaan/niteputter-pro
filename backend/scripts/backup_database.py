"""
Database Backup Script for NitePutter Pro
Creates automated backups of MongoDB database
"""

import asyncio
import sys
import os
from datetime import datetime, UTC
from pathlib import Path
import subprocess
import tarfile
import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongodb, get_database
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Handle database backup operations"""
    
    def __init__(self, backup_dir: Path = Path("/tmp/backups")):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        
        # Initialize S3 client if configured
        self.s3_client = None
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.get_aws_secret(),
                region_name=settings.aws_s3_region
            )
    
    async def backup_mongodb(self) -> Optional[Path]:
        """Create MongoDB backup using mongodump"""
        try:
            backup_name = f"mongodb_backup_{self.timestamp}"
            backup_path = self.backup_dir / backup_name
            
            logger.info(f"Starting MongoDB backup to {backup_path}")
            
            # Parse MongoDB URL
            import urllib.parse
            parsed = urllib.parse.urlparse(settings.mongodb_url)
            
            # Build mongodump command
            cmd = [
                "mongodump",
                "--uri", settings.mongodb_url,
                "--out", str(backup_path),
                "--db", settings.mongodb_db_name
            ]
            
            # Run mongodump
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("MongoDB backup completed successfully")
            
            # Create tar archive
            tar_path = backup_path.with_suffix(".tar.gz")
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_name)
            
            # Remove uncompressed backup
            subprocess.run(["rm", "-rf", str(backup_path)])
            
            return tar_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"mongodump failed: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    async def backup_to_s3(self, file_path: Path) -> bool:
        """Upload backup file to S3"""
        if not self.s3_client:
            logger.warning("S3 not configured, skipping cloud backup")
            return False
        
        try:
            s3_key = f"backups/database/{file_path.name}"
            
            logger.info(f"Uploading backup to S3: {s3_key}")
            
            self.s3_client.upload_file(
                str(file_path),
                settings.aws_s3_bucket_name,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'StorageClass': 'STANDARD_IA'  # Infrequent access for backups
                }
            )
            
            logger.info("Backup uploaded to S3 successfully")
            return True
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return False
    
    async def cleanup_old_backups(self, retention_days: int = 30):
        """Remove old local backups"""
        try:
            cutoff_date = datetime.now(UTC).timestamp() - (retention_days * 86400)
            
            for backup_file in self.backup_dir.glob("*.tar.gz"):
                if backup_file.stat().st_mtime < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file.name}")
        
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def cleanup_s3_backups(self, retention_days: int = 30):
        """Remove old S3 backups"""
        if not self.s3_client:
            return
        
        try:
            cutoff_date = datetime.now(UTC).timestamp() - (retention_days * 86400)
            
            response = self.s3_client.list_objects_v2(
                Bucket=settings.aws_s3_bucket_name,
                Prefix="backups/database/"
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['LastModified'].timestamp() < cutoff_date:
                        self.s3_client.delete_object(
                            Bucket=settings.aws_s3_bucket_name,
                            Key=obj['Key']
                        )
                        logger.info(f"Deleted old S3 backup: {obj['Key']}")
        
        except ClientError as e:
            logger.error(f"S3 cleanup failed: {e}")
    
    async def get_database_stats(self) -> dict:
        """Get database statistics before backup"""
        try:
            await connect_to_mongodb()
            db = await get_database()
            
            stats = {
                "timestamp": self.timestamp,
                "database": settings.mongodb_db_name,
                "collections": {}
            }
            
            # Get collection counts
            collections = ["products", "users", "orders", "carts", "reviews", "coupons"]
            for collection in collections:
                count = await db[collection].count_documents({})
                stats["collections"][collection] = count
            
            # Get database size
            db_stats = await db.command("dbStats")
            stats["size_mb"] = round(db_stats.get("dataSize", 0) / 1024 / 1024, 2)
            stats["index_size_mb"] = round(db_stats.get("indexSize", 0) / 1024 / 1024, 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    async def run_backup(self, upload_to_s3: bool = True, cleanup: bool = True):
        """Run complete backup process"""
        logger.info("=" * 60)
        logger.info(f"NitePutter Pro Database Backup - {self.timestamp}")
        logger.info("=" * 60)
        
        # Get database stats
        stats = await self.get_database_stats()
        if stats:
            logger.info(f"Database: {stats['database']}")
            logger.info(f"Size: {stats['size_mb']} MB")
            for collection, count in stats['collections'].items():
                logger.info(f"  {collection}: {count} documents")
        
        # Create backup
        backup_file = await self.backup_mongodb()
        if not backup_file:
            logger.error("Backup creation failed")
            return False
        
        logger.info(f"Backup created: {backup_file}")
        logger.info(f"Backup size: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Upload to S3
        if upload_to_s3:
            success = await self.backup_to_s3(backup_file)
            if not success:
                logger.warning("S3 upload failed, backup available locally")
        
        # Cleanup old backups
        if cleanup:
            await self.cleanup_old_backups()
            await self.cleanup_s3_backups()
        
        logger.info("Backup process completed successfully")
        return True


class DatabaseRestore:
    """Handle database restore operations"""
    
    def __init__(self):
        self.s3_client = None
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.get_aws_secret(),
                region_name=settings.aws_s3_region
            )
    
    async def list_backups(self) -> list:
        """List available backups"""
        backups = []
        
        # List local backups
        backup_dir = Path("/tmp/backups")
        if backup_dir.exists():
            for backup_file in backup_dir.glob("*.tar.gz"):
                backups.append({
                    "name": backup_file.name,
                    "location": "local",
                    "path": str(backup_file),
                    "size_mb": backup_file.stat().st_size / 1024 / 1024,
                    "created": datetime.fromtimestamp(backup_file.stat().st_mtime, UTC)
                })
        
        # List S3 backups
        if self.s3_client:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=settings.aws_s3_bucket_name,
                    Prefix="backups/database/"
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        backups.append({
                            "name": Path(obj['Key']).name,
                            "location": "s3",
                            "path": obj['Key'],
                            "size_mb": obj['Size'] / 1024 / 1024,
                            "created": obj['LastModified']
                        })
            except ClientError as e:
                logger.error(f"Failed to list S3 backups: {e}")
        
        # Sort by creation date
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    async def restore_from_backup(self, backup_path: str, drop_existing: bool = False):
        """Restore database from backup"""
        try:
            # If S3 path, download first
            if backup_path.startswith("backups/"):
                local_path = Path("/tmp") / Path(backup_path).name
                logger.info(f"Downloading backup from S3: {backup_path}")
                
                self.s3_client.download_file(
                    settings.aws_s3_bucket_name,
                    backup_path,
                    str(local_path)
                )
                backup_path = local_path
            else:
                backup_path = Path(backup_path)
            
            # Extract tar archive
            extract_dir = Path("/tmp") / "restore_temp"
            extract_dir.mkdir(exist_ok=True)
            
            logger.info(f"Extracting backup: {backup_path}")
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(extract_dir)
            
            # Find the backup directory
            backup_dir = next(extract_dir.iterdir())
            
            # Build mongorestore command
            cmd = [
                "mongorestore",
                "--uri", settings.mongodb_url
            ]
            
            if drop_existing:
                cmd.append("--drop")
            
            cmd.extend([
                "--dir", str(backup_dir / settings.mongodb_db_name)
            ])
            
            logger.info("Starting database restore...")
            
            # Run mongorestore
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Cleanup
            subprocess.run(["rm", "-rf", str(extract_dir)])
            
            logger.info("Database restore completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"mongorestore failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False


async def main():
    """Main backup script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NitePutter Pro Database Backup/Restore")
    parser.add_argument("action", choices=["backup", "restore", "list"], help="Action to perform")
    parser.add_argument("--s3", action="store_true", help="Upload backup to S3")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup old backups")
    parser.add_argument("--backup-file", help="Backup file to restore from")
    parser.add_argument("--drop", action="store_true", help="Drop existing collections before restore")
    
    args = parser.parse_args()
    
    if args.action == "backup":
        backup = DatabaseBackup()
        success = await backup.run_backup(
            upload_to_s3=args.s3,
            cleanup=args.cleanup
        )
        sys.exit(0 if success else 1)
    
    elif args.action == "list":
        restore = DatabaseRestore()
        backups = await restore.list_backups()
        
        print("\nAvailable Backups:")
        print("-" * 80)
        for backup in backups:
            print(f"Name: {backup['name']}")
            print(f"  Location: {backup['location']}")
            print(f"  Size: {backup['size_mb']:.2f} MB")
            print(f"  Created: {backup['created']}")
            print()
    
    elif args.action == "restore":
        if not args.backup_file:
            print("Error: --backup-file required for restore")
            sys.exit(1)
        
        restore = DatabaseRestore()
        
        # Check if backup exists
        backups = await restore.list_backups()
        backup_names = [b['name'] for b in backups]
        
        if args.backup_file not in backup_names:
            print(f"Error: Backup '{args.backup_file}' not found")
            print("Available backups:", ", ".join(backup_names))
            sys.exit(1)
        
        # Find backup path
        backup = next(b for b in backups if b['name'] == args.backup_file)
        
        print(f"Restoring from: {backup['name']}")
        print(f"Location: {backup['location']}")
        print(f"Size: {backup['size_mb']:.2f} MB")
        
        if args.drop:
            print("WARNING: This will drop existing collections!")
            confirm = input("Are you sure? (yes/no): ")
            if confirm.lower() != "yes":
                print("Restore cancelled")
                sys.exit(0)
        
        success = await restore.restore_from_backup(
            backup['path'],
            drop_existing=args.drop
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())