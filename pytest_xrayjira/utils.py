import os
import json
import logging
import datetime
import pytest
import requests

from .constants import XRAY_MARKER_NAME

log = logging.getLogger('xrayjira.publisher')
log.setLevel(logging.INFO)

_test_keys = {}


def get_revision():
    return os.environ.get('XRAY_REVISION', "")


def get_version():
    return os.environ.get('XRAY_VERSION', "")


def get_testplan_key():
    return os.environ.get('XRAY_TESTPLAN_KEY', "")


def get_test_environments():
    envs = os.environ.get('XRAY_TEST_ENVS', "")
    envs = envs.split(';')
    return envs


def get_user():
    return os.environ.get('XRAY_USER', "")


def _get_xray_marker(item):
    return item.get_closest_marker(XRAY_MARKER_NAME)


def associate_marker_metadata_for(item):
    marker = _get_xray_marker(item)
    if not marker:
        return

    test_key = marker.kwargs["test_key"]
    _test_keys[item.nodeid] = test_key


def get_test_key_for(item):
    results = _test_keys.get(item.nodeid)
    if results:
        return results
    return None, None


class PublishXrayResults:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        log.info(f"XrayJira Publisher Initialized")
        self._start_time = datetime.datetime.now()

    def __call__(self, *report_objs):
        log.info(f"XrayJira Publisher Called")
        bearer_token = self.authenticate()

        payload = self._test_execution_summary(*report_objs)
        self._post(payload, bearer_token)

        log.info("Successfully posted all test results to Xray!")

    def _post(self, a_dict, bearer_token):
        payload = json.dumps(a_dict)
        log.debug(f"Payload => {payload}")
        url = self.results_url()
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {bearer_token}"}
        resp = requests.post(url, data=payload, headers=headers)

        if not resp.ok:
            log.error("There was an error from Xray API!")
            log.error(resp.text)
            log.info(f"Payload => {payload}")
        else:
            log.info("Post test execution success!")

    def results_url(self):
        return f"{self.base_url}/api/v1/import/execution"

    def authenticate(self):
        url = f"{self.base_url}/api/v1/authenticate"
        payload = {"client_id": self.client_id, "client_secret": self.client_secret}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, payload, headers)
        token = resp.json()
        return token

    def _test_execution_summary(self, *report_objs):
        summary = self._create_header()

        for each in report_objs:
            summary["tests"].append(each.as_dict())

        return summary

    def _create_header(self):
        return {
            "info": {
                "summary": "Execution of automated tests",
                "description": "Execution of automated tests",
                "version": get_version(),
                "revision": get_revision(),
                "user": get_user(),
                "testPlanKey": get_testplan_key(),
                "startDate": self._start_time.isoformat(),
                "finishDate": datetime.datetime.now().isoformat(),
                "testEnvironments": get_test_environments(),
            },
            "tests": [],
        }
