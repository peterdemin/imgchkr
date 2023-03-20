from setuptools import find_packages, setup

setup(
    name='imgchkr_api',
    version='0.0.0',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={'console_scripts': ['imgchkr_api=imgchkr_api.cli:serve']},
)
