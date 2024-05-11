from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().strip().split('\n')

setup(
    name='backpack',
    version='0.1.0',
    author='Yura Mkrtchyan, Ani Ivanyan',
    author_email='contact1@example.com, contact1@example.com',
    description='Incremental backup system',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/YuraMkrtchyan404/OS_Snapshots.git',
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'backpack=src.cli:backpack',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
    ],
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False
)
