import pytest

from ..wagtail_client import WagtailClient


def test_is_next_total_count_0():
    client = WagtailClient("http://127.0.0.1:8080")
    response = {
        'meta': {'total_count': 0},
        'items': []
    }

    is_next = client._is_next(response)
    assert is_next == {'has_next': False, 'has_previos': False}


def test_is_next_equal_total_count_items():
    client = WagtailClient("http://127.0.0.1:8080")
    response = {
        'meta': {'total_count': 1},
        'items': [{'id': 1, 'meta': {'type': 'home.HomePage', 'detail_url': 'http://localhost/api/v2/pages/3/', 'html_url': 'http://localhost/', 'slug': 'home', 'first_published_at': None}, 'title': 'Home'}]
    }

    is_next = client._is_next(response)
    assert is_next == {'has_next': False, 'has_previos': False}


def test_is_next_param_is_none():
    client = WagtailClient("http://127.0.0.1:8080")
    response = {
        'meta': {'total_count': 21},
        'items': [{'id': 1, 'meta': {'type': 'home.HomePage', 'detail_url': 'http://localhost/api/v2/pages/3/', 'html_url': 'http://localhost/', 'slug': 'home', 'first_published_at': None}, 'title': 'Home'}]
    }

    is_next = client._is_next(response)
    assert is_next == {'has_next': True, 'has_previos': False}


def test_is_next_offset_not_define():
    client = WagtailClient("http://127.0.0.1:8080")
    response = {
        'meta': {'total_count': 5},
        'items': [
            {'id': 1, 'meta': {'type': 'home.HomePage', 'detail_url': 'http://localhost/api/v2/pages/3/',
                               'html_url': 'http://localhost/', 'slug': 'home', 'first_published_at': None}, 'title': 'Home'},
            {'id': 2, 'meta': {'type': 'home.HomePage', 'detail_url': 'http://localhost/api/v2/pages/3/',
                               'html_url': 'http://localhost/', 'slug': 'home', 'first_published_at': None}, 'title': 'Home'}
        ]
    }
    param = {
        'limit': 2
    }

    is_next = client._is_next(response, param)
    assert is_next == {'has_next': True, 'has_previos': False}

@pytest.fixture
def fixture_next_true():
    return [
        {
            'response': {
                'meta': {'total_count': 3},
                'items': [
                    {'id': 1, 'meta': {'type': 'home.HomePage', 'detail_url': 'http://localhost/api/v2/pages/1/',
                                       'html_url': 'http://localhost/', 'slug': 'home', 'first_published_at': None}, 'title': 'Home'}
                ]
            },
            'param': {
                'limit': 1
            },
            'assert_value': {
                'has_next': True, 'has_previos': False
            }
        },
        {
            'response': {
                'meta': {'total_count': 3},
                'items': [
                    {'id': 1, 'meta': {'type': 'home.HomePage', 'detail_url': 'http://localhost/api/v2/pages/1/',
                                       'html_url': 'http://localhost/', 'slug': 'home', 'first_published_at': None}, 'title': 'Home'}
                ]
            },
            'param': {
                'limit': 1,
                'offset': 0
            },
            'assert_value': {
                'has_next': True, 'has_previos': False
            }
        }
    ]

@pytest.fixture
def fixture_next_previos_true():
    return [
        {
            'response': {
                'meta': {'total_count': 3},
                'items': [
                    {'id': 2, 'meta': {'type': 'home.HomePage', 'detail_url': 'http://localhost/api/v2/pages/2/',
                                       'html_url': 'http://localhost/', 'slug': 'home', 'first_published_at': None}, 'title': 'Home'}
                ]
            },
            'param': {
                'limit': 1,
                'offset': 1
            },
            'assert_value': {
                'has_next': True, 'has_previos': True
            }
        }
    ]

@pytest.fixture
def fixture_previos_true():
    return [
        {
            'response': {
                'meta': {'total_count': 3},
                'items': [
                    {'id': 3, 'meta': {'type': 'home.HomePage', 'detail_url': 'http://localhost/api/v2/pages/3/',
                                       'html_url': 'http://localhost/', 'slug': 'home', 'first_published_at': None}, 'title': 'Home'}
                ]
            },
            'param': {
                'limit': 1,
                'offset': 2
            },
            'assert_value': {
                'has_next': False, 'has_previos': True
            }
        }
    ]

@pytest.fixture
def fixture_next_prevos_false():
    return [
        {
            'response': {
                'meta': {'total_count': 3},
                'items': []
            },
            'param': {
                'limit': 1,
                'offset': 3
            },
            'assert_value': {
                'has_next': False, 'has_previos': True
            }
        }
    ]

def test_is_next_all_data(fixture_next_true, fixture_next_previos_true, fixture_previos_true, fixture_next_prevos_false):
    client = WagtailClient("http://127.0.0.1:8080")

    errors = []
    errors.extend(_fixture_data_test(client, fixture_next_true))
    errors.extend(_fixture_data_test(client, fixture_next_previos_true))
    errors.extend(_fixture_data_test(client, fixture_previos_true))
    errors.extend(_fixture_data_test(client, fixture_next_prevos_false))

    assert not errors, "{}".format('\n'.join(errors))

def _fixture_data_test(client: WagtailClient, datas: list) -> list:
    errors = []
    for x in datas:
        is_next = client._is_next(x['response'], x['param'])
        if not x['assert_value'] == is_next:
            errors.append(
            f"""
            response: {x['response']}
            param: {x['param']}
            x['assert_value'] == is_next: {x['assert_value']} == {is_next}
            """)
    return errors
