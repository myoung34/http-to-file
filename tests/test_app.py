#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from unittest import mock

import pytest

import app
from app import create_app
from config import Config


class TestConfig(Config):
    pass

@pytest.fixture
def client():
    app = create_app(TestConfig)
    app.app_context().push()

    with app.test_client() as client:
        yield client

def test_app(
    client,
):
    with mock.patch.dict('os.environ', {}):
      rv = client.get('/')
      assert rv.status_code == 405
    with mock.patch.dict('os.environ', {}):
          rv = client.post('/')
          assert rv.status_code == 401
    with mock.patch.dict('os.environ', {
        'API_KEY': 'wrong',
    }):
        rv = client.post('/')
        assert rv.status_code == 401

    with mock.patch('os.path.exists', return_value=False), \
        mock.patch('builtins.open', mock.mock_open()) as mocked_file, \
        mock.patch('os.makedirs', return_value=False) as make_dirs, \
        mock.patch('app.main.routes.uuid4', return_value='wut'), \
        mock.patch.dict('os.environ', {
                'API_KEY': 'test',
                'FILE_DIR': '/opt/foo',
    }):
            rv = client.post(
                '/',
                headers={'Authorization': 'Bearer test', 'Content-Type': 'application/json'},
                json={'topic': 'test', 'message': 'test message'},
            )
            assert rv.status_code == 200
            assert rv.json == {'status': 'ok', 'id': 'wut'}
            make_dirs.assert_called_once_with('/opt/foo')

            mocked_file.assert_called_once_with('/opt/foo/wut.log', 'w')
            mocked_file().write.assert_called_once_with("{'message': 'test message', 'topic': 'test'}")