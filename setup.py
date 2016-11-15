#!/usr/bin/env python
from setuptools import setup
from distutils.command.install import install

class AddOnInstall(install):
    def run(self):
        install.run(self)

setup(
    name='icinga2-aws-multi-account-instance-discovery',
    version='0.1',
    description='Dynamicaly creates hosts lists for Icinga2, based on the list of AWS accounts and AWS instances tags.',
    author='Wojciech  Olesiejuk',
    author_email='admin@woew.co.uk',
    install_requires=["awscli", "boto3"],
    license="MIT",
    include_package_data=True,
    cmdclass={'install': AddOnInstall}
)