from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


class add_pyside6(build_py):
    def run(self):
        super().run()
        self.copy_file(
            str(Path(__file__).resolve().parent / "system_pyside6.pth"),
            str(Path(self.build_lib) / "system_pyside6.pth"),
            preserve_mode=0,
        )


setup(
    cmdclass={"build_py": add_pyside6},
)
