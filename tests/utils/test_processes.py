import os
from pathlib import Path
import sys

from zpp.utils.processes import run_process


def test_process_preserves_arguments_utf8_cwd_environment_and_failure_facts(
    tmp_path: Path,
) -> None:
    result = run_process(
        (
            sys.executable,
            "-c",
            "import os,sys; value='\\n'.join((sys.argv[1], "
            "os.environ['ZPP_PROCESS_TEST'], os.getcwd()))+'\\n'; "
            "sys.stdout.buffer.write(value.encode('utf-8')); sys.exit(7)",
            "空 格",
        ),
        cwd=tmp_path,
        env={"ZPP_PROCESS_TEST": "值"},
    )

    assert result.argv[-1] == "空 格"
    assert result.returncode == 7
    assert result.stdout.splitlines() == ["空 格", "值", str(tmp_path)]
    assert result.stderr == ""
    assert os.environ.get("ZPP_PROCESS_TEST") is None
