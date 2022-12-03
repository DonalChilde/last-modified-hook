from pathlib import Path

import pytest


@pytest.fixture(scope="session", name="test_dir")
def test_app_data_dir_(tmp_path_factory) -> Path:
    """make a temp directory for app data."""
    test_app_data_dir = tmp_path_factory.mktemp("last_modified_hook_")
    return test_app_data_dir
