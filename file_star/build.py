import os
import time
from subprocess import call

from loguru import logger


class Build:
    """Build the app with nuitka"""

    def __init__(self):
        """This depends on the user, may need some path adaption"""

        cwd = os.getcwd()
        self.entry_path = os.path.join(cwd, 'main.py')
        self.build_path = os.path.join(os.path.dirname(cwd), 'build')
        os.makedirs(self.build_path, exist_ok=True)

        self.user_env_path = os.path.join(
            os.path.expanduser('~'),
            'miniconda3',
            'envs',
            'file_star',
            'lib',
            'python3.12',
            'site-packages',
        )

        assert os.path.isfile(self.entry_path), f'No valid src main.py file -> {self.entry_path}'
        assert os.path.isdir(self.user_env_path), f'No valid user env path folder -> {self.user_env_path}'

    def __call__(self):
        """Here we build"""

        start_clock = time.time()
        self.compile()
        logger.info(f'U need that long in min --> {(time.time() - start_clock) / 60}')

    def compile(self):
        """With nuitka from python to C"""

        call(
            'python -m nuitka '
            '--standalone '
            '--onefile '
            '--include-package=math '
            '--include-package=pygments '
            '--include-package=nicegui '
            '--nofollow-import-to=pylint '
            '--nofollow-import-to=isort '
            '--nofollow-import-to=blake '
            '--nofollow-import-to=nuitka '
            '--nofollow-import-to=unittest '
            '--nofollow-import-to=doctest '
            f'--include-data-dir={self.user_env_path}{os.sep}nicegui=nicegui '
            f'--output-dir={self.build_path} '
            f'--output-filename=file_star '
            f'{self.entry_path}',
            shell=True,
        )


if __name__ == '__main__':
    build = Build()
    build()
