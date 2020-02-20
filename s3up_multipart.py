import sys
import os
import re
import boto3
import threading
import pyperclip
import winsound
import ansicon
import datetime
from subprocess import Popen, CREATE_NEW_CONSOLE
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from botocore.client import Config
from boto3.s3.transfer import TransferConfig

# see https://github.com/tartley/colorama/blob/master/colorama/ansi.py
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[90m'


def finish_signal():
    frequency = 500
    duration = 200
    for i in range(2):
        winsound.Beep(frequency+i*300, duration)


def remove_forbidden_chars(filename):
    """
    TODO Important! Test filenames with dot (.) and double-dot (..)
    Проверка на допустимые символы
    https: // docs.aws.amazon.com / AmazonS3 / latest / dev / UsingMetadata.html

    Acceptable:
    0-9 a-z A-Z  ! - _ . * ' ( )

    Require special handling:
    &$@=;:+,? and space

    Characters to Avoid:
    \{}^%`[]«»<>~#|
    """

    replace_whitespace_with_hyphen = re.sub("\s", "-", filename)
    only_acceptable_symbols = re.findall("[0-9a-zA-Z!_\-.*()']", replace_whitespace_with_hyphen)
    return ''.join(only_acceptable_symbols)


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    credentials = {'aws_access_key_id': os.getenv('AWS_SERVER_PUBLIC_KEY'),
                   'aws_secret_access_key': os.getenv('AWS_SERVER_SECRET_KEY'),
                   'region_name': os.getenv('REGION_NAME')
                   }

    # Upload the file
    s3_client = boto3.client('s3', **credentials, config=Config(signature_version='s3v4'))

    transfer_config = TransferConfig(multipart_threshold=1024 * 25,
                                     max_concurrency=10,
                                     multipart_chunksize=1024 * 25,
                                     use_threads=True)

    try:
        # print('aaa', file_name)
        print(bcolors.WARNING + 'Start upload: ' + bcolors.ENDC + os.path.split(file_name)[1])
        print(bcolors.WARNING + 'Renamed to:   ' + bcolors.ENDC + os.path.split(object_name)[1])
        response = s3_client.upload_file(file_name, bucket, object_name,
                                         ExtraArgs={'ACL': 'public-read'},
                                         Config=transfer_config,
                                         Callback=ProgressPercentage(file_name)
                                         )
    except ClientError as e:
        print('Error!!!')
        print(e)
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

    print('\n' + bcolors.WARNING + 'File link:    ' + link + bcolors.ENDC)

    pyperclip.copy(link)
    spam = pyperclip.paste()
    print('\n' + bcolors.OKGREEN + 'Ссылка скопирована в буфер обмена.')

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
                "\r%s %.2f%% %s(%s из %s байт)%s " % (
                    # os.path.basename(self._filename), self._seen_so_far, self._size, percentage))
                    bcolors.WARNING + 'Progress:    ' + bcolors.ENDC, percentage, bcolors.DIM, self._seen_so_far, self._size, bcolors.ENDC))
            sys.stdout.flush()


if __name__ == '__main__':
    load_dotenv()
    ansicon.load()

    prog_start = Popen([sys.executable], shell=True, creationflags=CREATE_NEW_CONSOLE)
    cmd = 'mode 110,15'
    os.system(cmd)

    # parse args
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        raise Exception('Must be only one argument')

    # file_large = 'files/test_large.pdf'
    # file_small = 'files/test_small.pdf'
    # input_file = file_small
    input_file = sys.argv[1]

    bucket = os.getenv('S3_Bucket')
    folder_name = os.getenv('folder')

    filename = os.path.basename(input_file)
    filename = remove_forbidden_chars(filename)
    now = datetime.datetime.now()
    unique = '_' + now.strftime("%Y-%m-%d_%H.%M.%S")
    body, extention = os.path.splitext(filename)
    object_name = folder_name + '/' + filename + unique + extention

    upload_file(input_file, bucket, object_name)

    finish_signal()

    input(bcolors.DIM + 'Enter to exit from this launcher script...' + bcolors.ENDC)

    # Unload ansicon
    ansicon.unload()

    # this will kill the invoked terminal
    pidvalue = prog_start.pid
    # subprocess.Popen('taskkill /F /T /PID %i' % pidvalue)
