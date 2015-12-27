#!/usr/bin/env python

""" === ttcBusTracker.py ===

This file creates a python API for tracking TTC Bus stops using the
collection of xml files provided by Nextbus

Disclaimer: 
	Vikram is not responsible for the accuracy of ANY of the data
	output by this API
"""

# === Code Information ====
# This code was written in python 3.4
__author__		= 	"Vikram Venkatramanan"
__maintainer__	        = 	"Vikram Venkatramanan"
__email__ 		= 	"vikram.venkatramanan@mail.utoronto.ca"

__version__		=	"1.0.1"
__status__ 		= 	"Production"
__copyright__	        =	"All data copyright Toronto Transit Commission"


# === Import Block - Dependant Packages ===
from urllib.request import urlopen
from xml.etree.ElementTree import parse

__all__ = [
    # Classes
    'NoRouteError','BusStop', 'BusRoute',

    #Functions
    'GMapsRoute',
]

def GMapsRoute(point_A, point_B, key="key here"):
	""" Returns the distance and time between two locations

	Uses Google Maps Distance Matrix API to compute the distance and time between locations.
	Create a local the xml file with travel information

	@type origin: tuple
		Geographic Coordinates of start location
	@type destination: str
		Geographic Coordinates of end location
	@type filename: str
	@rtype: Tuple

	NOTE: Test cases for this function is not provided since the time of arrival
          varies 

	"""

	origin = str(point_A[0])+','+str(point_A[1])
	destination = str(point_B[0])+','+str(point_B[1])

	url = ("https://maps.googleapis.com/maps/api/distancematrix/xml?"
	    + "origins="+ origin
	    + "&destinations="+ destination
	    + "&mode=transit"
	    + "&key="+ key
	)

	_xml = urlopen(url)

	file_name = 'map.xml'
	_file = open(file_name,'wb')
	_file.write(_xml.read())
	_file.close()

	time = parse(file_name).find('row')[0][1][1].text
	distance = parse(file_name).find('row')[0][2][1].text

	return(distance, time)


class NoRouteError(Exception):
	"error Raised when the Route Number does not reffer to a bus Route"


class BusStop():
	" Is a Location where the bus will stop."
	# === Private Attributes ===
	# @type self._id: Str | None
	#	The id that uniquly identifies the stop, provided by ttc
	#	Some stops don't have an id
	# @type self._tag: Str | None
	#	The tag that uniquly identifies the coordinates, provided
	#	by Nextbus
	# 	
	# === Representational Invarients
	# - The id of the stop is always a 4-5 digit String of Numbers
	# - The tag of the stop is alwats a 4-5 digit String of Number 

	def __init__(self, route, stop_id, intersection, coordinates, tag = None):
		""" Creates a new BusStop

		=== Public Attributes ===
		@type self: BusStop
		@type self.intserction: Str
			The intersection where the stop is located
		@type self.coordinates: Tuple(float,float)
			The geographical coordinates (Latitude and Longitude)
			of the stop
		@type self.route: Str
			The Bus Route for which the stop belongs to
		@rtype: None

		>>> MyBus = BusStop(1,"0000","Subway Station",(0, 0))
		>>> MyBus.route
		1
		>>> MyBus.intersection
		'Subway Station'
		>>> MyBus.coordinates
		(0, 0)
 
		"""
		self._tag = tag
		self._id = stop_id
		self.intersection = intersection
		self.coordinates = coordinates
		self.route = route


