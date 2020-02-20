from os import environ

from .constants import XRAY_API_BASE_URL, XRAY_PLUGIN, XRAY_MARKER_NAME, MARKER_ARGS, MARKER_DESCRIPTION, \
    UPLOAD_RESULTS_TO_XRAY_JIRA_FLAG
from .models import XrayTestReport
from .utils import PublishXrayResults, associate_marker_metadata_for, get_test_xray_kwargs


def pytest_configure(config):
    if not config.getoption(UPLOAD_RESULTS_TO_XRAY_JIRA_FLAG):
        return

    plugin = PublishXrayResults(
        XRAY_API_BASE_URL,
        client_id=environ["XRAY_API_CLIENT_ID"],
        client_secret=environ["XRAY_API_CLIENT_SECRET"],
    )
    config.pluginmanager.register(plugin, XRAY_PLUGIN)
    config.addinivalue_line(
        "markers", f"{XRAY_MARKER_NAME}{MARKER_ARGS}: {MARKER_DESCRIPTION}"
    )


def pytest_addoption(parser):
    group = parser.getgroup("JIRA Xray integration")

    group.addoption(
        UPLOAD_RESULTS_TO_XRAY_JIRA_FLAG, action="store_true", help="jira_xray: Publish test results to Xray Jira API"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption(UPLOAD_RESULTS_TO_XRAY_JIRA_FLAG):
        return

    for item in items:
        associate_marker_metadata_for(item)


def pytest_terminal_summary(terminalreporter):
    if not terminalreporter.config.getoption(UPLOAD_RESULTS_TO_XRAY_JIRA_FLAG):
        return

    test_reports = []
    if "passed" in terminalreporter.stats:
        for each in terminalreporter.stats["passed"]:
            xray_kwargs = get_test_xray_kwargs(each)
            if xray_kwargs:
                report = XrayTestReport.as_passed(xray_kwargs, each.duration)
                test_reports.append(report)

    if "failed" in terminalreporter.stats:
        for each in terminalreporter.stats["failed"]:
            xray_kwargs = get_test_xray_kwargs(each)
            if xray_kwargs:
                report = XrayTestReport.as_failed(
                    xray_kwargs, each.duration, each.longreprtext
                )
                test_reports.append(report)

    publish_results = terminalreporter.config.pluginmanager.get_plugin(XRAY_PLUGIN)

    if not callable(publish_results):
        raise TypeError("Xray plugin is not a callable. Please review 'pytest_configure' hook!")

    publish_results(*test_reports)
