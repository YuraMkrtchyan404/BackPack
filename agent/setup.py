from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().strip().split('\n')

setup(
    name='backpack',
    version='0.1.0',
    author='Yura Mkrtchyan, Ani Ivanyan',
    author_email='yura_mkrtchyan@edu.aua.am, ani_ivanyan2@edu.aua.am',
    description='Snapshot-based incremental backup system',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/YuraMkrtchyan404/BackPack',
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'backpack=src.cli:backpack',
        ],
    },
    classifiers=[
        'Natural Language :: English',
        'Operating System :: Ubuntu',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Backup System',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False
)