class BusRoute():
	" Creates a new bus route."
	# === Private Attributes ===
	# @type self._bus_stops: List[BusStop]
	#	A list of all the Bus stops on the route
	# @type self._xml_file: URL
	#	The nextbus xml file for the bus route

	def __init__(self, route_no):
		"""	Gathers the Route information with the Bus number.
		Creates a local xml file with the Route information

		=== Public Attibutes ===
		@type self: BusRoute
		@type self.number: int
			The raw ttc Route Number, leaving out the extension. 
		@type self.name: Str
			The name of the Bus Route
		
		@type self.bus_stops: List(BusStop)
			Has a list of the bus stops on the route.
		@type self.north_stops:List(BusStop) | None
			Has the bus_stops in the North Stops.
			Is set to None if there are no North Buses
		@type self.south_stops:List(BusStop) | None
			Has the bus_stops in the South Stops.
			Is set to None if there are no South Buses
		@type self.east_stops:List(BusStop) | None
			Has the bus_stops in the East Stops.
			Is set to None if there are no East Buses
		@type self.west_stops:List(BusStop) | None
			Has the bus_stops in the West Stops.
			Is set to None if there are no West Buses
		
		@rtype: None

		>>> DawesBus = BusRoute(23)
		>>> DawesBus.number
		23
		>>> DawesBus.name
		'23-Dawes'

		"""
		# === Private Variables ===
		# @type _file: File
		#	The Local file that is temporarily opened for editing
		# @type _doc: File
		#	The parsed version of the xml file
		# @type _orientation:
		#	The direction in which the bus travels
		
		# === Representational Invarients ====
		# - The Orientation of the BusStop is either "N","S","E","W"

		self.number = route_no
		self.bus_stops = []

		url = (
			"http://webservices.nextbus.com/service/"
			+"publicXMLFeed?command=routeConfig&a=ttc&r="
			+str(self.number)
		)


		# Write the path to a local file
		self._xml_file = urlopen(url)
		data = self._xml_file.read()

		_file_name = 'rt' + str(self.number) + '.xml'
		_file = open(_file_name,'wb')
		_file.write(data)
		_file.close()

		# Parses the useful XML information
		_doc = parse(_file_name)

		try:
			self.name = _doc.getroot()[0].attrib['title']
		except KeyError:
			error = ("There is no TTC Bus Route corresponding to the number " 
			+ str(route_name)
			)
			raise NoRouteError(error)

		for route in _doc.findall('route'):
			
			for stop in route.findall('stop'):
				# Creates a BusStop and adds it to the list of BusStops
				self.bus_stops.append(BusStop(
					self.name, 
					stop.get('stopId'), stop.get('title'),
					(float(stop.get('lat')), float(stop.get('lon'))),
					stop.get('tag')
					))

			# Separates the Buses By Direction
			for direction in route.findall("direction"):
				title = direction.get('title')
				_orientation = title[0]

				# North Buses
				if _orientation == "N":
					self.north_stops = []
					for tag in direction.findall("stop"):
						for bus_stop in self.bus_stops:
							if stop.get('tag') == bus_stop._tag:
								self.north_stops.append(bus_stop)

				# East Buses
				elif _orientation == "E":
					self.east_stops = []
					for tag in direction.findall("stop"):
						for bus_stop in self.bus_stops:
							if stop.get('tag') == bus_stop._tag:
								self.east_stops.append(bus_stop)
				
				# South Buses
				elif _orientation == "S":
					self.south_stops = []
					for tag in direction.findall("stop"):
						for bus_stop in self.bus_stops:
							if stop.get('tag') == bus_stop._tag:
								self.south_stops.append(bus_stop)
				
				# West Buses
				else:
					self.west_stops = []
					for tag in direction.findall("stop"):
						for bus_stop in self.bus_stops:
							if stop.get('tag') == bus_stop._tag:
								self.west_stops.append(bus_stop)



	def bus_stop_coordinates(self):
		""" Provides a list of Bus Stop coordinates

		=== Public Attributes ===
		@type self: BusRoute
		@rtype:List(Str)  
		"""
		return [stop.coordinates for stop in self._bus_stops]


if __name__ == "__main__":
	import doctest
	doctest.testmod()


=======
#!/usr/bin/env python

""" === ttcBusTracker.py ===

This file creates a python API for tracking TTC Bus stops using the
collection of xml files provided by Nextbus

Disclaimer: 
	Vikram is not responsible for the accuracy of ANY of the data
	output by this API
"""

# === Code Information ====
# This code was written in python 3.4
__author__ 		= 	"Vikram Venkatramanan"
__maintainer__  	= 	"Vikram Venkatramanan"
__email__ 		= 	"vikram.venkatramanan@mail.utoronto.ca"

__version__	        = 	"1.0.1"
__status__ 		= 	"Production"
__copyright__	        = 	"All data copyright Toronto Transit Commission"


# === Import Block - Dependant Packages ===
from urllib.request import urlopen
from xml.etree.ElementTree import parse

__all__ = [
    # Classes
    'NoRouteError','BusStop', 'BusRoute',

    #Functions
    'GMapsRoute',
]

