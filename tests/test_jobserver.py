# -*- coding: utf-8 -*-


def test_help_message(testdir):
    result = testdir.runpytest("--help")
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["jobserver:", "*--jobserver*"])


def test_plugin_setup(testdir):
    testdir.makepyfile(
        """
        import pytest

        def test_plugin_setup(request):
            assert 'jobserver.pipe' == request.config.getoption('jobserver')
    """
    )
    testdir.makefile(".pipe", jobserver="X")

    result = testdir.runpytest("-v", "--jobserver", "jobserver.pipe")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["*::test_plugin_setup PASSED*"])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
