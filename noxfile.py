"""Nox sessions."""
import os
import shlex
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import nox


try:
    from nox_poetry import Session
    from nox_poetry import session
except ImportError:
    message = f"""\
    Nox failed to import the 'nox-poetry' package.

    Please install it using the following command:

    {sys.executable} -m pip install nox-poetry"""
    raise SystemExit(dedent(message)) from None


PACKAGE = "trending_homebrew"
python_versions = ["3.10", "3.9", "3.8", "3.7"]
nox.needs_version = ">= 2021.6.6"
nox.options.sessions = (
    "pre-commit",
    "safety",
    "mypy",
    "tests",
    "typeguard",
    "xdoctest",
    "docs-build",
)


def activate_virtualenv_in_precommit_hooks(nox_session: Session) -> None:
    """Activate virtualenv in hooks installed by pre-commit.

    This function patches git hooks installed by pre-commit to activate the
    session's virtual environment. This allows pre-commit to locate hooks in
    that environment when invoked from git.

    Args:
        session: The Session object.
    """
    assert nox_session.bin is not None  # noqa: S101

    # Only patch hooks containing a reference to this session's bindir. Support
    # quoting rules for Python and bash, but strip the outermost quotes so we
    # can detect paths within the bindir, like <bindir>/python.
    bindirs = [
        bindir[1:-1] if bindir[0] in "'\"" else bindir
        for bindir in (repr(nox_session.bin), shlex.quote(nox_session.bin))
    ]

    virtualenv = nox_session.env.get("VIRTUAL_ENV")
    if virtualenv is None:
        return

    headers = {
        # pre-commit < 2.16.0
        "python": f"""\
            import os
            os.environ["VIRTUAL_ENV"] = {virtualenv!r}
            os.environ["PATH"] = os.pathsep.join((
                {nox_session.bin!r},
                os.environ.get("PATH", ""),
            ))
            """,
        # pre-commit >= 2.16.0
        "bash": f"""\
            VIRTUAL_ENV={shlex.quote(virtualenv)}
            PATH={shlex.quote(nox_session.bin)}"{os.pathsep}$PATH"
            """,
        # pre-commit >= 2.17.0 on Windows forces sh shebang
        "/bin/sh": f"""\
            VIRTUAL_ENV={shlex.quote(virtualenv)}
            PATH={shlex.quote(nox_session.bin)}"{os.pathsep}$PATH"
            """,
    }

    hookdir = Path(".git") / "hooks"
    if not hookdir.is_dir():
        return

    for hook in hookdir.iterdir():
        if hook.name.endswith(".sample") or not hook.is_file():
            continue

        if not hook.read_bytes().startswith(b"#!"):
            continue

        text = hook.read_text()

        if not any(
            Path("A") == Path("a") and bindir.lower(
            ) in text.lower() or bindir in text
            for bindir in bindirs
        ):
            continue

        lines = text.splitlines()

        for executable, header in headers.items():
            if executable in lines[0].lower():
                lines.insert(1, dedent(header))
                hook.write_text("\n".join(lines))
                break


@session(name="pre-commit", python=python_versions[0])
def precommit(nox_session: Session) -> None:
    """Lint using pre-commit."""
    args = nox_session.posargs or [
        "run",
        "--all-files",
        "--hook-stage=manual",
        "--show-diff-on-failure",
    ]
    nox_session.install(
        "black",
        "darglint",
        "flake8",
        "flake8-bandit",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-rst-docstrings",
        "isort",
        "pep8-naming",
        "pre-commit",
        "pre-commit-hooks",
        "pyupgrade",
    )
    nox_session.run("pre-commit", *args)
    if args and args[0] == "install":
        activate_virtualenv_in_precommit_hooks(nox_session)


@session(python=python_versions[0])
def safety(nox_session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = nox_session.poetry.export_requirements()
    nox_session.install("safety")
    nox_session.run("safety", "check", "--full-report",
                    f"--file={requirements}")


@session(python=python_versions)
def mypy(nox_session: Session) -> None:
    """Type-check using mypy."""
    args = nox_session.posargs or ["src", "tests", "docs/conf.py"]
    nox_session.install(".")
    nox_session.install("mypy", "pytest")
    nox_session.run("mypy", *args)
    if not nox_session.posargs:
        nox_session.run(
            "mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python=python_versions)
def tests(nox_session: Session) -> None:
    """Run the test suite."""
    nox_session.install(".")
    nox_session.install("coverage[toml]", "pytest", "pygments")
    try:
        nox_session.run("coverage", "run", "--parallel",
                        "-m", "pytest", *nox_session.posargs)
    finally:
        if nox_session.interactive:
            nox_session.notify("coverage", posargs=[])


@session(python=python_versions[0])
def coverage(nox_session: Session) -> None:
    """Produce the coverage report."""
    args = nox_session.posargs or ["report"]

    nox_session.install("coverage[toml]")

    if not nox_session.posargs and any(Path().glob(".coverage.*")):
        nox_session.run("coverage", "combine")

    nox_session.run("coverage", *args)


@session(python=python_versions[0])
def typeguard(nox_session: Session) -> None:
    """Runtime type checking using Typeguard."""
    nox_session.install(".")
    nox_session.install("pytest", "typeguard", "pygments")
    nox_session.run(
        "pytest", f"--typeguard-packages={PACKAGE}", *nox_session.posargs)


@session(python=python_versions)
def xdoctest(nox_session: Session) -> None:
    """Run examples with xdoctest."""
    if nox_session.posargs:
        args = [PACKAGE, *nox_session.posargs]
    else:
        args = [f"--modname={PACKAGE}", "--command=all"]
        if "FORCE_COLOR" in os.environ:
            args.append("--colored=1")

    nox_session.install(".")
    nox_session.install("xdoctest[colors]")
    nox_session.run("python", "-m", "xdoctest", *args)


@session(name="docs-build", python=python_versions[0])
def docs_build(nox_session: Session) -> None:
    """Build the documentation."""
    args = nox_session.posargs or ["docs", "docs/_build"]
    if not nox_session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")

    nox_session.install(".")
    nox_session.install("sphinx", "sphinx-click", "furo", "myst-parser")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    nox_session.run("sphinx-build", *args)


@session(python=python_versions[0])
def docs(nox_session: Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = nox_session.posargs or ["--open-browser", "docs", "docs/_build"]
    nox_session.install(".")
    nox_session.install("sphinx", "sphinx-autobuild",
                        "sphinx-click", "furo", "myst-parser")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    nox_session.run("sphinx-autobuild", *args)
