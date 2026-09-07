import asyncio
import os
import shutil
import tempfile
import time
from typing import Optional, Tuple

from app.core.config import settings
from app.services.judger.languages import get_language_config


class BaseRunner:
    async def run(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float,
        memory_limit: int,
    ) -> Tuple[Optional[str], Optional[str], float, int, Optional[str]]:
        raise NotImplementedError


class SubprocessRunner(BaseRunner):
    def __init__(self) -> None:
        os.makedirs(settings.JUDGER_WORKDIR, exist_ok=True)

    async def run(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float,
        memory_limit: int,
    ) -> Tuple[Optional[str], Optional[str], float, int, Optional[str]]:
        config = get_language_config(language)
        if config is None:
            return None, None, 0, 0, f"unsupported language: {language}"

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._run_sync,
            code, language, input_data, time_limit, memory_limit, config,
        )

    def _run_sync(self, code, language, input_data, time_limit, memory_limit, config):
        workdir = tempfile.mkdtemp(prefix="judge_", dir=settings.JUDGER_WORKDIR)
        try:
            source_name = "Main.java" if language == "java11" else f"solution{config.extension}"
            source_path = os.path.join(workdir, source_name)
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            if config.compile_cmd:
                cmd = config.compile_cmd.format(
                    source_file=source_path,
                    executable=os.path.join(workdir, "solution"),
                    workdir=workdir,
                )
                compile_proc = _run_process(cmd, cwd=workdir, timeout=15)
                if compile_proc.returncode != 0:
                    err = compile_proc.stderr.decode("utf-8", errors="ignore")[:2000]
                    return None, None, 0, 0, f"Compilation Error: {err}"

            if language == "java11":
                run_cmd = "java -cp {wd} Main".format(wd=workdir)
            elif config.compile_cmd:
                run_cmd = os.path.join(workdir, "solution")
            else:
                run_cmd = "python3 {src}".format(src=source_path)

            start = time.perf_counter()
            proc = _run_process(
                run_cmd,
                cwd=workdir,
                stdin=input_data.encode("utf-8"),
                timeout=time_limit * config.time_multiplier + 0.5,
                memory_limit_mb=int(memory_limit * config.memory_multiplier),
            )
            elapsed = time.perf_counter() - start

            if proc.returncode is None or proc.returncode == -9:
                if elapsed > time_limit * config.time_multiplier:
                    return None, None, elapsed, 0, "Time Limit Exceeded"
                return None, None, elapsed, 0, "Runtime Error: killed"

            if proc.returncode != 0:
                err = proc.stderr.decode("utf-8", errors="ignore")[:2000]
                return None, None, elapsed, 0, f"Runtime Error: {err}"

            stdout = proc.stdout.decode("utf-8", errors="ignore")
            memory_used = max(0, getattr(proc, "_peak_memory_mb", 0))
            return stdout, None, elapsed, int(memory_used), None
        finally:
            shutil.rmtree(workdir, ignore_errors=True)


def _run_process(cmd: str, cwd: str, stdin: bytes = None, timeout: float = 10.0, memory_limit_mb: int = None):
    import subprocess
    import resource

    def _set_limits():
        if memory_limit_mb:
            limit = memory_limit_mb * 1024 * 1024
            try:
                resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
            except (ValueError, resource.error):
                pass

    try:
        return subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            input=stdin,
            capture_output=True,
            timeout=timeout,
            preexec_fn=_set_limits if memory_limit_mb else None,
        )
    except subprocess.TimeoutExpired as exc:
        class _Killed:
            returncode = None
            stdout = exc.stdout or b""
            stderr = exc.stderr or b""
        return _Killed()


def get_runner() -> BaseRunner:
    backend = settings.JUDGER_BACKEND.lower()
    if backend == "docker":
        try:
            from app.services.judger.docker_runner import DockerRunner
            return DockerRunner()
        except Exception:
            pass
    return SubprocessRunner()
