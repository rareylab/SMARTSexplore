"""
Contains reusable utility code for the SMARTSexplore application.
"""

import subprocess
import logging


def run_process(cmd, timeout=None, stdout=None, stderr=None, reraise_exceptions=False, **kwargs):
    """
    Helper function that wraps subprocess.run with some additional
    exception handling that is useful to us.

    .. note::
        Will log an error message via the ``logging`` module if anything goes wrong.
        Passes shell=False to subprocess.run.

    :param cmd: Just like for subprocess.run.
    :param timeout: Just like for subprocess.run.
    :param stdout: Just like for subprocess.run.
    :param stderr: Just like for subprocess.run.
    :param reraise_exceptions: False by default. If True, caught exceptions will be re-raised.
        The False case is likely more useful for console-based interactions; the True case for
        interactions of a running web application to properly handle errors.
    :param kwargs: Will be passed directly to subprocess.run.
    """
    stdout = stdout or subprocess.PIPE
    stderr = stderr or subprocess.PIPE
    process = None
    try:
        process = subprocess.run(
            cmd, stdout=stdout, stderr=stderr,
            shell=False, timeout=timeout, **kwargs
        )
        if process.returncode != 0:
            raise Exception("Return code != 0, it is " + str(process.returncode))
    except Exception as exception:
        if process is not None:
            logging.error("Process FAILED during runtime. Command was: %s", " ".join(cmd))
            logging.error("Output on standard out:")
            logging.error(process.stdout.decode('utf-8'))
            logging.error("Output on standard error:")
            logging.error(process.stderr.decode('utf-8'))
        else:
            logging.error("Process FAILED starting up. Command was: %s", " ".join(cmd))

        if reraise_exceptions:
            raise exception
    return process
