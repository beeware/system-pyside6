import importlib.metadata
import os
import platform

import pytest

IS_DEBIAN = "debian" in platform.freedesktop_os_release()[
    "ID"
] or "debian" in platform.freedesktop_os_release().get("ID_LIKE", "")


def test_qapplication_override():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PySide6.QtWidgets import QApplication

    qt_style = os.environ.get("QT_STYLE_OVERRIDE", None)
    app = QApplication([])

    if qt_style:
        style_name = app.style().objectName()
        assert style_name.lower() == qt_style.lower()

    app.quit()


def test_pyside6_location():
    import PySide6

    assert PySide6.__file__.startswith("/usr/lib")


def test_metadata_version():
    import PySide6
    import shiboken6

    pyside6_version = importlib.metadata.version("PySide6")
    shiboken6_version = importlib.metadata.version("shiboken6")
    assert pyside6_version == PySide6.__version__
    assert shiboken6_version == shiboken6.__version__


def test_metadata_summary():
    pyside6_dist = importlib.metadata.distribution("PySide6")
    shiboken6_dist = importlib.metadata.distribution("shiboken6")
    assert isinstance(pyside6_dist.metadata["Summary"], str)
    assert isinstance(shiboken6_dist.metadata["Summary"], str)


def test_nonexposal():
    with pytest.raises(ImportError):
        import torch  # noqa: F401
    with pytest.raises(importlib.metadata.PackageNotFoundError):
        importlib.metadata.version("torch")


@pytest.mark.xfail(
    IS_DEBIAN, reason="Debian does not provide KDE frameworks that are bound to Python"
)
def test_import_kde():
    import KStatusNotifierItem

    _ = KStatusNotifierItem.KStatusNotifierItem
