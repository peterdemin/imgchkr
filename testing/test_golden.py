#!/usr/bin/python3
import copy
import glob
import json
import os
import re
import time
from typing import Iterator, List

import httpx
import pytest
from printer import SubprocessPrinter

_HERE = os.path.dirname(__file__)
_TESTDATA = os.path.join(_HERE, 'testdata')
_LOCALHOST = '127.0.0.1'
_SUBMIT_URL_PATTERN = 'http://{}:5001/assets/image'
_STATUS_URL_PATTERN = 'http://{}:5001/assets/image/{{}}'
_REQ_GLOB = '*-req.json'
_RE_REQ_LABEL = re.compile(r'^(?:.*\/)?([^/]+)-req\.json$')
_RESP_PATTERN = '{}-resp.json'
_NOTF_PATTERN = '{}-notf.json'
_TASK_ID = '00000000-0000-0000-0000-000000000000'
_RE_TASK_ID = re.compile(r'(?i)[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}')


def _find_request_files() -> List[str]:
    return glob.glob(os.path.join(_TESTDATA, _REQ_GLOB))


@pytest.fixture(scope='session', name='callback')
def _load_callback_fixture() -> Iterator[SubprocessPrinter]:
    with SubprocessPrinter() as callback:
        yield callback


@pytest.mark.parametrize('request_file', _find_request_files())
def test_golden_response(
    request_file: str,
    api_host: str,
    callback_host: str,
    callback: SubprocessPrinter,
) -> None:
    payload = _load_request(request_file, api_host, callback_host)

    response = _wait_for_task(
        httpx.post(_SUBMIT_URL_PATTERN.format(api_host), json=payload).json(),
        _STATUS_URL_PATTERN.format(api_host),
    )
    response_file = _get_response_file(request_file)
    if os.path.exists(response_file):
        assert response == _load(response_file)
    else:
        _dump(response_file, response)

    notifications = list(map(_sanitize_text, callback.flush_output()))
    notifications_file = _get_notifications_file(request_file)
    if os.path.exists(notifications_file):
        assert notifications == _read_lines(notifications_file)
    elif notifications:
        _write_lines(notifications_file, notifications)


def _load_request(path: str, api_host: str, callback_host: str) -> dict:
    with open(path, "r", encoding="utf-8") as fobj:
        content = fobj.read()
        content = content.replace('api', api_host).replace('monitor', callback_host)
        return json.loads(content)


def _load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fobj:
        return json.loads(fobj.read())


def _dump(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as fobj:
        json.dump(data, fobj, indent=2)


def _read_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as fobj:
        return [line.strip() for line in fobj]


def _write_lines(path: str, lines: List[str]) -> None:
    with open(path, "w", encoding="utf-8") as fobj:
        for line in lines:
            fobj.write(f'{line}\n')


def _get_response_file(request_file: str) -> str:
    return _find_output_file(request_file, _RESP_PATTERN)


def _get_notifications_file(request_file: str) -> str:
    return _find_output_file(request_file, _NOTF_PATTERN)


def _find_output_file(request_file: str, output_pattern: str) -> str:
    matchobj = _RE_REQ_LABEL.match(request_file)
    assert matchobj
    label = matchobj.group(1)
    return os.path.join(_TESTDATA, output_pattern.format(label))


def _wait_for_task(status: dict, status_url_pattern: str) -> dict:
    for attempt in range(20):
        if attempt > 0:
            time.sleep(0.5)
        if status['state'] != 'queued':
            break
        response = httpx.get(status_url_pattern.format(status['id']))
        status = response.json()
    return _sanitize(status)


def _sanitize(result: dict) -> dict:
    sanitized = copy.deepcopy(result)
    if sanitized.get('id'):
        sanitized['id'] = _TASK_ID
    return sanitized


def _sanitize_text(text: str) -> str:
    return _RE_TASK_ID.sub(_TASK_ID, text)
