from io import BytesIO
import os
import re
from typing import List
import requests as r
import zipfile as zp

import pandas as pd

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
    ''' '''
    global dir_path
    dir_path = _create_downloads_dir()

    _process_uris(download_uris)

    return


def _process_uris(uri_set: List) -> None:
    ''' docstring '''
    for uri in uri_set:
        file_name = _extract_file_name(uri)
        _make_file(uri, file_name)
    return


def _create_downloads_dir() -> str:
    ''' docstring'''
    current_path, new_dir = os.getcwd(), 'downloads'
    new_path = os.path.join(current_path, new_dir)
    if not os.path.isdir(new_path):
        os.mkdir(new_path)
    return new_path


def _extract_file_name(uri: str) -> str:
    ''' docstring '''
    match = re.search(r'([^\/]+)(?=\.zip$)', uri)
    if match:
        file_name = match.group(1)
        return ''.join([file_name, '.csv'])
    return ''


def _make_file(uri: str, file_name: str) -> None:
    ''' docstring'''
    res = r.get(uri)
    if res.ok:
        print('#' * 50)
        print(uri, file_name)
        _ = (zp.ZipFile(BytesIO(res.content))
                .extract(member=file_name, path=dir_path))
    return


if __name__ == "__main__":
    main()
