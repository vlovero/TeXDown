from setuptools import setup, find_packages


with open('README.md') as f:
    pypi_description = f.read()

setup(
    name='texdown',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['matplotlib', 'tqdm'],
    description='A python package that adds simple syntax to markdown files to make Github friendly LaTeX',
    long_description=pypi_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vlovero/',
    author='Vincent Lovero',
    author_email='vllovero@ucdavis.edu',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    keywords=['latex', 'github', 'markdown']
)
