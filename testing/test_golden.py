#!/usr/bin/python3
from typing import List
import time
import glob
import json
import os
import re
import copy

import pytest
import httpx

_HERE = os.path.dirname(__file__)
_TESTDATA = os.path.join(_HERE, 'testdata')
_SUBMIT_URL = 'http://api:5001/assets/image'
_STATUS_URL_PATTERN = 'http://api:5001/assets/image/{}'
_REQ_GLOB = '*-req.json'
_RE_REQ_LABEL = re.compile(r'^(?:.*\/)?([^/]+)-req\.json$')
_RESP_PATTERN = '{}-resp.json'
_TASK_ID = '00000000-0000-0000-0000-000000000000'


def _find_request_files() -> List[str]:
    return glob.glob(os.path.join(_TESTDATA, _REQ_GLOB))


@pytest.mark.parametrize('request_file', _find_request_files())
def test_golden_response(request_file) -> None:
    payload = _load(request_file)

    result = _wait_for_task(httpx.post(_SUBMIT_URL, json=payload).json())

    response_file = _get_response_file(request_file)
    if not os.path.exists(response_file):
        _dump(response_file, result)
        return
    assert result == _load(response_file)


def _load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fobj:
        return json.load(fobj)


def _dump(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as fobj:
        json.dump(data, fobj, indent=2)


def _get_response_file(request_file: str) -> str:
    matchobj = _RE_REQ_LABEL.match(request_file)
    assert matchobj
    label = matchobj.group(1)
    return os.path.join(_TESTDATA, _RESP_PATTERN.format(label))


def _wait_for_task(status: dict) -> dict:
    for attempt in range(20):
        if attempt > 0:
            time.sleep(0.5)
        if status['state'] != 'queued':
            break
        response = httpx.get(_STATUS_URL_PATTERN.format(status['id']))
        status = response.json()
    return _sanitize(status)


def _sanitize(result: dict) -> dict:
    sanitized = copy.deepcopy(result)
    if sanitized.get('id'):
        sanitized['id'] = _TASK_ID
    return sanitized
