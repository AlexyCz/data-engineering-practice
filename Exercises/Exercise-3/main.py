import gzip
import io
from os import SEEK_SET
import logging

import boto3

from constants import BUCKET, COMMON_CRAWL_KEY

logger = logging.getLogger()


def read_from_s3(client, bucket, key, full_file=False):
    '''
        Reads from an s3 bucket given the following params:
        
        client: boto3 session client,
        bucket: string,
        key: string,
        full_file: boolean representing single line or full read
        
    '''

    logger.warning(f'retreiving from bucket: {bucket} with key: {key}\n')
    content = ''
    
    with io.BytesIO() as data_file_obj:
        client.download_fileobj(bucket, key, data_file_obj)
        data_file_obj.seek(SEEK_SET)  # prepare pointer for read, i.e. reset stream position
        
        with gzip.open(filename=data_file_obj, mode='rt', encoding='utf-8') as read_file:
            if full_file:
                content = read_file.read()
            else:
                content = read_file.readline()
            print(content)
    return content


def main():
    '''
    We read the first line off an index wet.paths file, and subsequently read the entire file at location.
    '''

    session = boto3.session.Session()
    esssthree = session.client('s3')

    new_key = read_from_s3(client=esssthree, bucket=BUCKET, key=COMMON_CRAWL_KEY)  # first file parsed is an index, only first line needed
    
    _ = read_from_s3(client=esssthree, bucket=BUCKET, key=new_key, full_file=True)  # whole file read out

    return


if __name__ == "__main__":
    main()
