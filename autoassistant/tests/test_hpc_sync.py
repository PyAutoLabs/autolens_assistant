"""Offline tests for the HPC kit: ``hpc/sync`` and the ``hpc/batch_cpu/stage`` entry.

No cluster is contacted. ``ssh`` is a fake that runs the remote command locally in a
temporary "remote" directory, and ``scontrol``, ``scancel``, ``python`` and ``rsync``
are fakes that only record how they were called.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SYNC = ROOT / "hpc" / "sync"
STAGE = ROOT / "hpc" / "batch_cpu" / "stage"

CAMPAIGN_YAML = "campaign: demo\nproject_root: /unused\nmanifest: hpc/manifest.txt\n"


def _fake(path: Path, body: str):
    path.write_text("#!/usr/bin/env bash\n" + body)
    path.chmod(0o755)


@pytest.fixture
def cluster(tmp_path):
    """A project with hpc/sync, a fake cluster and the environment to drive it."""
    project = tmp_path / "proj"
    (project / "hpc").mkdir(parents=True)
    shutil.copy(SYNC, project / "hpc" / "sync")
    (project / "hpc" / "campaign.yaml").write_text(CAMPAIGN_YAML)
    remote = tmp_path / "remote"
    (remote / "proj").mkdir(parents=True)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = tmp_path / "calls.log"
    cluster_log = tmp_path / "cluster.log"
    _fake(bin_dir / "ssh", f'echo "ssh $*" >> "{calls}"\nshift\nbash -c "$*"\n')
    _fake(bin_dir / "rsync", f'echo "rsync $*" >> "{calls}"\n')
    for name in ("scontrol", "scancel", "sbatch", "python"):
        _fake(bin_dir / name, f'echo "{name} $*" >> "{cluster_log}"\n')

    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "HPC_HOST": "fakehost",
        "HPC_BASE": str(remote),
        "PROJECT_NAME": "proj",
        "USER": "tester",
    }

    def run(*args, extra_env=None):
        return subprocess.run(
            ["bash", "hpc/sync", *args],
            cwd=project,
            env={**env, **(extra_env or {})},
            capture_output=True,
            text=True,
            timeout=60,
        )

    def lines(path):
        return path.read_text().splitlines() if path.exists() else []

    return {
        "run": run,
        "project": project,
        "remote": remote / "proj",
        "bin": bin_dir,
        "calls": lambda: lines(calls),
        "cluster": lambda: lines(cluster_log),
    }


def _actions(cluster, name="demo"):
    log = cluster["remote"] / "campaign" / name / "actions.log"
    return [json.loads(line) for line in log.read_text().splitlines()]


def test_help_works_before_any_configuration(tmp_path):
    shutil.copytree(ROOT / "hpc", tmp_path / "hpc", ignore=shutil.ignore_patterns("sync.conf"))
    env = {k: v for k, v in os.environ.items() if k not in ("HPC_HOST", "HPC_BASE")}
    process = subprocess.run(
        ["bash", "hpc/sync", "help"], cwd=tmp_path, env=env, capture_output=True, text=True
    )
    assert process.returncode == 0
    assert "act <action>" in process.stdout
    assert "status <campaign.yaml>" in process.stdout


def test_status_with_a_campaign_file_collects_and_pulls_the_digest(cluster):
    process = cluster["run"]("status", "hpc/campaign.yaml")

    assert process.returncode == 0, process.stderr
    assert cluster["cluster"]() == ["python -m autofit.campaign status hpc/campaign.yaml"]
    ssh_calls = [c for c in cluster["calls"]() if c.startswith("ssh")]
    assert len(ssh_calls) == 1
    (pull,) = [c for c in cluster["calls"]() if c.startswith("rsync")]
    assert "--include=*.md" in pull and "--exclude=*" in pull
    assert pull.endswith(f"fakehost:{cluster['remote']}/campaign/demo/ {cluster['project']}/hpc/campaign/demo/")


def test_status_without_a_campaign_file_is_still_the_dry_run(cluster):
    process = cluster["run"]("status")

    assert process.returncode == 0, process.stderr
    assert "DRY RUN" in process.stdout
    assert cluster["cluster"]() == []


@pytest.mark.parametrize(
    "args, expected",
    [
        (["plan", "hpc/campaign.yaml", "--idle-cpus", "ral=100"],
         "python -m autofit.campaign plan hpc/campaign.yaml --idle-cpus ral=100"),
        (["pilot", "hpc/campaign.yaml", "--fraction", "0.05"],
         "python -m autofit.campaign pilot hpc/campaign.yaml --fraction 0.05"),
        (["resubmit", "hpc/campaign.yaml", "--stage", "source_lp", "--class", "timeout"],
         "python -m autofit.campaign resubmit hpc/campaign.yaml --stage source_lp --class timeout"),
        (["report", "hpc/campaign.yaml", "--site", "ral"],
         "python -m autofit.campaign report hpc/campaign.yaml --site ral"),
    ],
)
def test_campaign_verbs_run_autofit_on_the_cluster(cluster, args, expected):
    process = cluster["run"](*args)

    assert process.returncode == 0, process.stderr
    assert cluster["cluster"]() == [expected]
    assert len([c for c in cluster["calls"]() if c.startswith("ssh")]) == 1


def test_campaign_verbs_need_a_campaign_file(cluster):
    process = cluster["run"]("plan")
    assert process.returncode == 1
    assert "Usage" in process.stdout


@pytest.mark.parametrize(
    "args, command",
    [
        (["hold", "hpc/campaign.yaml", "123"], "scontrol hold 123"),
        (["release", "demo", "123"], "scontrol release 123"),
        (["throttle", "demo", "123", "5"], "scontrol update JobId=123 ArrayTaskThrottle=5"),
        (["update-pending", "demo", "123_4", "TimeLimit=10:00:00", "MinMemoryCPU=4096"],
         "scontrol update JobId=123_4 TimeLimit=10:00:00 MinMemoryCPU=4096"),
        (["cancel", "demo", "123"], "scancel 123"),
        (["submit", "hpc/campaign.yaml", "--stage", "source_lp", "--indices", "0-9%5"],
         "python -m autofit.campaign submit hpc/campaign.yaml --stage source_lp --indices 0-9%5"),
        (["resubmit", "hpc/campaign.yaml", "resubmit_source_lp_timeout.json"],
         "python -m autofit.campaign submit hpc/campaign.yaml "
         "--proposal campaign/demo/resubmit_source_lp_timeout.json"),
    ],
)
def test_act_runs_one_command_and_logs_it(cluster, args, command):
    process = cluster["run"]("act", *args)

    assert process.returncode == 0, process.stderr
    assert cluster["cluster"]() == [command]
    assert len([c for c in cluster["calls"]() if c.startswith("ssh")]) == 1
    (entry,) = _actions(cluster)
    assert set(entry) == {"utc", "user", "campaign", "action", "args", "exit"}
    assert entry["user"] == "tester"
    assert entry["campaign"] == "demo"
    assert entry["action"] == args[0]
    assert entry["args"] == args[2:]
    assert entry["exit"] == 0
    assert f'"action": "{args[0]}"' in process.stdout


def test_act_logs_a_failed_command_with_its_exit_status(cluster):
    _fake(cluster["bin"] / "scontrol", "exit 3\n")

    process = cluster["run"]("act", "hold", "demo", "123")

    assert process.returncode == 3
    assert _actions(cluster)[0]["exit"] == 3


def test_act_does_nothing_when_its_log_cannot_be_written(cluster):
    (cluster["remote"] / "campaign" / "demo" / "actions.log").mkdir(parents=True)

    process = cluster["run"]("act", "hold", "demo", "123")

    assert process.returncode == 1
    assert "nothing was done" in process.stderr
    assert cluster["cluster"]() == []


@pytest.mark.parametrize(
    "args, message",
    [
        (["launch", "demo", "1"], "unknown action"),
        (["hold", "demo"], "takes one job id"),
        (["hold", "demo", "abc"], "takes one job id"),
        (["hold", "demo", "1; rm -rf /"], "characters act does not pass on"),
        (["update-pending", "demo", "123", "Partition=gpu"], "may change only"),
        (["update-pending", "demo", "123", "TimeLimit"], "may change only"),
        (["throttle", "demo", "123"], "throttle takes"),
        (["resubmit", "demo", "p.json"], "needs the campaign.yaml"),
        (["submit", "demo"], "needs the campaign.yaml"),
        (["submit", "hpc/campaign.yaml", "--proposal=p.json"], "act resubmit"),
        (["hold", "bad name!", "1"], "campaign name"),
    ],
)
def test_act_refuses_anything_outside_its_allowlist(cluster, args, message):
    process = cluster["run"]("act", *args)

    assert process.returncode == 1
    assert message in process.stderr
    assert cluster["cluster"]() == []
    assert not [c for c in cluster["calls"]() if c.startswith("ssh")]


def test_cancel_goes_through_act_and_is_logged(cluster):
    process = cluster["run"]("cancel", "999")

    assert process.returncode == 0, process.stderr
    assert cluster["cluster"]() == ["scancel 999"]
    assert _actions(cluster, "adhoc")[0]["action"] == "cancel"


def test_submit_passes_sbatch_arguments_quoted(cluster):
    (cluster["remote"] / "hpc" / "batch_cpu").mkdir(parents=True)

    process = cluster["run"]("submit", "cpu", "stage", "--array=0-9", "--export=ALL,SAMPLE=a b")

    assert process.returncode == 0, process.stderr
    (call,) = [c for c in cluster["calls"]() if c.startswith("ssh")]
    assert "sbatch --array=0-9 --export=ALL\\,SAMPLE=a\\ b 'stage'" in call
    assert cluster["cluster"]() == ["sbatch --array=0-9 --export=ALL,SAMPLE=a b stage"]


def test_pull_rejects_an_unknown_result_root(cluster):
    process = cluster["run"]("pull", "nope")
    assert process.returncode == 1
    assert "not one of this project's result roots" in process.stdout


@pytest.mark.parametrize(
    "rsync_exit, message",
    [(23, "not on the HPC yet, or still being written (rsync exit 23)"), (255, "ssh connection failed"), (11, "rsync exit 11")],
)
def test_logs_tell_a_missing_directory_from_a_failed_pull(cluster, rsync_exit, message):
    _fake(cluster["bin"] / "rsync", f"exit {rsync_exit}\n")

    process = cluster["run"]("logs")

    assert process.returncode == 0
    assert message in process.stdout + process.stderr
    if rsync_exit != 23:
        assert "not on the HPC yet" not in process.stdout


@pytest.fixture
def stage_project(tmp_path):
    """A project for the stage entry: a manifest and a stand-in pipeline script."""
    project = tmp_path / "proj"
    (project / "hpc").mkdir(parents=True)
    (project / "scripts").mkdir()
    (project / "hpc" / "manifest.txt").write_text("imaging lens_a\nimaging lens_b\n")
    (project / "scripts" / "fit.py").write_text(
        "import os, signal, sys, time\n"
        "open(os.environ['ARGS_OUT'], 'w').write(' '.join(sys.argv[1:]))\n"
        "if os.environ.get('FIT_WAIT_USR1'):\n"
        "    got = []\n"
        "    signal.signal(signal.SIGUSR1, lambda *_: got.append(1))\n"
        "    open(os.environ['FIT_WAIT_USR1'], 'w').close()\n"
        "    while not got:\n"
        "        time.sleep(0.05)\n"
        "    time.sleep(0.2)  # the checkpoint flush, after the stage's first wait returned\n"
        "sys.exit(int(os.environ.get('FIT_EXIT', '0')))\n"
    )

    def environment(index, fit_exit=0, **extra):
        return {
            **os.environ,
            "STAGE": "source_lp",
            "STAGE_SCRIPT": "fit.py",
            "MANIFEST": "hpc/manifest.txt",
            "CAMPAIGN": "demo",
            "CAMPAIGN_OFFSET": "0",
            "SLURM_ARRAY_TASK_ID": str(index),
            "SLURM_ARRAY_JOB_ID": "777",
            "SLURM_CPUS_PER_TASK": "4",
            "ARGS_OUT": str(tmp_path / "args.txt"),
            "FIT_EXIT": str(fit_exit),
            **extra,
        }

    def run(index, fit_exit=0, **extra):
        return subprocess.run(
            ["bash", str(STAGE)], cwd=project, env=environment(index, fit_exit, **extra),
            capture_output=True, text=True, timeout=60,
        )

    run.environment = environment
    return project, tmp_path, run


def _record(project, index):
    return project / "output" / ".campaign_tasks" / "demo" / "source_lp" / f"{index}.status.json"


def test_stage_runs_the_manifest_line_and_removes_its_record_on_success(stage_project):
    project, tmp_path, run = stage_project

    process = run(1)

    assert process.returncode == 0, process.stderr
    args = (tmp_path / "args.txt").read_text()
    assert args == "--sample=imaging --dataset=lens_b --use_cpu --number_of_cores=4"
    assert not _record(project, 1).exists()


def test_stage_failure_leaves_a_failed_record_the_collector_reads(stage_project):
    project, _, run = stage_project

    process = run(0, fit_exit=1)

    assert process.returncode == 1
    record = json.loads(_record(project, 0).read_text())
    assert record["state"] == "failed"
    assert record["failure_class"] == "exception"
    assert record["exit"] == 1
    assert record["job"] == {"job_id": "777", "task_id": 0, "node": None}
    assert record["schema"] == 1
    # The start time, so a failure record the fit wrote itself (later) wins.
    assert record["updated"] == record["started"]
    assert record["updated"].endswith("Z")


def test_stage_with_no_manifest_line_is_bad_input(stage_project):
    project, _, run = stage_project

    process = run(5)

    assert process.returncode == 2
    record = json.loads(_record(project, 5).read_text())
    assert record["state"] == "failed"
    assert record["failure_class"] == "bad_input"


def test_stage_task_record_is_read_by_the_autofit_collector(stage_project):
    autofit = pytest.importorskip("autofit.campaign.collector")
    project, _, run = stage_project
    run(0, fit_exit=1)

    index = autofit.scan_status(project / "output")

    assert index[("777", 0)]["state"] == "failed"


def test_stage_that_checkpoints_on_usr1_and_then_finishes_is_a_success(stage_project):
    """The pre-timeout USR1 interrupts the stage's wait; the fit's own exit 0 must win."""
    import signal
    import time

    project, tmp_path, run = stage_project
    ready = tmp_path / "fit_ready"
    process = subprocess.Popen(
        [str(STAGE)], cwd=project, env=run.environment(0, FIT_WAIT_USR1=str(ready)),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    deadline = time.time() + 30
    while not ready.exists() and time.time() < deadline:
        time.sleep(0.05)
    process.send_signal(signal.SIGUSR1)
    stdout, stderr = process.communicate(timeout=60)

    assert process.returncode == 0, stdout + stderr
    assert "Finished: exit 0" in stdout
    assert not _record(project, 0).exists()


def test_stage_is_not_a_login_shell():
    """A login shell runs ~/.bash_logout after the EXIT trap and can overwrite the status."""
    assert STAGE.read_text().splitlines()[0] == "#!/bin/bash"
