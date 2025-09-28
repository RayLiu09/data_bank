import logging
import os.path
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from settings import settings

logger = logging.getLogger(__name__)

class MinioUtils:
    """
    Minio工具类，用于进行Minio操作，如上传、下载、删除文件等
    """
    
    def __init__(self):
        """
        初始化Minio客户端，从settings配置类获取连接信息
        """
        try:
            self.client = Minio(
                f"{settings.minio_url}:{settings.minio_port}",
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=False  # 根据实际需要设置为True或False
            )
            self.bucket_name = settings.minio_bucket
            logger.info(f"MinIO client initialized successfully for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {str(e)}")
            raise
    
    async def upload_file(self, file_path: str, object_name: str, content_type: str = "application/octet-stream") -> bool:
        """
        上传文件到Minio
        
        Args:
            file_path: 本地文件路径
            object_name: 存储在Minio中的对象名称
            content_type: 文件内容类型
            
        Returns:
            bool: 上传是否成功
            
        Raises:
            S3Error: Minio操作异常
            FileNotFoundError: 本地文件不存在
        """
        try:
            # 检查本地文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Local file not found: {file_path}")
            
            # 上传文件
            self.client.fput_object(
                self.bucket_name,
                object_name,
                file_path,
                content_type=content_type
            )
            logger.info(f"File {file_path} uploaded successfully as {object_name}")
            return True
            
        except FileNotFoundError:
            logger.error(f"Local file not found: {file_path}")
            raise
        except S3Error as e:
            logger.error(f"MinIO upload error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {str(e)}")
            raise
    
    async def download_file(self, object_name: str, file_path: str) -> bool:
        """
        从Minio下载文件
        
        Args:
            object_name: Minio中的对象名称
            file_path: 本地保存文件路径
            
        Returns:
            bool: 下载是否成功
            
        Raises:
            S3Error: Minio操作异常
        """
        try:
            # 下载文件
            self.client.fget_object(
                self.bucket_name,
                object_name,
                file_path
            )
            logger.info(f"File {object_name} downloaded successfully to {file_path}")
            return True
            
        except S3Error as e:
            logger.error(f"MinIO download error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file download: {str(e)}")
            raise
    
    async def delete_file(self, object_name: str) -> bool:
        """
        从Minio删除文件
        
        Args:
            object_name: Minio中的对象名称
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            S3Error: Minio操作异常
        """
        try:
            # 删除文件
            self.client.remove_object(
                self.bucket_name,
                object_name
            )
            logger.info(f"File {object_name} deleted successfully")
            return True
            
        except S3Error as e:
            logger.error(f"MinIO delete error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {str(e)}")
            raise
    
    async def file_exists(self, object_name: str) -> bool:
        """
        检查文件是否存在于Minio中
        
        Args:
            object_name: Minio中的对象名称
            
        Returns:
            bool: 文件是否存在
            
        Raises:
            S3Error: Minio操作异常
        """
        try:
            statics = self.client.stat_object(
                self.bucket_name,
                object_name
            )
            logger.info(f"File {object_name} exists: {statics}")
            if statics:
                return True
            return False
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            else:
                logger.error(f"MinIO stat error: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error during file existence check: {str(e)}")
            raise
    
    async def list_files(self, prefix: str = "") -> list:
        """
        列出Minio中的文件
        
        Args:
            prefix: 文件名前缀过滤
            
        Returns:
            list: 文件对象列表
            
        Raises:
            S3Error: Minio操作异常
        """
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            file_list = [obj.object_name for obj in objects]
            logger.info(f"Listed {len(file_list)} files with prefix '{prefix}'")
            return file_list
            
        except S3Error as e:
            logger.error(f"MinIO list error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file listing: {str(e)}")
            raise
    
    def get_file_url(self, object_name: str, expires: int = 86400) -> str:
        """
        获取文件的临时访问URL
        
        Args:
            object_name: Minio中的对象名称
            expires: URL过期时间（秒），默认1天
            
        Returns:
            str: 文件的临时访问URL
            
        Raises:
            S3Error: Minio操作异常
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
            logger.debug(f"Generated presigned URL for {object_name}")
            return url
            
        except S3Error as e:
            logger.error(f"MinIO presigned URL error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during presigned URL generation: {str(e)}")
            raise

minio_client = MinioUtils()