import os
import json
import logging
import datetime
import pytest
import requests
from collections import defaultdict
from .constants import XRAY_MARKER_NAME

log = logging.getLogger('xrayjira.publisher')
log.setLevel(logging.INFO)

_xray_tests = {}


def get_revision():
    return os.environ.get('XRAY_REVISION', "")


def get_version():
    return os.environ.get('XRAY_VERSION', "")


def get_testplan_key():
    return os.environ.get('XRAY_TESTPLAN_KEY', "")


def get_test_environments():
    envs = os.environ.get('XRAY_TEST_ENVS', "")
    envs = envs.split(';') if envs else []
    return envs


def get_user():
    return os.environ.get('XRAY_USER', "")


def get_project():
    return os.environ.get('XRAY_PROJECT', "")


def get_summary():
    return os.environ.get('XRAY_SUMMARY', "Execution of automated tests, auto-created execution")


def get_description():
    return os.environ.get('XRAY_DESCRIPTION', "Execution of automated tests, auto-created execution")


def _get_xray_marker(item):
    return item.get_closest_marker(XRAY_MARKER_NAME)


def associate_marker_metadata_for(item):
    marker = _get_xray_marker(item)
    if not marker:
        return

    _xray_tests[item.nodeid] = marker.kwargs


def get_test_xray_kwargs(item):
    results = _xray_tests.get(item.nodeid)
    if results:
        return results
    return None


def format_timestamp(dt):
    return dt.astimezone().isoformat(timespec='seconds')


class PublishXrayResults:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        log.info(f"XrayJira Publisher Initialized")
        self._start_time = datetime.datetime.now()

    def __call__(self, *report_objs):
        log.info(f"XrayJira Publisher Called")
        self._finish_time = datetime.datetime.now()
        payloads = self._prepare_test_payloads(*report_objs)
        if self.is_test:
            log.info(f"XrayJira in test mode, skip publishing - print to stdout")
            print('XrayJira test payloads:')
            for p in payloads:
                print(json.dumps(p))
            return payloads

        bearer_token = self.authenticate()
        for payload in payloads:
            success = self._post(payload, bearer_token)
            if success:
                log.info("Successfully posted test results to Xray! Plan={}".format(payload['info'].get('testPlanKey')))
            else:
                log.info("Failure posting all test results to Xray! Plan={}".format(payload['info'].get('testPlanKey')))

    def _post(self, a_dict, bearer_token):
        payload = json.dumps(a_dict, sort_keys=True)
        log.debug(f"Payload => {payload}")
        url = self.results_url()
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {bearer_token}"}
        resp = requests.post(url, data=payload, headers=headers)

        if not resp.ok:
            log.error("There was an error from Xray API!")
            log.error(resp.text)
            log.info(f"Payload => {payload}")
            return False
        else:
            log.info("Post test execution success!")
            return True

    @property
    def is_test(self):
        return bool(self.client_id == 'test' and self.client_secret == 'test')

    def results_url(self):
        return f"{self.base_url}/api/v1/import/execution"

    def authenticate(self):
        url = f"{self.base_url}/api/v1/authenticate"
        payload = {"client_id": self.client_id, "client_secret": self.client_secret}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, payload, headers)
        token = resp.json()
        return token

    def _sort_tests_into_plans(self, report_objs):
        test_plans = defaultdict(list)
        for each in report_objs:
            test_plans[each.testplan_key].append(each)
        return test_plans

    def _prepare_test_payloads(self, *report_objs):
        test_plans = self._sort_tests_into_plans(report_objs)
        payloads = []
        for testplan_key, reports in test_plans.items():
            payload = self._create_base_payload(testplan_key=testplan_key)

            for each in reports:
                payload["tests"].append(each.as_dict())

            payloads.append(payload)
        return payloads

    def _create_base_payload(self, **info):
        payload = {
            "info": {
                # strings
                "project": info.get('project') or get_project(),
                "summary": info.get('summary') or get_summary(),
                "description": info.get('description') or get_description(),
                "version": info.get('version') or get_version(),
                "revision": info.get('revision') or get_revision(),
                # dates
                "startDate": format_timestamp(self._start_time),
                "finishDate": format_timestamp(self._finish_time),
                # list
                "testEnvironments": info.get('test_environments') or get_test_environments(),
            },
            "tests": [],
        }

        # optional params (if we dont have, we should not use)
        user = info.get('user') or get_user()
        if user:
            payload['info']['user'] = user  # assigns the execution to this user
        testplan_key = info.get('testplan_key') or get_testplan_key()
        if testplan_key:  # either supplied by the test mark with plan_key=XXX or by env with XRAY_TESTPLAN_KEY
            payload['info']['testPlanKey'] = testplan_key

        return payload
