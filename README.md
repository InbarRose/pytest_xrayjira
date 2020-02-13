Plugin installation
======================

To install this library for use please enter the following command (pypi integration coming soon):

    $ pip install git+git://github.com/InbarRose/pytest_xrayjira@master#egg=pytest_xrayjira
    

To use this plugin
======================

To take advantage of the pytest xrayjira plugin, use markers from pytest to associate a test function with a test key:

    import pytest

    @pytest.mark.xrayjira(test_key="KEY-12345")
    def test_my_function():
        assert True == True

Enable the plugin by passing the extra options to the command line when invoking the pytest runner:

    $ pytest . --upload-results-to-jira-xray

It is important that the environment variables **XRAY_API_CLIENT_ID** and **XRAY_API_CLIENT_SECRET** are set for pytest_xrayjira to sucessfully post results to the Xray API.

This will create a new test execution which will include all tests that were run.

Maintenance notes
======================
Please make sure that any new releases of the library use an incremented version number from the last. The following guidance is used to properly version bump this library {major}.{minor}.{patch}.

Major versions are increased for any new overall library features or general API breaking changes.

Minor versions are increased for any new features added or implementation changes to existing APIs.

Patch versions are increased for any bug fixes and non-breaking changes.

To automatically bump versions, best to install bump2version, then enter either of the following on the command line:

    $ bump2version major

or

    $ bump2version minor

or

    $ bump2version patch

These commands automatically commits and tags a new version. Make sure to push tags to the server with 

    $ git push && git push --tags
