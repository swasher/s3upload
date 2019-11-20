import sys
import os
import logging
import boto3
import threading
import pyperclip
import subprocess
import ansicon
from subprocess import Popen, CREATE_NEW_CONSOLE
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from botocore.client import Config


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    bucket = os.getenv('S3_Bucket')

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    credentials = {'aws_access_key_id': os.getenv('AWS_SERVER_PUBLIC_KEY'),
                   'aws_secret_access_key': os.getenv('AWS_SERVER_SECRET_KEY'),
                   'region_name': os.getenv('REGION_NAME')
                   }

    # Upload the file
    s3_client = boto3.client('s3', **credentials, config=Config(signature_version='s3v4'))

    try:
        print(file_name)
        response = s3_client.upload_file(file_name, bucket, object_name,
                                         ExtraArgs={'ACL': 'public-read'},
                                         Callback=ProgressPercentage(file_name)
                                         )
    except ClientError as e:
        logging.error(e)
        return False

    # https://stackoverflow.com/questions/33809592/upload-to-amazon-s3-using-boto3-and-return-public-url

    # generate link 1
    # link = s3_client.generate_presigned_url('get_object', ExpiresIn=7776000, Params={'Bucket': S3_Bucket, 'Key': object_name})

    # generate link 2
    # import boto3
    # s3_client = boto3.client
    # bucket_location = s3_client.get_bucket_location(Bucket='my_bucket_name')
    # url = "https://s3.{0}.amazonaws.com/{1}/{2}".format(bucket_location['LocationConstraint'], 'my_bucket_name',
    #                                                     quote_plus('2018-11-26 16:34:48.351890+09:00.jpg')
    # print(url)

    # generate link 3
    link = '%s/%s/%s' % (s3_client.meta.endpoint_url, bucket, object_name)

    print('\n' + bcolors.WARNING + 'File link:' + bcolors.ENDC)
    print(bcolors.WARNING + link + bcolors.ENDC)

    pyperclip.copy(link)
    spam = pyperclip.paste()

    return True


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    os.path.basename(self._filename), self._seen_so_far, self._size, percentage))
            sys.stdout.flush()


if __name__ == '__main__':

    load_dotenv()
    ansicon.load()

    prog_start = Popen([sys.executable], shell=True, creationflags=CREATE_NEW_CONSOLE)
    # prog_start = Popen('ansicon.exe python', shell=True, creationflags=CREATE_NEW_CONSOLE)

    cmd = 'mode 120,20'
    os.system(cmd)

    # Have fun with terminal codes
    # print(u'\x1b[32m Green \x1b[m')

    # parse args
    arguments = sys.argv[1:]
    count = len(arguments)
    # UNCOMENT FOR CHECK ONE ARG!!!!
    if count != 1:
        raise Exception('Must be only one argument')

    # file_large = 'files/test_large.pdf'
    # file_small = 'files/test_small.pdf'
    # input_file = file_small
    input_file = sys.argv[1]

    bucket = 'tipo-proof'
    folder_name = os.getenv('folder')
    filename = os.path.basename(input_file)

    object_name = folder_name + '/' + filename

    upload_file(input_file, bucket, object_name)

    input('Enter to exit from this launcher script...')

    # Unload ansicon
    ansicon.unload()

    # this will kill the invoked terminal
    pidvalue = prog_start.pid
    subprocess.Popen('taskkill /F /T /PID %i' % pidvalue)
