# Based on https://blog.ionelmc.ro/2014/05/25/python-packaging

from setuptools import setup, find_packages

setup(
    name='craigs_web_sdr_backend',
    description='View radio spectrum using an SDR. Not innovative, just a learning exercise for me.',
    version='0.1.0',
    author='Craig J Perry',
    author_email='craigp84@gmail.com',
    url='https://github.com/craigjperry2/websdr',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
    # Minimal list here per https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=[
        'fastapi[all]'
        ,'numpy'
        ,'scipy'
        ,'pyrtlsdr'
    ],
    setup_requires=[
        'pytest-runner',
    ]
)
