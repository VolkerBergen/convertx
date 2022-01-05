import os
from setuptools import find_packages, setup

setup(
    name='convertx',
    version='0.0.1',
    description='Convert Word documents (docx) to clean HTML and Markdown',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    author='Volker Bergen',
    author_email='email@volkerbergen.de',
    url='http://github.com/VolkerBergen/convertx',
    packages=find_packages(),
    entry_points={"console_scripts": ["convertx=convertx.cli:main"]},
    keywords="docx word clean html markdown md",
    install_requires=["mammoth==1.4.18", "cobble>=0.1.3,<0.2", "html2text"],
    python_requires='>=2.7',
    license="BSD-2-Clause",
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
