import os
import re
import zipfile as zp
from io import BytesIO
from typing import List

import requests as r

download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
]

dir_path = ''


def main():
    ''' main '''
    global dir_path
    dir_path = _create_downloads_dir()

    _process_uris(download_uris)

    return


def _process_uris(uri_set: List) -> None:
    ''' High level helper that calls all uri processing functions.
        params:
            uri_set: List - uris to process.
    '''
    for uri in uri_set:
        file_name = _extract_file_name(uri)
        _make_file(uri, file_name)
    return


def _create_downloads_dir() -> str:
    ''' Creates the downloads directory if not currently present.
        We use os.getcwd and path.join to have a path agnostic of
        system.
        params:
            None
    '''
    current_path, new_dir = os.getcwd(), 'downloads'
    new_path = os.path.join(current_path, new_dir)
    if not os.path.isdir(new_path):
        os.mkdir(new_path)
    return new_path


def _extract_file_name(uri: str) -> str:
    ''' Creates the full file name with csv extension from list
        of uris.
        params:
            uri: string - uri used for file name extraction
    '''
    match = re.search(r'([^\/]+)(?=\.zip$)', uri)
    if match:
        file_name = match.group(1)
        return ''.join([file_name, '.csv'])
    return ''


def _make_file(uri: str, file_name: str) -> None:
    ''' Makes the GET request, and given valid response, we proceed
        with writing the file to disk.
        params:
            uri: string - uri used for request
            file_name: string - created by way of extracting from uri
    '''
    res = r.get(uri)
    if res.ok:
        _ = (zp.ZipFile(BytesIO(res.content))
                .extract(member=file_name, path=dir_path))  # went this way as opposed to context wrapping an open file to write
    return


if __name__ == "__main__":
    main()
