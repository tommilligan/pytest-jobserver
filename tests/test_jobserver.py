import os
import time


def make_jobserver(dir_, name, size):
    """Create a fifo with the given name and directory. Return a filehandle.

    :param str dir_: Directory to create jobserver fifo in.
    :param str name: Name of fifo.
    :param int size: Number of tokens to preload into the jobserver.
    """
    # Create our fifo
    fifo_path = os.path.join(dir_, name)
    os.mkfifo(fifo_path)

    # Open it as noblocking
    fifo = os.open(fifo_path, os.O_RDWR | os.O_NONBLOCK)

    # Write some tokens into it
    tokens = b"X" * size
    os.write(fifo, tokens)

    return fifo


def test_help_message(testdir):
    result = testdir.runpytest("--help")
    # Check our options have been registered
    result.stdout.fnmatch_lines(["jobserver:", "*--jobserver*"])


def test_server(testdir):
    testdir.makepyfile(
        """
        import pytest

        def test_plugin_setup(request):
            assert 'jobserver_fifo' == request.config.getoption('jobserver')
    """
    )
    make_jobserver(testdir.tmpdir, "jobserver_fifo", 1)

    result = testdir.runpytest("-v", "--jobserver", "jobserver_fifo")

    result.stdout.fnmatch_lines(["*::test_plugin_setup PASSED*"])
    assert result.ret == 0


def test_server_xdist(testdir):
    testdir.makepyfile(
        """
        from time import sleep

        import pytest

        def pause():
            sleep(1)

        def test_0(request):
            pause()

        def test_1(request):
            pause()

        def test_2(request):
            pause()
    """
    )

    def time_with_tokens(tokens):
        jobserver_name = "jobserver_{}".format(tokens)
        make_jobserver(testdir.tmpdir, jobserver_name, tokens)

        start = time.time()
        # Run with 3 xdist workers, so tokens is the limiting factor
        result = testdir.runpytest("-v", "--jobserver", jobserver_name, "-n3")
        end = time.time()
        duration = end - start

        assert result.ret == 0
        return duration

    assert time_with_tokens(3) < time_with_tokens(2) < time_with_tokens(1)


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

    result.stderr.fnmatch_lines(["ERROR: jobserver is not a fifo: jobserver.txt"])
    assert result.ret == 4
