from pathlib import Path

import pytest
import os

from jina.docker.hubio import HubIO
from jina.docker import hubapi
from jina.excepts import ImageAlreadyExists
from jina.jaml import JAML
from jina.helper import expand_dict
from jina.docker.helper import credentials_file
from jina.parser import set_hub_build_parser, set_hub_list_parser, set_hub_pushpull_parser

cur_dir = Path(__file__).parent

@pytest.fixture
def access_token_github():
    token = os.environ.get('GITHUB_TOKEN', None)
    return token

@pytest.mark.timeout(360)
def test_hub_build_pull():
    args = set_hub_build_parser().parse_args(
        [str(cur_dir / 'hub-mwu'), '--push', '--test-uses', '--raise-error'])
    HubIO(args).build()

    args = set_hub_pushpull_parser().parse_args(['jinahub/pod.dummy_mwu_encoder'])
    HubIO(args).pull()

    args = set_hub_pushpull_parser().parse_args(['jinahub/pod.dummy_mwu_encoder:0.0.6'])
    HubIO(args).pull()


@pytest.mark.timeout(360)
def test_hub_build_uses():
    args = set_hub_build_parser().parse_args(
        [str(cur_dir / 'hub-mwu'), '--test-uses', '--raise-error'])
    HubIO(args).build()
    # build again it shall not fail
    HubIO(args).build()

    args = set_hub_build_parser().parse_args(
        [str(cur_dir / 'hub-mwu'), '--test-uses', '--daemon', '--raise-error'])
    HubIO(args).build()
    # build again it shall not fail
    HubIO(args).build()

def test_hub_build_push(monkeypatch, access_token_github):
    monkeypatch.setattr(Path, 'is_file', True)
    monkeypatch.setattr(hubapi, '_fetch_access_token', access_token_github)
    args = set_hub_build_parser().parse_args([str(cur_dir / 'hub-mwu'), '--push', '--host-info'])
    summary = HubIO(args).build()

    with open(cur_dir / 'hub-mwu' / 'manifest.yml') as fp:
        manifest_jaml = JAML.load(fp, substitute=True)
        manifest = expand_dict(manifest_jaml)

    assert summary['is_build_success']
    assert manifest['version'] == summary['version']
    assert manifest['description'] == summary['manifest_info']['description']
    assert manifest['author'] == summary['manifest_info']['author']
    assert manifest['kind'] == summary['manifest_info']['kind']
    assert manifest['type'] == summary['manifest_info']['type']
    assert manifest['vendor'] == summary['manifest_info']['vendor']
    assert manifest['keywords'] == summary['manifest_info']['keywords']

    args = set_hub_list_parser().parse_args([
        '--name', summary['manifest_info']['name'],
        '--keywords', summary['manifest_info']['keywords'][0],
        '--type', summary['manifest_info']['type']
    ])
    response = HubIO(args).list()
    manifests = response

    assert len(manifests) >= 1
    assert manifests[0]['name'] == summary['manifest_info']['name']


def test_hub_build_push_push_again(monkeypatch, access_token_github):
    monkeypatch.setattr(Path, 'is_file', True)
    monkeypatch.setattr(hubapi, '_fetch_access_token', access_token_github)
    args = set_hub_build_parser().parse_args([str(cur_dir / 'hub-mwu'), '--push', '--host-info'])
    summary = HubIO(args).build()

    with open(cur_dir / 'hub-mwu' / 'manifest.yml') as fp:
        manifest_jaml = JAML.load(fp, substitute=True)
        manifest = expand_dict(manifest_jaml)

    assert summary['is_build_success']
    assert manifest['version'] == summary['version']
    assert manifest['description'] == summary['manifest_info']['description']
    assert manifest['author'] == summary['manifest_info']['author']
    assert manifest['kind'] == summary['manifest_info']['kind']
    assert manifest['type'] == summary['manifest_info']['type']
    assert manifest['vendor'] == summary['manifest_info']['vendor']
    assert manifest['keywords'] == summary['manifest_info']['keywords']

    args = set_hub_list_parser().parse_args([
        '--name', summary['manifest_info']['name'],
        '--keywords', summary['manifest_info']['keywords'][0],
        '--type', summary['manifest_info']['type']
    ])
    response = HubIO(args).list()
    manifests = response

    assert len(manifests) >= 1
    assert manifests[0]['name'] == summary['manifest_info']['name']

    with pytest.raises(ImageAlreadyExists):
        # try and push same version again should fail with `--no-overwrite`
        args = set_hub_build_parser().parse_args([str(cur_dir / 'hub-mwu'), '--push', '--host-info', '--no-overwrite'])
        HubIO(args).build()


def test_hub_build_failures():
    for j in ['bad-dockerfile', 'bad-pythonfile', 'missing-dockerfile', 'missing-manifest']:
        args = set_hub_build_parser().parse_args(
            [str(cur_dir / 'hub-mwu-bad' / j)])
        assert not HubIO(args).build()['is_build_success']


def test_hub_build_no_pymodules():
    args = set_hub_build_parser().parse_args(
        [str(cur_dir / 'hub-mwu-bad' / 'fail-to-start')])
    assert HubIO(args).build()['is_build_success']

    args = set_hub_build_parser().parse_args(
        [str(cur_dir / 'hub-mwu-bad' / 'fail-to-start'), '--test-uses'])
    assert not HubIO(args).build()['is_build_success']
