from ..src.endpoints import version

def test_list_version():
    version_number = "0.0.5"
    assert version.list_version() == version_number