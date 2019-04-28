import os


def test_help_message(testdir):
    result = testdir.runpytest("--help")
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(["jobserver:", "*--jobserver*"])


def test_server_fifo(testdir):
    testdir.makepyfile(
        """
        import pytest

        def test_plugin_setup(request):
            assert 'jobserver_named_pipe' == request.config.getoption('jobserver')
    """
    )
    # Create our fifo and write a byte into it
    fifo_path = os.path.join(testdir.tmpdir, "jobserver_named_pipe")
    os.mkfifo(fifo_path)
    fifo = os.open(fifo_path, os.O_RDWR | os.O_NONBLOCK)
    os.write(fifo, b"X")

    # Run our test
    result = testdir.runpytest("-v", "--jobserver", "jobserver_named_pipe")

    result.stdout.fnmatch_lines(["*::test_plugin_setup PASSED*"])
    assert result.ret == 0


def test_server_not_found(testdir):
    testdir.makepyfile(
        """
        import pytest

        def test_pass(request):
            pass
    """
    )
    # Run our test
    result = testdir.runpytest("-v", "--jobserver", "non_existent_file")

    result.stderr.fnmatch_lines(["ERROR: jobserver doesn't exist: non_existent_file"])
    assert result.ret == 4


def test_server_not_fifo(testdir):
    testdir.makefile(".txt", jobserver="X")
    testdir.makepyfile(
        """
        import pytest

        def test_pass(request):
            pass
    """
    )
    # Run our test
    result = testdir.runpytest("-v", "--jobserver", "jobserver.txt")

    result.stderr.fnmatch_lines(
        ["ERROR: jobserver is not a fifo/named pipe: jobserver.txt"]
    )
    assert result.ret == 4
