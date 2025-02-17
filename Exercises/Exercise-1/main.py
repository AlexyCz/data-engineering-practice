from io import BytesIO
import os
import re
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
    ''' docstring'''
    # TO DO:
        # download files
    global dir_path
    dir_path = _create_downloads_dir()

    for uri in download_uris:
        file_name = _extract_file_name(uri)
        _make_file(uri, file_name)

    return


def _create_downloads_dir():
    ''' docstring'''
    current_path, new_dir = os.getcwd(), 'downloads'
    new_path = os.path.join(current_path, new_dir)
    if not os.path.isdir(new_path):
        os.mkdir(new_path)
    return new_path


def _extract_file_name(uri: str):
    file_name = re.search(r'([^\/]+)(?=\.zip$)', uri).group(1)
    if file_name:
        return ''.join([file_name, '.csv'])
    return ''


def _make_file(uri: str, file_name: str):
    ''' docstring'''
    res = r.get(uri)
    if res.ok:
        _ = (zp.ZipFile(BytesIO(res.content))
                .extract(member=file_name, path=dir_path))
    return


if __name__ == "__main__":
    main()
