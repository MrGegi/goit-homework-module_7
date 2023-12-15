from setuptools import setup, find_namespace_packages

setup(name = 'clean_folder',
      version='1.1',
      description='Script cleans folder by sorting all files acording to their extensions',
      url='https://github.com/MrGegi/goit-homework-module_7',
      author='MrGegi',
      author_email='randomemail@something.com',
      licence='None',
      packages=find_namespace_packages(),
      entry_points={'console_scripts': ['clean_folder = clean_folder.clean:main']})