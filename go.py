#!python
import sys
major_minor = (sys.version_info.major, sys.version_info.minor)
if major_minor < (3, 7):
    print("-------------------------------------------------------------------------------------", file=sys.stderr)
    print("Python version:", sys.version, file=sys.stderr)
    print("WARNING: the version of Python you are using is likely incompatible with this script.", file=sys.stderr)
    print("Please update to at least version 3.8, or expect unsupported issues.", file=sys.stderr)
    print("-------------------------------------------------------------------------------------", file=sys.stderr)


from dataclasses import dataclass
from enum import Enum, auto
import logging as lg
import os
from pathlib import Path
import subprocess as sp
from typing import *


LOG = lg.getLogger(__name__)


try:
    import psutil
except ImportError:
    if sys.argv[-1] == "rerun":
        LOG.critical("Gambit to run with temporary venv with psutil fails!")
        sys.exit(11)
    psutil = None


def not_yet_implemented(fn):
    def fail(*_, **__):
        return NotImplementedError(fn.__name__)
    return fail


class Repository(Enum):
    pypi = "pypi"
    conda = "conda"


@dataclass
class Dependency:
    name: str
    repo: Repository
    constraint: str
    conditional: bool

    @classmethod
    def make(cls, name: str, repo_: str = "", constraint: str = "") -> "Dependency":
        conditional = False
        if repo_:
            if repo_.endswith("*"):
                conditional = True
                repo_ = repo_[:-1]
        else:
            repo_ = "pypi"

        return Dependency(name=name, repo=Repository[repo_], constraint=constraint, conditional=conditional)


DEPENDENCIES: Sequence[Dependency] = [
    Dependency.make(*row.strip().split())
    for row in """\
        bokeh              pypi     sync
        hdbscan
        ipywidgets         conda
        jupyterlab         conda
        jupyterlab-lsp     conda
        matplotlib         conda
        numba              conda
        numpy              conda
        pandas             conda
        panel              pypi     sync
        pip                conda*
        python             conda*   >=3.10
        python-lsp-server  conda
        pyviz-comms        pypi     sync
        scipy              conda
        thisnotthat
        umap
        vectorizers
    """.strip().split("\n")
]
Packages = Mapping[str, str]


class Deployed(Protocol):

    def python(self, *args: str) -> sp.CompletedProcess: ...


class JupyterHost(Enum):
    is_jupyter_running: bool
    dependencies: Mapping[str, str]


class Setup(Protocol):

    def deploy(self) -> Deployed: ...


@dataclass
class Context:
    is_jupyter_running: bool
    critical_dependencies: bool
    environment: Environment

    @classmethod
    def sense(cls) -> "Context":



def choose_setup() -> Setup:
    deps = gather_critical_dependencies()
    for var in ["CONDA_EXE", "CONDA_PREFIX", "CONDA_DEFAULT_ENV"]:
        LOG.debug(f"{var} = {os.environ.get(var, '<nope>')}")
        if not os.environ.get(var, ""):
            break
    else:
        return Conda(deps)
    return Venv(deps)


def gather_critical_dependencies():
    deps = DEPS.copy()
    if is_jupyter_running():
        for process in psutil.Process().parents():
            cmdline = process.cmdline()
            if len(cmdline) > 1 and any(
                cmdline[1].endswith(name)
                for name in ["jupyter-lab", "jupyter-notebook", "jupyterhub-singleuser", "jupyter-labhub"]
            ):



def is_jupyter_running():
    LOG.debug(f"JUPYTER_SERVER_URL = {os.environ.get('JUPYTER_SERVER_URL', '<nope>')}")
    return os.environ.get("JUPYTER_SERVER_URL", "").startswith("http")


class Conda:

    @not_yet_implemented
    def __init__(self, deps_jupyter: Packages):
        ...

    @not_yet_implemented
    def deploy(self) -> Deployed:
        ...


class Venv:

    @not_yet_implemented
    def __init__(self, deps_jupyter: Packages):
        ...

    @not_yet_implemented
    def deploy(self) -> Deployed:
        ...


def go():
    if psutil is None:
        sys.exit(rerun_with_psutil())
    else:
        context = Context.sense()
        env_deployed = context.environment.deploy()
        install_kernel(env_deployed)
        deploy_hooks()


def rerun_with_psutil():
    with tf.TemporaryDirectory(dir=".") as dir_venv:
        LOG.debug("Put up temporary venv with psutil package")
        sp.run([sys.executable, "-m", "venv", dir_venv], check=True)
        sp.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
        LOG.debug(f"Restart {sys.argv[0]} in this venv")
        return sp.run([f"{dir_env}/bin/python", *sys.argv, "rerun"], shell=False).returncode


if __name__ == "__main__":
    lg.basicConfig(
        level=lg.getLevelName(sys.argv[1]) if len(sys.argv) > 1 else lg.INFO,
        format="%(levelname)8s | %(message)s"
    )
    go()
