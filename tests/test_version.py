"""Module testing the application version module."""
import re

from ..src.endpoints import version

def test_list_version():
    """ Test that the module returns a version number in the correct format; see:
    https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string """

    response = version.list_version()
    regex_pattern = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$" # pylint: disable=line-too-long
    assert re.search(regex_pattern, response) is not None
