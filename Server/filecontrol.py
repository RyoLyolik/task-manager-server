from minio import Minio
from minio.error import InvalidResponseError
import os
from io import BytesIO
from config import MinioConfig


# Put a file with default content-type, upon success prints the etag identifier computed by server.
# try:
#     with open('tests.py', 'rb') as file_data:
#         file_stat = os.stat('tests.py')
#         print(client.put_object('teststorage', 'INITIAL_UPLOAD.py',
#                                file_data, file_stat.st_size))
# except InvalidResponseError as err:
#     print(err)


class FileControl:
    def __init__(self):
        self.client = Minio(
            MinioConfig.host,
            access_key=MinioConfig.access_key,
            secret_key=MinioConfig.secret_key,
            secure=MinioConfig.secure
        )

    def upload_file(self, bucket, filename, file):
        pass

    def get_file(self, filename):
        x = self.client.get_object(bucket_name="files", object_name=filename)
        x.close()
        x.release_conn()
        return x.data
