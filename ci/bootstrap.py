#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib
import subprocess
import sys

base_path: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent
templates_path = base_path / "ci" / "templates"


def check_call(args):
    print("+", *args)
    subprocess.check_call(args)


def exec_in_env():
    env_path = base_path / ".tox" / "bootstrap"
    if sys.platform == "win32":
        bin_path = env_path / "Scripts"
    else:
        bin_path = env_path / "bin"
    if not env_path.exists():
        import subprocess

        print("Making bootstrap env in: {0} ...".format(env_path))
        try:
            check_call([sys.executable, "-m", "venv", env_path])
        except subprocess.CalledProcessError:
            try:
                check_call([sys.executable, "-m", "virtualenv", env_path])
            except subprocess.CalledProcessError:
                check_call(["virtualenv", env_path])
        print("Installing `jinja2` into bootstrap environment...")
        check_call([bin_path / "pip", "install", "jinja2", "tox", "matrix"])
    python_executable = bin_path / "python"
    if not python_executable.exists():
        python_executable = python_executable.with_suffix('.exe')

    print("Re-executing with: {0}".format(python_executable))
    print("+ exec", python_executable, __file__, "--no-env")
    os.execv(python_executable, [python_executable, __file__, "--no-env"])


def main():
    import jinja2
    import matrix

    print("Project path: {0}".format(base_path))

    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(templates_path)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )

    tox_environments = {}
    for (alias, conf) in matrix.from_file(base_path / "setup.cfg").items():
        deps = conf["dependencies"]
        tox_environments[alias] = {
            "deps": deps.split(),
        }
        if "coverage_flags" in conf:
            cover = {"false": False, "true": True}[conf["coverage_flags"].lower()]
            tox_environments[alias].update(cover=cover)
        if "environment_variables" in conf:
            env_vars = conf["environment_variables"]
            tox_environments[alias].update(env_vars=env_vars.split())

    for template in templates_path.rglob('*'):
        if template.is_file():
            template_path = str(template.relative_to(templates_path))
            destination = base_path / template_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(jinja.get_template(template_path).render(tox_environments=tox_environments))
            print("Wrote {}".format(template_path))
    print("DONE.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--no-env"]:
        main()
    elif not args:
        exec_in_env()
    else:
        print("Unexpected arguments {0}".format(args), file=sys.stderr)
        sys.exit(1)
