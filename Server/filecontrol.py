from minio import Minio
from minio.error import InvalidResponseError
import os
from io import BytesIO

# Put a file with default content-type, upon success prints the etag identifier computed by server.
# try:
#     with open('tests.py', 'rb') as file_data:
#         file_stat = os.stat('tests.py')
#         print(client.put_object('teststorage', 'INITIAL_UPLOAD.py',
#                                file_data, file_stat.st_size))
# except InvalidResponseError as err:
#     print(err)


class FileControl:
    def __init__(self, host_ = 'localhost:9000', access_key_="minioadmin", secret_key_='minioadmin', secure=False):
        self.client = Minio(
            "localhost:9000",
            access_key='minioadmin',
            secret_key='minioadmin',
            secure = False # Почему-то только так работает
        )

    def upload_file(self, bucket, filename, file):
        pass

    def get_file(self, filename):
        x = self.client.get_object(bucket_name="files", object_name=filename)
        x.close()
        x.release_conn()
        return x.data