def GMapsRoute(point_A, point_B, key="AIzaSyAwNEyAajRMeSPwk6R19x61Laop_g2eEAE"):
	""" Returns the distance and time between two locations

	Uses Google Maps Distance Matrix API to compute the distance and time between locations.
	Create a local the xml file with travel information

	@type origin: tuple
		Geographic Coordinates of start location
	@type destination: str
		Geographic Coordinates of end location
	@type filename: str
	@rtype: Tuple

	NOTE: Test cases for this function is not provided since the time of arrival
          varies 

	"""

	origin = str(point_A[0])+','+str(point_A[1])
	destination = str(point_B[0])+','+str(point_B[1])

	url = ("https://maps.googleapis.com/maps/api/distancematrix/xml?"
	    + "origins="+ origin
	    + "&destinations="+ destination
	    + "&mode=transit"
	    + "&key="+ key
	)

	_xml = urlopen(url)

	file_name = 'map.xml'
	_file = open(file_name,'wb')
	_file.write(_xml.read())
	_file.close()

	time = parse(file_name).find('row')[0][1][1].text
	distance = parse(file_name).find('row')[0][2][1].text

	return(distance, time)


class NoRouteError(Exception):
	"error Raised when the Route Number does not reffer to a bus Route"


class BusStop():
	" Is a Location where the bus will stop."
	# === Private Attributes ===
	# @type self._id: Str | None
	#	The id that uniquly identifies the stop, provided by ttc
	#	Some stops don't have an id
	# 
	# === Representational Invarients
	# - The id of the stop is always a 4-5 digit String of Numbers 

	def __init__(self, route, stop_id, intersection, coordinates):
		""" Creates a new BusStop

		=== Public Attributes ===
		@type self: BusStop
		@type self.intserction: Str
			The intersection where the stop is located
		@type self.coordinates: Tuple(float,float)
			The geographical coordinates (Latitude and Longitude)
			of the stop
		@type self.route: Str
			The Bus Route for which the stop belongs to
		@rtype: None

		>>> MyBus = BusStop(1,"0000","Subway Station",(0, 0))
		>>> MyBus.route
		1
		>>> MyBus.intersection
		'Subway Station'
		>>> MyBus.coordinates
		(0, 0)
 
		"""
		self._id = stop_id
		self.intersection = intersection
		self.coordinates = coordinates
		self.route = route


class BusRoute():
	" Creates a new bus route."
	# === Private Attributes ===
	# @type self._bus_stops: List[BusStop]
	#	A list of all the Bus stops on the route
	# @type self._xml_file: URL
	#	The nextbus xml file for the bus route

	def __init__(self, route_no):
		"""	Gathers the Route information with the Bus number.
		Creates a local xml file with the Route information

		=== Public Attibutes ===
		@type self: BusRoute
		@type self.number: int
			The raw ttc Route Number, leaving out the extension. 
		@type self.name: Str
			The name of the Bus Route
		@rtype: None

		>>> DawesBus = BusRoute(23)
		>>> DawesBus.number
		23
		>>> DawesBus.name
		'23-Dawes'

		"""
		# === Private Variables ===
		# @type _file: File
		#	The Local file that is temporarily opened for editing
		# @type _doc: File
		#	The parsed version of the xml file

		self.number = route_no
		self._bus_stops = []

		url = (
			"http://webservices.nextbus.com/service/"
			+"publicXMLFeed?command=routeConfig&a=ttc&r="
			+str(self.number)
		)


		# Write the path to a local file
		self._xml_file = urlopen(url)
		data = self._xml_file.read()

		_file_name = 'rt' + str(self.number) + '.xml'
		_file = open(_file_name,'wb')
		_file.write(data)
		_file.close()

		# Parses the useful XML information
		_doc = parse(_file_name)

		try:
			self.name = _doc.getroot()[0].attrib['title']
		except KeyError:
			error = ("There is no TTC Bus Route corresponding to the number " 
			+ str(route_name)
			)
			raise NoRouteError(error)

		for route in _doc.findall('route'):
			for stop in route.findall('stop'):
				# Creates a BusStop and adds it to the list of BusStops
				self._bus_stops.append(BusStop(
					self.name, 
					stop.get('stopId'), stop.get('title'), 
					(float(stop.get('lat')), float(stop.get('lon')))
					))

	def bus_stops(self):
		""" Provides a list of Bus Stop addresses

		=== Public Attributes ===
		@type self: BusRoute
		@rtype:List(Str)  
		"""
		return [stop.intersection for stop in self._bus_stops]

	def bus_stop_coordinates(self):
		""" Provides a list of Bus Stop coordinates

		=== Public Attributes ===
		@type self: BusRoute
		@rtype:List(Str)  
		"""
		return [stop.coordinates for stop in self._bus_stops]


if __name__ == "__main__":
	import doctest
	doctest.testmod()
	print("Passed all Tests Cases")
>>>>>>> ef0c03d50983c65468c6ad9774b608b62906aae5
