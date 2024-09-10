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
            make_dirs.assert_called_with('/opt/foo')

            mocked_file.assert_called_with('/opt/foo/wut.log', 'w')
            mocked_file().write.assert_called_with("{'message': 'test message', 'topic': 'test'}")

            rv_base64 = client.post(
                '/',
                headers={'Authorization': 'Bearer test', 'Content-Type': 'application/json'},
                json={'base64': 'True', 'data': 'dGVzdAphc2RmCg=='},
            )
            assert rv_base64.status_code == 200
            assert rv_base64.json == {'status': 'ok', 'id': 'wut'}

            mocked_file().write.assert_called_with("test\nasdf\n")

def test_expel(
        client,
):
    with mock.patch.dict('os.environ', {}):
        rv = client.get('/expel')
        assert rv.status_code == 405
    # missing passthrough header
    with mock.patch.dict('os.environ', {}):
        rv = client.post('/expel')
        assert rv.status_code == 404
        # missing passthrough header
    with mock.patch.dict('os.environ', {}), \
        mock.patch.dict('os.environ', {
            'PASSTHROUGH_HEADER': 'My-Header',
        }):
        # empty passthrough header
        rv = client.post(
            '/expel',
            headers={'My-Header': '', 'Content-Type': 'application/json'},
            json={'topic': 'test', 'message': 'test message'},
        )
        assert rv.status_code == 404

    with mock.patch('os.path.exists', return_value=False), \
            mock.patch('builtins.open', mock.mock_open()) as mocked_file, \
            mock.patch('os.makedirs', return_value=False) as make_dirs, \
            mock.patch('app.main.routes.uuid4', return_value='asdf'), \
            mock.patch.dict('os.environ', {
                'PASSTHROUGH_HEADER': 'My-Test-Header',
            }):
        rv = client.post(
            '/expel',
            headers={'My-Test-Header': 'foo=anyvalue', 'Content-Type': 'application/json'},
            json={
                'guid': '1a9c6d7a-78e6-4238-8cd7-8d2ec2492cab',
                'rule': 'a rule name',
                'event_name': 'event name',
                'data': {'stuff': 'yup'},
            },
        )
        assert rv.status_code == 200
        assert rv.json == {'status': 'ok', 'id': 'anyvalue'}

        mocked_file.assert_called_with('/tmp/anyvalue.log', 'w')
        mocked_file().write.assert_called_with("{'data': {'stuff': 'yup'}, 'event_name': 'event name', 'guid': '1a9c6d7a-78e6-4238-8cd7-8d2ec2492cab', 'rule': 'a rule name'}")