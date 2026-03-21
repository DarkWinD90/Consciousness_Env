#!/usr/bin/env python3
"""Setup script for Consciousness System Environment."""

from setuptools import setup, find_packages
import os

# Read the README file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='consciousness-env',
    version='3.0.0',
    description='Multi-Layer Architecture for Synthetic Proto-Consciousness',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='DarkWinD90',
    url='https://github.com/DarkWinD90/Consciousness_Env',
    packages=find_packages(include=['appendices', 'phases', 'core', 'mcp', 'tools']),
    package_data={
        'mcp': ['*.json'],
    },
    include_package_data=True,
    py_modules=['consciousness_cli'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'consciousness=consciousness_cli:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='consciousness neuromorphic robotics snn simulation',
)
