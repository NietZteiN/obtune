
import os
from pathlib import Path


DEFAULT_JAVA_LIBS = ("/usr/share/java/javatuples.jar",)


def _build_extra_java_classpath() -> str:
    entries = []
    for lib in DEFAULT_JAVA_LIBS:
        if Path(lib).exists():
            entries.append(lib)

    env_cp = os.environ.get("OBF_JAVA_CLASSPATH") or os.environ.get("CLASSPATH") or ""
    if env_cp:
        for item in env_cp.split(os.pathsep):
            item = item.strip()
            if item:
                entries.append(item)

    deduped = []
    seen = set()
    for item in entries:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return os.pathsep.join(deduped)


_REGISTERED_TESTS = []


def Test(func):
    """
    Decorator to register lightweight test helpers exposed via __main__.
    """
    _REGISTERED_TESTS.append(func)
    return func


class utity:
    def run_java_program_with_result(
        java_code_string: str,
        java_class_name: str,
        *,
        enable_assertions: bool = True,
    ) -> dict:
        import tempfile
        import subprocess

        if java_code_string.strip() == "":
            raise ValueError("Empty Java source received.")
        if java_class_name.strip() == "":
            raise ValueError("Invalid Java class name.")

        # Compile and run inside an isolated temp directory. With correct naming.
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_path = tmp_path / f"{java_class_name}.java"
            source_path.write_text(java_code_string, encoding="utf-8")
            extra_cp = _build_extra_java_classpath()

            compile_cmd = ["javac"]
            if extra_cp:
                compile_cmd += ["-cp", extra_cp]
            compile_cmd += [source_path.name]
            compile_proc = subprocess.run(
                compile_cmd,
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            if compile_proc.returncode != 0:
                return {
                    "compiled": False,
                    "ran": False,
                    "success": False,
                    "returncode": compile_proc.returncode,
                    "stdout": compile_proc.stdout.strip(),
                    "stderr": compile_proc.stderr.strip(),
                    "compile_error": compile_proc.stderr.strip() or compile_proc.stdout.strip(),
                    "runtime_error": "",
                    "assertion_failed": False,
                }

            run_cmd = ["java"]
            if enable_assertions:
                run_cmd.append("-ea")
            if extra_cp:
                run_cmd += ["-cp", f".{os.pathsep}{extra_cp}"]
            run_cmd += [java_class_name]
            run_proc = subprocess.run(
                run_cmd,
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            run_stdout = run_proc.stdout.strip()
            run_stderr = run_proc.stderr.strip()
            runtime_error = run_stderr or run_stdout
            assertion_failed = "AssertionError" in runtime_error

            return {
                "compiled": True,
                "ran": True,
                "success": run_proc.returncode == 0,
                "returncode": run_proc.returncode,
                "stdout": run_stdout,
                "stderr": run_stderr,
                "compile_error": "",
                "runtime_error": runtime_error,
                "assertion_failed": assertion_failed,
            }

    def run_java_program(java_code_string: str, java_class_name: str) -> str:
        result = utity.run_java_program_with_result(
            java_code_string,
            java_class_name,
            enable_assertions=True,
        )
        if not result.get("compiled"):
            raise RuntimeError(
                f"Compilation failed for {java_class_name}: {result.get('compile_error', '').strip()}"
            )
        if not result.get("success"):
            raise RuntimeError(
                f"Execution failed for {java_class_name}: {result.get('runtime_error', '').strip()}"
            )
        return str(result.get("stdout", "")).strip()


@Test
def run_all_source_java_files():
    from pathlib import Path
    from paths import resolve_eyetracking_source_root

    source_dir = resolve_eyetracking_source_root(Path(__file__).resolve().parent)
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    for java_file in sorted(source_dir.glob("*.java")):
        code = java_file.read_text(encoding="utf-8")
        class_name = java_file.stem
        print(f"Running {java_file.name}...")
        try:
            result = utity.run_java_program(code, class_name)
        except Exception as exc:
            print(f"Aborting on {java_file.name}: {exc}")
            raise
        print(result)
        print()


@Test
def _test_llama70b_downloaded():
    """
    Sanity-check that llama70b defaults are intact and the cached assets exist.
    """
    from pathlib import Path
    import importlib
    import sys

    try:
        models_module = importlib.import_module("eyetracking.models")
    except ModuleNotFoundError:
        fallback_path = str(Path(__file__).resolve().parent)
        if fallback_path not in sys.path:
            sys.path.append(fallback_path)
        models_module = importlib.import_module("models")

    DEFAULT_CACHE_DIR = getattr(models_module, "DEFAULT_CACHE_DIR")
    DEFAULT_MODEL_NAME = getattr(models_module, "DEFAULT_MODEL_NAME")
    llama70b = getattr(models_module, "llama70b")

    model = llama70b()

    mismatches = {}
    if model.model_name != DEFAULT_MODEL_NAME:
        mismatches["model_name"] = (model.model_name, DEFAULT_MODEL_NAME)
    if model.cache_dir != DEFAULT_CACHE_DIR:
        mismatches["cache_dir"] = (model.cache_dir, DEFAULT_CACHE_DIR)
    if mismatches:
        raise AssertionError(f"llama70b configuration mismatch: {mismatches}")

    cache_path = Path(model.cache_dir)
    if not cache_path.exists():
        raise FileNotFoundError(f"Cache directory missing: {cache_path}")

    required_files = {
        "config.json",
        "generation_config.json",
        "tokenizer_config.json",
        "tokenizer.model",
    }
    missing = []
    for target in required_files:
        if not any(path.name == target for path in cache_path.rglob(target)):
            missing.append(target)
    if missing:
        raise FileNotFoundError(
            f"Missing expected llama70b assets under {cache_path}: {missing}"
        )

    print(f"llama70b assets verified in {cache_path}")


class _TestFuncNamespace:
    @staticmethod
    def llama70b():
        return _test_llama70b_downloaded()


test_func = _TestFuncNamespace()
test_func.run_all_source_java_files = run_all_source_java_files


if __name__ == "__main__":
    for entry in _REGISTERED_TESTS:
        print(f"Executing test {entry.__name__}()")
        entry()

        
