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
_STATUS_URL_PATTERN = 'http://api:5001/check/{}'
_REQ_GLOB = '*-req.json'
_RE_REQ_LABEL = re.compile(r'^(?:.*\/)?([^/]+)-req\.json$')
_RESP_PATTERN = '{}-resp.json'


def _find_request_files() -> List[str]:
    return glob.glob(os.path.join(_TESTDATA, _REQ_GLOB))


@pytest.mark.parametrize('request_file', _find_request_files())
def test_golden_response(request_file):
    response_file = _get_response_file(request_file)
    with open(request_file, "r", encoding="utf-8") as fobj:
        payload = json.load(fobj)
    response = httpx.post(_SUBMIT_URL, json=payload)
    result = _wait_for_task(response.json())
    try:
        with open(response_file, "r", encoding="utf-8") as fobj:
            expected = json.load(fobj)
    except OSError:
        with open(response_file, "w", encoding="utf-8") as fobj:
            json.dump(result, fobj, indent=2)
        return
    sanitized = _sanitize(result, expected)
    if sanitized != expected:
        print(f'Mismatch found in {response_file}. Got:')
        print(json.dumps(sanitized, indent=2))
        print('Expected:')
        print(json.dumps(expected, indent=2))


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
    return status


def _sanitize(result: dict, expected: dict) -> dict:
    sanitized = copy.deepcopy(result)
    if result.get('id') and expected.get('id'):
        sanitized['id'] = expected['id']
    return sanitized
