from os import path
from unittest.mock import patch

import pytest

from main import _create_downloads_dir, _extract_file_name, _make_file, _process_uris


@pytest.mark.parametrize(
    'uris, test_fname',
    [
        (['uri.one'], 'one'),
        (['uri.two'], 'two'),
        (['uri.three'], 'three'),
        (['uri.four'], 'four'),
        (['uri.five'], 'five')
    ]
)
@patch('main._extract_file_name')
@patch('main._make_file')
def test_process_uris(mock_make_file, mock_extract_file_name, uris, test_fname):
    mock_extract_file_name.return_value = test_fname
    _process_uris(uris)
    mock_extract_file_name.assert_called_once_with(uris[-1])
    mock_make_file.assert_called_once_with(uris[-1], test_fname)


@patch('main.os.getcwd', return_value='/current/path')
@patch('main.os.path.isdir', return_value=False)
@patch('main.os.mkdir')
def test_create_downloads_dir(mock_mkdir, mock_isdir, mock_getcwd):
    res = _create_downloads_dir()

    assert res == '/current/path/downloads'
    mock_mkdir.assert_called_once_with(res)


@pytest.mark.parametrize(
    'uri, expected',
    [
        ('webbitywebsite.com/file_one.zip', 'file_one.csv'),
        ('webbitywebsite.com/file_two.zip', 'file_two.csv'),
        ('webbitywebsite.com/resource/file_three.zip', 'file_three.csv'),
        ('webbitywebsite.com/file_four.csv', ''),
        ('webbitywebsite.com/file_five.zzip', '')
    ]
)
def test_extract_file_name(uri, expected):
    result = _extract_file_name(uri)
    assert result == expected


@pytest.mark.parametrize(  # possibly future refactor to: pytest.generate_tests()
    'uri, test_fname, test_response_ok, test_path',
    [
        ('uri.one', 'one', True, ''),
        ('uri.two', 'two', False, ''),
        ('uri.three', 'three', False, ''),
        ('uri.four', 'four', True, ''),
        ('uri.five', 'five', True, '')
    ]
)
@patch('main.r')
@patch('main.zp.ZipFile')
@patch('main.BytesIO')
def test_make_file(mock_bytesio,
                   mock_zipfile,
                   mock_requests,
                   uri,
                   test_fname,
                   test_response_ok,
                   test_path):

    mock_response = mock_requests.Response()
    mock_response.ok = test_response_ok
    mock_requests.get.return_value = mock_response

    _make_file(uri, test_fname)

    mock_requests.get.assert_called_once_with(uri)

    if test_response_ok:
        mock_bytesio.assert_called_once()
        mock_zipfile.assert_called_once()
        mock_zipfile.return_value.extract.assert_called_once_with(member=test_fname,
                                                                    path=test_path)
    else:
        mock_bytesio.assert_not_called()
        mock_zipfile.assert_not_called()
        mock_zipfile.return_value.extract.assert_not_called()
