# ------------------------------------------------------------------------------
# Name:          setup.py
# Purpose:       install fcpxml package
#
# Authors:       Greg Chapman <gregc@mac.com>
#
# Copyright:     (c) 2024 Greg Chapman
# License:       MIT, see LICENSE
# ------------------------------------------------------------------------------

import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='fcpxml',
        version='0.9a1',
        description='A Final Cut Pro XML parser',
        packages=setuptools.find_packages(),
        python_requires='>=3.10',
    )
