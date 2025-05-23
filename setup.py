from setuptools import setup, find_packages
import os
import pathlib

CURRENT_DIR = pathlib.Path(__file__).parent
README = (CURRENT_DIR / "readme.md").read_text()

env = os.environ.get('source')


def get_dependencies():
    dependency = ["openpyxl==3.1.5", "python-barcode==0.15.1", "pillow==10.4.0", "svgwrite==1.4.3", "PyAudio==0.2.14"]

    if env and env == "dev":
        return dependency

    return dependency + []


setup(
    name='py-code-hub',
    version='0.0.1',
    url='https://github.com/banglafighter/py-code-hub',
    license='Apache 2.0',
    author='Bangla Fighter',
    author_email='banglafighter.com@gmail.com',
    description='Python Code Hub',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=get_dependencies(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ]
)