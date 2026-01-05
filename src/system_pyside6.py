import ast
import importlib.machinery
import subprocess
import sys
from importlib.metadata import Distribution, DistributionFinder
from pathlib import Path


def get_system_site():
    """Locate the system site package directories.

    This (deliberately) circumvents any virtual environment to print the site
    package directories for the system Python.

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


SITE_PACKAGE_DIR = get_system_site()


def locate_dist_info_dir(pkgname):
    """Locate the distribution metadata directory for a package.

    Accepted metadata directories either uses [NAME].{dist-info, egg-info},
    or [NAME]-[VERSION].{dist-info, egg-info}; this matches the way
    various common distros distribute the metadata directories.

    :param pkgname: Package name to search metadata directory for.
    :return: The matching metadata directory or None if missing.
    """
    for directory in SITE_PACKAGE_DIR:
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
    # pkgname is the package name to look for; _dist_info
    # is the pre-located metadata for the package.  The metapath
    # finder manages its caching, so it is passed as a parameter.
    def __init__(self, pkgname, dist_info):
        self.pkgname = pkgname
        self._dist_info = dist_info

        if not self._dist_info:
            raise RuntimeError(f"No dist-info directory found for {pkgname}")

    def read_text(self, filename):
        file = self._dist_info / filename
        if file.exists():
            return file.read_text(encoding="utf-8")
        return None

    def locate_file(self, path):
        return self._dist_info.parent / path


class IsolatedPackageFinder(DistributionFinder):
    def __init__(self, packages, dist_packages):
        """
        :param packages: List of packages/modules that can be imported into
            the current venv from global site packages.
        :param dist_packages: List of distribution names that can be queried
            within the current venv from global site packages.  This is necessary
            because KDE package bindings do not ship corresponding .dist-info
            directories for some reason.
        """
        self.packages = packages
        self.dist_packages = dist_packages
        self.dist_info_dirs = {
            pkgname: locate_dist_info_dir(pkgname) for pkgname in dist_packages
        }

    def find_spec(self, fullname, path=None, target=None):
        """Find the package specification for the named package.

        :param fullname: Fully-qualified name of the module to find.
            e.g. PySide6, PySide6.QtCore
        :param path: __path__ of the parent package for submodules;
            None for top-level imports.
            e.g. None, /usr/lib/python3/dist-packages/PySide6
        :param target: Some sort of existing module object to aid the
            finder; unused here.
        """
        for pkg in self.packages:
            if fullname == pkg or fullname.startswith(pkg + "."):
                spec = importlib.machinery.PathFinder.find_spec(
                    fullname, SITE_PACKAGE_DIR
                )
                return spec
        return None

    def find_distributions(self, context=None):
        if context is None:
            context = DistributionFinder.Context()

        if not context.name:
            return

        # System packages on Fedora etc. uses PySide6 as the distribution.
        # instead of like PySide6-Essentials used on PyPI.
        if context.name in self.dist_packages:
            yield IsolatedDistribution(context.name, self.dist_info_dirs[context.name])


sys.meta_path.insert(
    0,
    IsolatedPackageFinder(
        [
            "PySide6",
            "shiboken6",
            # Python-bound KDE6 frameworks; from
            # https://invent.kde.org/teams/goals/streamlined-application-development-experience/-/issues/9  # noqa: E501
            "KCoreAddons",
            "KGuiAddons",
            "KI18n",
            "KWidgetsAddons",
            "KNotifications",
            "KStatusNotifierItem",
            "KUnitConversion",
            "KXmlGui",
        ],
        # Only PySide6 and shiboken6 are properly compiled distributions in the sense
        # of Python packaging.
        ["PySide6", "shiboken6"],
    ),
)
