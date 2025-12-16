# system-pyside6

[![Python Versions](https://img.shields.io/pypi/pyversions/system-pyside6.svg)](https://pypi.python.org/pypi/system-pyside6)
[![PyPI Version](https://img.shields.io/pypi/v/system-pyside6.svg)](https://pypi.python.org/pypi/system-pyside6)
[![Maturity](https://img.shields.io/pypi/status/system-pyside6.svg)](https://pypi.python.org/pypi/system-pyside6)
[![BSD License](https://img.shields.io/pypi/l/system-pyside6.svg)](https://github.com/beeware/system-pyside6/blob/main/LICENSE)
[![Build Status](https://github.com/beeware/system-pyside6/actions/workflows/ci.yml/badge.svg)](https://github.com/beeware/system-pyside6/actions)
[![Discord server](https://img.shields.io/discord/836455665257021440?label=Discord%20Chat&logo=discord&style=plastic)](https://beeware.org/bee/chat/)

A Python package that exposes system-installed [PySide6](https://pypi.org/project/PySide6/) packages into a virtual environment.

## Usage

PySide6 publishes multiple packages to PyPI. Howevever, these packages include a full copy of Qt. As a result, a Python app that uses a virtual environment and specifies PySide6 as a dependency will not use the system version of Qt - and as a result, will not adopt the system theme. This leads to an app that doesn't look native, as it doesn't conform to the system look and feel.

This package provides a customization of the Python import system that allows system-installed Python packages to be used in a virtual environment.

**NOTE: This is not an official Qt package!!** The BeeWare project has provided this package to provide a way to write Python applications that use a virtual environment (or other forms of environment isolation) without the need to duplicate Qt libraries in the virtual environment.

To use `system-pyside6`, install the system packages for PySide6:

* **Ubuntu / Debian** - `sudo apt-get install python3-pyside6.qtwidgets` (and other modules you may need, such as ``python3-pyside6.qtcore``; Only available from Ubuntu 24.10+ / Debian 13+)

* **Fedora** - `sudo dnf install python3-pyside6`, then `sudo dnf upgrade --refresh`

* **Arch/ Manjaro** - `sudo pacman -Syu pyside6`

* **OpenSUSE Tumbleweed** - `sudo zypper install python3-pyside6`

Then, create a virtual environment, and install `system-pyside6` into that environment. You should then be able to write a Python app using PySide6 without adding `PySide6` as a dependency of your app.

## Community

Briefcase is part of the [BeeWare suite](https://beeware.org). You can talk to the community through:

- [@beeware@fosstodon.org on Mastodon](https://fosstodon.org/@beeware)
- [Discord](https://beeware.org/bee/chat/)

We foster a welcoming and respectful community as described in our [BeeWare Community Code of Conduct](https://beeware.org/community/behavior/).

## Contributing

If you experience problems with system-pyside6, [log them on GitHub](https://github.com/beeware/system-pyside6/issues).

If you'd like to contribute to the development if system-pyside6, [submit a pull request](https://github.com/beeware/system-pyside6/pulls).
