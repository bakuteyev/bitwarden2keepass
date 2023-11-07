"""Tests for the bitwarden2keepass.convert module."""

import pytest
from pykeepass import create_database, PyKeePass
from bitwarden2keepass.convert import update_or_create_entry


@pytest.fixture
def kp(tmp_path):
    """Create a new KeePass database."""
    db_path = tmp_path / 'test.kdbx'
    password = 'testpassword'
    kp = create_database(str(db_path), password=password)
    yield kp


def test_create_new_entry(kp):
    """Test creating a new entry."""
    item = {
        'name': 'Test Entry',
        'login': {
            'username': 'testuser',
            'password': 'testpassword',
            'uris': [{'uri': 'https://example.com'}]
        },
        'notes': 'Test notes',
        'fields': [
            {'name': 'Custom Field 1', 'value': 'Custom Value 1'},
            {'name': 'Custom Field 2', 'value': 'Custom Value 2', 'type': 1}
        ]
    }
    entry_group = kp.add_group(kp.root_group, 'Test Group')
    update_or_create_entry(kp, entry_group, item)
    entry = kp.find_entries(title='Test Entry', group=entry_group, first=True)
    assert entry is not None
    assert entry.username == 'testuser'
    assert entry.password == 'testpassword'
    assert entry.url == 'https://example.com'
    assert entry.notes == 'Test notes'
    assert entry.get_custom_property('Custom Field 1') == 'Custom Value 1'
    assert entry.get_custom_property('Custom Field 2') == 'Custom Value 2'

def test_update_existing_entry(kp):
    """Test updating an existing entry."""
    item = {
        'name': 'Test Entry',
        'login': {
            'username': 'testuser',
            'password': 'testpassword',
            'uris': [{'uri': 'https://example.com'}]
        },
        'notes': 'Test notes',
        'fields': [
            {'name': 'Custom Field 1', 'value': 'Custom Value 1'},
            {'name': 'Custom Field 2', 'value': 'Custom Value 2', 'type': 1}
        ]
    }
    entry_group = kp.add_group(kp.root_group, 'Test Group')
    kp.add_entry(entry_group, title='Test Entry', username='testuser',
                 password='oldpassword', url='https://example.com')
    update_or_create_entry(kp, entry_group, item)
    entry = kp.find_entries(title='Test Entry', group=entry_group, first=True)
    assert entry is not None
    assert entry.username == 'testuser'
    assert entry.password == 'testpassword'
    assert entry.url == 'https://example.com'
    assert entry.notes == 'Test notes'
    assert entry.get_custom_property('Custom Field 1') == 'Custom Value 1'
    assert entry.get_custom_property('Custom Field 2') == 'Custom Value 2'
    kp.save()
