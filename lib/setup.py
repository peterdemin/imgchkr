from setuptools import find_packages, setup

setup(
    name='imgchkr_lib',
    version='0.0.0',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    package_data={"imgchkr_lib": ["py.typed"]},
)
