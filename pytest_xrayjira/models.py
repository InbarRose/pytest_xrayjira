import datetime
from .utils import format_timestamp


class XrayTestReport:
    def __init__(self, xray_kwargs, duration, exception_log=None):
        self.kwargs = xray_kwargs
        self.test_key = xray_kwargs['test_key']
        self.testplan_key = xray_kwargs.get('plan_key', None)
        self._set_execution_range(duration)
        self.exception_log = exception_log

    def _set_execution_range(self, duration):
        self.start_dt = datetime.datetime.utcnow()
        self.end_dt = self.start_dt + datetime.timedelta(microseconds=duration * 1000 ** 2)

    def __repr__(self):
        if self.exception_log:
            return f"<XrayTestReport (FAIL) test_key={self.test_key}>"
        else:
            return f"<XrayTestReport (PASS) test_key={self.test_key}>"

    def as_dict(self):
        entry = {
            "testKey": self.test_key,
            "status": "FAILED" if self.exception_log else "PASSED",
            "start": format_timestamp(self.start_dt),
            "finish": format_timestamp(self.end_dt),
        }
        if self.exception_log:
            entry["comment"] = self.exception_log
        return entry

    @classmethod
    def as_passed(cls, xray_kwargs, duration):
        return XrayTestReport(xray_kwargs, duration)

    @classmethod
    def as_failed(cls, xray_kwargs, duration, exception_log):
        return XrayTestReport(xray_kwargs, duration, exception_log)
