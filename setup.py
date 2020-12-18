try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name="py-opc-ng",
    version="0.1.0",
    packages=['opcng'],
    author="Filippo Argiolas",
    author_email="filippo.argiolas@gmail.com",
    description="Python library to operate Alphasense OPC N2, N3 and R1 particle counters",
    url="https://baltig.infn.it/fargiolas/opc",
    license = 'GPLv3',
    keywords = ["alphasense", "opc"],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
	'Intended Audience :: Education',
	'Programming Language :: Python :: 3.3',
	'Programming Language :: Python :: 3.4',
	'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
	'Topic :: Scientific/Engineering :: Atmospheric Science',
	'Topic :: Software Development',
        'Topic :: System :: Hardware',
    ]
)
