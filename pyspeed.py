import urllib2,base64
from cStringIO import StringIO
from xml.etree import ElementTree as ET
import re
import datetime

class LivePosition(object):

	def __init__(self):
		self.lat = 0.0
		self.lon = 0.0
		self.height = 0.0
		self.cog = 0.0
		self.sog = 0.0
		self.time = None
		self.feed_id = ""

	def __repr__(self):
		return "Liveposition(lat=%s, lon=%s, height=%s, cog=%s, time=%s, feed_id=%s" % \
		                     (self.lat, self.lon, self.height, self.cog, self.time, self.feed_id)
	@staticmethod
	def from_placemark_node(pmark_node):
		name = pmark_node.findtext("{http://www.opengis.net/kml/2.2}name")
		description = pmark_node.findtext("{http://www.opengis.net/kml/2.2}description")
		point_node = pmark_node.find("{http://www.opengis.net/kml/2.2}Point")
		if point_node == None:
			return None
		coordstring = point_node.findtext("{http://www.opengis.net/kml/2.2}coordinates")

		p = LivePosition()
		(p.feed_id, p.time) = LivePosition.parse_namestring(name)
		(p.lon, p.lat, p.height) = LivePosition.parse_coordstring(coordstring)
		(p.sog, p.cog) = LivePosition.parse_descriptionstring(description)
		return p


	@staticmethod
	def parse_descriptionstring(desc_str):
		m = re.match("Speed:(?P<sog>[0-9]+).*Heading:(?P<heading>[0-9]+)", desc_str)
		cog = float(m.group("heading"))
		sog = float(m.group("sog"))
		return (sog, cog)


	@staticmethod
	def parse_namestring(name_str):
		m = re.match("(?P<time>.*) in '(?P<id>.*)'", name_str)
		if m == None:
			return None
		else:
			dt = datetime.datetime.strptime(m.group("time"), 
			                                "%Y-%m-%d %H:%M:%S %Z")
			id = m.group("id")
			return (id, dt)

	@staticmethod
	def parse_coordstring(coord_str):
		(lonstr, latstr, heightstr) = coord_str.split(",")

		return (float(lonstr), float(latstr), float(heightstr))


		

class LiveFeedDocument(object):

	def __init__(self, kml_data, feed_id):
		self.feed_id = feed_id
		self.placemarks = self._parse_kml(kml_data)


	def _parse_kml(self, kml_data):
		if kml_data == None:
			return None
		
		doc = ET.parse(StringIO(kml_data)).getroot()
		folders = doc.findall("{http://www.opengis.net/kml/2.2}Document/" + \
								 "{http://www.opengis.net/kml/2.2}Folder/")
		folder = None
		id_str = "Track for '%s'" % self.feed_id
		for f in folders:
			if f.findtext("{http://www.opengis.net/kml/2.2}name") == id_str:
				folder = f
				break
		if folder == None:
			raise Exception("Cannot find track with id=" % (self.feed_id,))

		placemark_nodes = folder.findall("{http://www.opengis.net/kml/2.2}Placemark")
		placemarks = []
		for pnode in placemark_nodes:
			p = LivePosition.from_placemark_node(pnode)
			if p != None:
				placemarks.append(p)
		return placemarks
	
	def last_position(self):
		return self.placemarks[-1]

	



class FeedCommunicator(object):
	
	def __init__(self, url, username, password):
		self.url = url
		self.username = username
		self.password = password


	def load_data(self):
		request = urllib2.Request(self.url)
		b64creds = base64.encodestring("%s:%s" % (self.username, 
												self.password)).replace("\n", "")
		request.add_header("Authorization", "Basic %s" % (b64creds,))

		con = urllib2.urlopen(request)
		data = con.read()
		con.close()
		return data






