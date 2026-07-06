import re
from pathlib import Path

from agent.state import PatchResult
from agent.tools import run_process


PATCH_PATH_RE = re.compile(r"^(?:---|\+\+\+) [ab]/(.+)$")


def _repo_root(repo_root: str | Path) -> Path:
    return Path(repo_root).resolve()


def _extract_changed_files(patch: str) -> list[str]:
    changed_files: list[str] = []
    for line in patch.splitlines():
        match = PATCH_PATH_RE.match(line)
        if not match:
            continue
        path = match.group(1)
        if path != "/dev/null" and path not in changed_files:
            changed_files.append(path)
    return changed_files


def _is_safe_repo_path(repo_root: Path, path: str) -> bool:
    target = (repo_root / path).resolve()
    return target == repo_root or repo_root in target.parents


def _git_apply_context(repo_root: Path) -> tuple[Path, list[str]]:
    top_level = run_process(["git", "rev-parse", "--show-toplevel"], cwd=repo_root, timeout=10)
    if top_level["returncode"] != 0:
        return repo_root, []

    git_root = Path(top_level["stdout"].strip()).resolve()
    try:
        relative_repo = repo_root.relative_to(git_root)
    except ValueError:
        return repo_root, []

    if str(relative_repo) == ".":
        return git_root, []

    return git_root, [f"--directory={relative_repo.as_posix()}"]


def validate_patch_paths(repo_root: str | Path, patch: str) -> PatchResult:
    root = _repo_root(repo_root)
    changed_files = _extract_changed_files(patch)

    if not patch.strip():
        return {"success": False, "logs": "Patch is empty.", "changed_files": []}

    if not changed_files:
        return {
            "success": False,
            "logs": "Patch does not contain any changed files.",
            "changed_files": [],
        }

    unsafe_paths = [path for path in changed_files if not _is_safe_repo_path(root, path)]
    if unsafe_paths:
        return {
            "success": False,
            "logs": "Patch contains paths outside repo: " + ", ".join(unsafe_paths),
            "changed_files": changed_files,
        }

    return {"success": True, "logs": "", "changed_files": changed_files}


def _parse_new_file_contents(patch: str) -> dict[str, str]:
    files: dict[str, str] = {}
    current_path: str | None = None
    is_new_file = False
    content_lines: list[str] = []

    def commit_current():
        if current_path and is_new_file:
            files[current_path] = "\n".join(content_lines)

    for line in patch.splitlines():
        if line.startswith("diff --git "):
            commit_current()
            current_path = None
            is_new_file = False
            content_lines = []
            continue

        if line.startswith("--- "):
            is_new_file = line == "--- /dev/null"
            continue

        if line.startswith("+++ "):
            path = line[4:]
            if path.startswith("b/"):
                path = path[2:]
            current_path = path
            continue

        if is_new_file and current_path is not None:
            if line.startswith("+") and not line.startswith("+++"):
                content_lines.append(line[1:])

    commit_current()
    return files


def _files_already_match_new_patch(repo_root: str | Path, patch: str) -> bool:
    root = _repo_root(repo_root)
    new_files = _parse_new_file_contents(patch)
    if not new_files:
        return False

    for path, content in new_files.items():
        target = root / path
        if not target.exists():
            return False
        existing = target.read_text(encoding="utf-8")
        if existing != content:
            return False
    return True


def _already_applied_patch_result(repo_root: str | Path, patch: str, original_logs: str, changed_files: list[str]) -> PatchResult:
    if "already exists in working directory" in original_logs:
        if _files_already_match_new_patch(repo_root, patch):
            return {
                "success": True,
                "logs": "Patch already applied; files exist with matching contents.",
                "changed_files": changed_files,
            }
    if "patch does not apply" in original_logs.lower() and _files_already_match_new_patch(repo_root, patch):
        return {
            "success": True,
            "logs": "Patch already applied; files exist with matching contents.",
            "changed_files": changed_files,
        }
    return {"success": False, "logs": original_logs, "changed_files": changed_files}


def apply_unified_diff(repo_root: str | Path, patch: str) -> PatchResult:
    path_result = validate_patch_paths(repo_root, patch)
    if not path_result["success"]:
        return path_result

    root = _repo_root(repo_root)
    apply_cwd, directory_args = _git_apply_context(root)

    check = run_process(
        ["git", "apply", "--check", *directory_args, "-"],
        cwd=apply_cwd,
        timeout=30,
        input_text=patch,
    )
    if check["returncode"] != 0:
        result = _already_applied_patch_result(root, patch, check["stdout"] + check["stderr"], path_result["changed_files"])
        if result["success"]:
            return result
        return result

    apply = run_process(
        ["git", "apply", *directory_args, "-"],
        cwd=apply_cwd,
        timeout=30,
        input_text=patch,
    )
    if apply["returncode"] != 0:
        logs = apply["stdout"] + apply["stderr"]
        result = _already_applied_patch_result(root, patch, logs, path_result["changed_files"])
        if result["success"]:
            return result
        return result

    return {
        "success": True,
        "logs": apply["stdout"] + apply["stderr"],
        "changed_files": path_result["changed_files"],
    }
