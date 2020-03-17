import json

pytest_plugins = "pytester"

test_marker = 'XrayJira test payloads:'


# set env vars XRAY_API_CLIENT_ID=test;XRAY_API_CLIENT_SECRET=test for testing

def test_xrayjira_mock(testdir):
    test_xrayjira = """
    import pytest
    pytest_plugins = "pytester"
    
    @pytest.mark.xrayjira(test_key="KEY-1")
    def test_pass_1():
        assert True
        
    @pytest.mark.xrayjira(test_key="KEY-2")
    def test_pass_2():
        assert True
        
    @pytest.mark.xrayjira(test_key="KEY-3")
    def test_fail_3():
        assert False        
    """
    testdir.makepyfile(test_xrayjira)
    result = testdir.runpytest("--upload-results-to-jira-xray")
    assert test_marker in result.outlines
    payload_start_index = result.outlines.index(test_marker)
    payloads = []
    for line in result.outlines[payload_start_index + 1:]:
        if not line.startswith('{'):
            break
        payloads.append(line)
    pdata = json.loads(payloads[0])
    assert pdata['info']
    assert pdata['tests']
    assert len(pdata['tests']) == 3
    assert pdata['tests'][0]['testKey'] == 'KEY-1'
    assert pdata['tests'][0]['status'] == 'PASSED'
    assert pdata['tests'][1]['testKey'] == 'KEY-2'
    assert pdata['tests'][1]['status'] == 'PASSED'
    assert pdata['tests'][2]['testKey'] == 'KEY-3'
    assert pdata['tests'][2]['status'] == 'FAILED'
    assert len(payloads) == 1
