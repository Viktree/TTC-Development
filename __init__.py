#!/usr/bin/env python

""" === __init__.py ===
A Toronto Public Transit Tracker written in Python.

Disclaimer: 
	Vikram is not responsible for the accuracy of ANY of the data
	output by this API

TTC-Development/
  README.md
  __init__.py
  ttcBusTracker.py/

"""

# === Code Information ====
__title__		=	'TTC-Development'
__url__	                =	'https://github.com/Viktree/TTC-Development.git'

__author__		= 	"Vikram Venkatramanan"
__email__ 		= 	"vikram.venkatramanan@mail.utoronto.ca"

__maintainer__          = 	"Vikram Venkatramanan"
__contact__		=	"vikram.venkatramanan@mail.utoronto.ca"

__version__		=	"1.0.1"
__status__ 		= 	"Production"
__license__		=       'Unlicense'
__copyright__		=	"All data copyright Toronto Transit Commission"
# This code was written in python 3.4

__all__ = [
    # Classes
    'NoRouteError','BusStop', 'BusRoute',

    #Functions
    'GMapsRoute',
]
