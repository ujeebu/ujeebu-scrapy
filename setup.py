#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()


requirements = ["scrapy"]

test_requirements = ['pytest>=3', ]

setup(
    author="Ujeebu",
    author_email='support@ujeebu.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Scrapy middleware for the Ujeebu API: headless Chrome rendering, rotating proxies, article extraction and Google SERP for Scrapy spiders",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='ujeebu, scrapy, scrapy middleware, web scraping, headless chrome, proxies, serp api',
    name='ujeebu_scrapy',
    packages=find_packages(include=['ujeebu_scrapy', 'ujeebu_scrapy.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://ujeebu.com',
    project_urls={
        'Documentation': 'https://ujeebu.com/docs',
        'Source': 'https://github.com/ujeebu/ujeebu-scrapy',
        'Issues': 'https://github.com/ujeebu/ujeebu-scrapy/issues',
        'Pricing': 'https://ujeebu.com/pricing',
    },
    version='0.2.3',
    zip_safe=False,
)
