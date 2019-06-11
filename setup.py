from setuptools import setup

setup(
    name='staplestatter',
    version='1.1',
    packages=['staplestatter'],
    url='https://github.com/scholer/staplestatter',
    license='GNU General Public License v3 (GPLv3)',
    author='Rasmus Scholer Sorensen',
    author_email='rasmusscholer@gmail.com',
    description='Library, tools, and cadnano plugin for analyzing DNA origami designs created with cadnano.',
    keywords=[
        # "GEL", "Image", "Annotation", "PAGE", "Agarose", "Protein",
        # "SDS", "Gel electrophoresis", "Typhoon", "GelDoc",
        "DNA Origami", "cadnano", "plugin",
        "DNA", "DNA sequences", "melting temperature", "sequence manipulation",
        "Data analysis", "statistics", "plotting", "Data visualization",
    ],
    install_requires=[
        'pyyaml',
        'six',
        'biopython',
        'matplotlib',
        'svgwrite',
    ],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',

        # 'Topic :: Software Development :: Build Tools',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX :: Linux',
    ],
)
