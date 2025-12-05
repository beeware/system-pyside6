import ast
import importlib.machinery
import platform
import subprocess
import sys
from importlib.metadata import Distribution, DistributionFinder
from pathlib import Path


def get_system_site():
    """
    Locate the system site directories by running python3 globally
    (thus circumventing venv) and printing its site packages directories.

    This is used as a fallback for uncommon distros for which we do not
    know where the system site package directories are.

    :return: List of global site-package directories.
    """
    return ast.literal_eval(
        subprocess.run(
            [
                "env",
                "-i",
                "python3",
                "-c",
                "import site; print(site.getsitepackages())",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )


DISTRO = platform.freedesktop_os_release()["ID"]
VERS = f"{sys.version_info.major}.{sys.version_info.minor}"

# Below, locations are hardcoded for common distros' layout, and those
# directories for package and distribution info are searched instead of
# the entire system site packages as defined above.

if DISTRO == "fedora":
    PACKAGE_DIR = [f"/usr/lib/python{VERS}/site-packages/"]
    DIST_INFO_DIR = [f"/usr/lib64/python{VERS}/site-packages/"]
elif DISTRO == "ubuntu":
    PACKAGE_DIR = ["/usr/lib/python3/dist-packages/"]
    DIST_INFO_DIR = ["/usr/lib/python3/dist-packages/"]
elif DISTRO.startswith("opensuse"):
    PACKAGE_DIR = [f"/usr/lib64/python{VERS}/site-packages/"]
    DIST_INFO_DIR = [f"/usr/lib64/python{VERS}/site-packages/"]
else:
    PACKAGE_DIR = DIST_INFO_DIR = get_system_site()


def locate_package(package_name):
    """
    Locate a package in system directories by a specific name.

    :param package_name: Name of the package to search for.
    :return: All package directories matching the package name.
    """

    paths = []
    for directory in PACKAGE_DIR:
        path = Path(directory) / package_name
        if path.exists() and path.is_dir():
            paths.append(path)
    return paths


def locate_dist_info_dir(pkgname):
    """
    Locate the distribution metadata directory for a package.
    Accepted metadata directories either uses [NAME].{dist-info, egg-info},
    or [NAME]-[VERSION].{dist-info, egg-info}; this matches the way
    various common distros distribute the metadata directories.

    :param pkgname: Package name to search metadata directory for.
    :return: The matching metadata directory or None if missing.
    """
    for directory in DIST_INFO_DIR:
        if not Path(directory).exists():
            continue
        for entry in Path(directory).iterdir():
            if entry.is_dir() and (
                (
                    entry.name.startswith(pkgname + "-")
                    and (
                        entry.name.endswith(".dist-info")
                        or entry.name.endswith(".egg-info")
                    )
                )
                or (
                    entry.name == f"{pkgname}.dist-info"
                    or entry.name == f"{pkgname}.egg-info"
                )
            ):
                return entry

    return None


class IsolatedDistribution(Distribution):
    def __init__(self, pkgname):
        self.pkgname = pkgname
        self._dist_info = locate_dist_info_dir(pkgname)

        if not self._dist_info:
            raise ImportError(f"No dist-info found for {pkgname}")

    def read_text(self, filename):
        file = self._dist_info / filename
        if file.exists():
            return file.read_text(encoding="utf-8")
        return None

    def locate_file(self, path):
        return self._dist_info.parent / path


class IsolatedPackageFinder(DistributionFinder):
    def __init__(self, package_dirs):
        self.package_dirs = package_dirs

    def find_spec(self, fullname, path=None, target=None):
        for pkg, pkg_paths in self.package_dirs.items():
            if fullname == pkg or fullname.startswith(pkg + "."):
                for path in pkg_paths:
                    spec = importlib.machinery.PathFinder.find_spec(
                        fullname, [str(path.parent)]
                    )
                    if spec is not None:
                        return spec
        return None

    def find_distributions(self, context=None):
        if context is None:
            context = DistributionFinder.Context()

        if not context.name:
            return

        # System packages on Fedora etc. uses PySide6 as the distribution.
        # instead of like PySide6-Essentials used on PyPI.
        if context.name in self.package_dirs:
            yield IsolatedDistribution(context.name)


sys.meta_path.insert(
    0,
    IsolatedPackageFinder(
        {
            "PySide6": locate_package("PySide6"),
            "shiboken6": locate_package("shiboken6"),
        }
    ),
)
