import unittest
import spidertrack
from spidertrack import LivePosition
from datetime import datetime

class TestLiveTracker(unittest.TestCase):

	def setUp(self):
		self.kml_data = open("test_kml.kml").read()
		self.doc = spidertrack.LiveFeedDocument(self.kml_data)
	
	def testParseNoneInit(self):
		doc = spidertrack.LiveFeedDocument(None)
		self.assert_(doc.placemarks == None, "Check that doc is None for None data")

	def testKmlParse(self):
		self.assert_(self.doc.placemarks != None, "Check that placemarks is not none")
		self.assert_(len(self.doc.placemarks) == 13, "Check correct number of placemarks found")
	
	def testLastPosition(self):
		
		p = self.doc.last_position()
		self.assert_(p.lon == -88.566913333333, "Check correct longitude")
		self.assert_(p.lat == 43.994776666667, "Check correct latitude")
		self.assert_(p.height == 239.0, "Check correct height")

		d = datetime(2010, 11, 29, 20, 38, 50)
		self.assert_(p.time == d, "Check correct time")

		for cur_p in self.doc.placemarks:
			self.assert_(cur_p.time <= p.time, "Check that placemark is last in time")
	
class TestLivePosition(unittest.TestCase):

	def testParseNamestring(self):
		s = "2010-11-29 20:36:50 UTC in 'EAA B-17'"

		(id, date) = LivePosition.parse_namestring(s)
		self.assert_(id == "EAA B-17", "Check correct id string")
		d = datetime(2010, 11, 29, 20, 36, 50)
		self.assert_(d == date, "Check correct date")

	def testParseCoordstring(self):
		s = "-88.566913333333,43.994776666667,239.000000000000 "
		(lon, lat, height) = LivePosition.parse_coordstring(s)
		self.assert_(lon == -88.566913333333, "Check correct lon")
		self.assert_(lat == 43.994776666667, "Check correct lat")
		self.assert_(height == 239.0, "Check correct height")
	
	def testParseDescriptionstring(self):
		s = "Speed:0, Altitude:242, Heading:253, Description:"
		heading = LivePosition.parse_descriptionstring(s)
		self.assert_(heading == 253, "Test Correct heading")

