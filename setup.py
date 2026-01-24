"""Setup script for py1stauthor package."""
from setuptools import setup, find_packages
import os

# Read the contents of README file
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = ''

# Base dependencies (API only)
base_requirements = [
    'requests>=2.31.0',
]

# Agent dependencies (full functionality)
agent_requirements = [
    'openai>=1.0.0',
    'langgraph>=0.0.20',
    'langchain-core>=0.1.0',
]

setup(
    name='py1stauthor',
    version='0.1.0',
    author='Hongjin Qian',
    author_email='',
    description='A Python package for arXiv paper access and intelligent agent interaction',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/qhjqhj00/py1stauthor',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=base_requirements,
    extras_require={
        'agent': agent_requirements,
        'all': base_requirements + agent_requirements,
    },
    keywords='arxiv research papers agent llm',
    project_urls={
        'Bug Reports': 'https://github.com/qhjqhj00/py1stauthor/issues',
        'Source': 'https://github.com/qhjqhj00/py1stauthor',
        'Demo': 'https://1stauthor.com/',
        'API Documentation': 'https://data.rag.ac.cn/api/docs',
    },
)
