import io
import setuptools


setuptools.setup(
    name='jpath-finder',
    version='1.0.2',
    description='An implementation of Json Path for python.',
    author='William Alvarez',
    author_email='alvarezpw@gmail.com',
    url='https://github.com/wapwallace/jpath_finder',
    license='Apache 2.0',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    packages=['jpath_finder'],
    test_suite='tests',
    install_requires=[
        'ply'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ],
)
