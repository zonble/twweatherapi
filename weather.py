#!/usr/bin/env python
# encoding: utf-8
"""
weather.py

Copyright (c) 2009 Weizhong Yang (http://zonble.net)

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import os
import urllib
import re
import unittest
import urllib
from datetime import *
import time

os.environ['TZ'] = "Asia/Taipei"
time.tzset()

WeatherRootURL = "http://www.cwb.gov.tw/mobile/"
WeatherWarningURL = "http://www.cwb.gov.tw/mobile/warning/%(id)s.wml"
WeatherOverViewURL = "http://www.cwb.gov.tw/mobile/real.wml"
WeatherForecastURL = "http://www.cwb.gov.tw/mobile/forecast/city_%(#)02d.wml"
WeatherWeekURL = "http://www.cwb.gov.tw/mobile/week/%(location)s.wml"
WeatherTravelURL = "http://www.cwb.gov.tw/mobile/week_travel/%(location)s.wml"
Weather3DaySeaURL = "http://www.cwb.gov.tw/mobile/3sea/3sea%(#)d.wml"
WeatherNearSeaURL = "http://www.cwb.gov.tw/mobile/nearsea/nearsea%(#)d.wml"
WeatherTideURL = "http://www.cwb.gov.tw/mobile/tide/area%(#)d.wml"
WeatherOBSURL = "http://www.cwb.gov.tw/mobile/obs/%(location)s.wml"
WeatherGloabalURL = "http://www.cwb.gov.tw/pda/forecast/global/%(area)s/%(location)s.htm"

class WeatherWarning(object):
	def __init__(self):
		pass
	def fetch(self):
		try:
			url = urllib.urlopen(WeatherRootURL, proxies={})
		except:
			return
		warnings = []
		lines = url.readlines()
		for line in lines:
			m = re.search('<a href="warning/(.*).wml">(.*)</a>', line)
			if m is not None:
				id = m.group(1)
				name = m.group(2)
				item = {"id": id, "name": name.decode('utf-8'), "text": ""}
				warnings.append(item)
		for item in warnings:
			URLString = WeatherWarningURL % {"id": item['id']}
			try:
				url = urllib.urlopen(URLString, proxies={})
			except:
				continue
				pass
			lines = url.readlines()
			text = ""
			for line in lines:
				if line.find("<") == -1:
					line = line.rstrip()
					line = line.replace("  ", "")
					line = line.replace("　", "")
					line = line.replace(" ", "")
					if line.find("：") > -1:
						text = text + line + "\n"
					elif len(line) == 0:
						text = text + "\n"
					else:
						text = text + line
			item['text'] = text.decode('utf-8')
		return warnings

class TestWeatherWarning(unittest.TestCase):
	def setUp(self):
		self.warnings = WeatherWarning()
	def testWarning(self):
		result = self.warnings.fetch()
		# It is ok to fail here, since there might not be always
		# warnings.
		self.assertTrue(result)

class WeatherOverview(object):
	def __init__(self):
		self.html = ""
		self.plain = ""
		pass
	def fetch(self):
		try:
			url = urllib.urlopen(WeatherOverViewURL, proxies={})
		except:
			return
		lines = url.readlines()
		count = 0
		for line in lines[14:-9]:
			self.plain += line

class TestWeatherOverview(unittest.TestCase):
	def setUp(self):
		self.overview = WeatherOverview()
	def testOverview(self):
		self.overview.fetch()
		# self.assertNotEqual(len(self.overview.html), 0)
		self.assertNotEqual(len(self.overview.plain), 0)

class Forecast(object):
	def locations(self):
		return []
	def locationNameWithID(self, id):
		for location in self.locations():
			locationID = location['id']
			if str(id) == str(locationID):
				return location['location']
		return None
	def locationItemWithID(self, id):
		for location in self.locations():
			locationID = location['id']
			if str(id) == str(locationID):
				return location
		return None


WeatherForecastLocations = [
	{"location": u"台北市", "id": 1 , "weekLocation":"Taipei"},
	{"location": u"高雄市", "id": 2 , "weekLocation":"South"},
	{"location": u"基隆",  "id": 3 , "weekLocation":"North-East"},
	{"location": u"台北",  "id": 4 , "weekLocation":"North"},
	{"location": u"桃園",  "id": 5 , "weekLocation":"North"},
	{"location": u"新竹",  "id": 6 , "weekLocation":"North"},
	{"location": u"苗栗",  "id": 7 , "weekLocation":"North"},
	{"location": u"台中",  "id": 8 , "weekLocation":"Center"},
	{"location": u"彰化",  "id": 9 , "weekLocation":"Center"},
	{"location": u"南投",  "id": 10, "weekLocation":"Center"},
	{"location": u"雲林",  "id": 11, "weekLocation":"Center"},
	{"location": u"嘉義",  "id": 12, "weekLocation":"Center"},
	{"location": u"台南",  "id": 13, "weekLocation":"South"},
	{"location": u"高雄",  "id": 14, "weekLocation":"South"},
	{"location": u"屏東",  "id": 15, "weekLocation":"South"},
	{"location": u"恆春",  "id": 16, "weekLocation":"South"},
	{"location": u"宜蘭",  "id": 17, "weekLocation":"North-East"},
	{"location": u"花蓮",  "id": 18, "weekLocation":"South-East"},
	{"location": u"台東",  "id": 19, "weekLocation":"South-East"},
	{"location": u"澎湖",  "id": 20, "weekLocation":"Penghu"},
	{"location": u"金門",  "id": 21, "weekLocation":"Kinmen"},
	{"location": u"馬祖",  "id": 22, "weekLocation":"Matsu"}
	]

class WeatherForecast(Forecast):
	def locations(self):
		return WeatherForecastLocations
	def fetchWithID(self, id):
		locationItem = self.locationItemWithID(id)
		if locationItem is None:
			return None
		locationName = locationItem['location']
		weekLocation = locationItem['weekLocation']

		URLString = WeatherForecastURL % {"#": int(id)}
		try:
			url = urllib.urlopen(URLString, proxies={})
		except:
			return None

		lines = url.readlines()
		items = []

		title = ""
		rain = ""
		temperature = ""
		description = ""
		time = ""
		beginTime = ""
		endTime = ""
		
		isHandlingTime = False
		isHandlingDescription = False
		
		for line in lines:
			line = line.rstrip()
			if line.startswith("今") or line.startswith("明"):
				title = line.replace("<br />", "").decode("utf-8")
				isHandlingTime = True
			elif line.startswith("降雨機率："):
				line = line.replace("降雨機率：", "").replace("<br />", "").replace("%", "").replace(" ", "")
				rain = line
				item = {"title":title, "time":time, "beginTime":beginTime, "endTime":endTime, "description":description, "temperature":temperature, "rain":rain}
				items.append(item)
			elif line.startswith("溫度"):
				line = line.replace("溫度(℃)：", "").replace("<br />", "")
				temperature = line
			elif isHandlingTime is True:
				time = line
				today = date.today()
				month = int(today.month)
				year = int(today.year)
				if month == 12 and int(line[0:2]) == 1:
					year = year + 1
				begin = datetime(year, int(line[0:2]), int(line[3:5]), int(line[6:8]), int(line[9:11]))
				beginTime = begin.__str__()
				end = datetime(year, int(line[12:14]), int(line[15:17]), int(line[18:20]), int(line[21:23]))
				endTime = end.__str__()
				time = beginTime + "/" + endTime
				
				isHandlingTime = False
				isHandlingDescription = True
			elif isHandlingDescription is True:
				if line.startswith("<br />") is False and len(line) > 2:
					description = line.replace("<br />", "")
					description = description.decode("utf-8")
					isHandlingDescription = False
		return {"locationName":locationName, "items":items, "id": id, "weekLocation":weekLocation}

class TestWeatherForecast(unittest.TestCase):
	def setUp(self):
		self.forecest = WeatherForecast()
	def testForecast(self):
		for i in range(1, 23):
			result = self.forecest.fetchWithID(i)
			self.assertTrue(result['locationName'])
			self.assertTrue(result['weekLocation'])
			self.assertTrue(result['id'])
			items = result['items']
			self.assertEqual(int(len(items)), 3)
			for item in items:
				self.assertTrue(item['title'])
				self.assertEqual(item['title'].find("<"), -1)
				self.assertTrue(item['time'])
				self.assertTrue(item['beginTime'])
				self.assertTrue(item['endTime'])
				self.assertTrue(item['description'])
				self.assertTrue(item['temperature'])
				self.assertTrue(item['rain'])

WeatherWeekLocations = [
	{"location": u"台北市", "id": "Taipei"},
	{"location": u"北部",  "id": "North"},
	{"location": u"中部",  "id": "Center"},
	{"location": u"南部",  "id": "South"},
	{"location": u"東北部", "id": "North-East"},
	{"location": u"東部",  "id": "East"},
	{"location": u"東南部", "id": "South-East"},
	{"location": u"澎湖",  "id": "Penghu"},
	{"location": u"金門",  "id": "Kinmen"},
	{"location": u"馬祖",  "id": "Matsu"},
	]

class WeatherWeek(Forecast):
	def locations(self):
		return WeatherWeekLocations
	def handleLines(self, URLString, locationName, name):
		try:
			url = urllib.urlopen(URLString, proxies={})
		except:
			return None
		lines = url.readlines()
		publishTime = ""
		items = []
		temperature = ""
		description = ""
		time = ""
		
		mainLine = ""
		
		for line in lines:
			line = line.rstrip()
			if line.find("<p>發布時間") > -1:
				mainLine = line
				break

		lines = mainLine.split('</p><p> ')
		firstLine = lines[0].strip()
		year = datetime.now().year
		publishTime = datetime(year, int(firstLine[24:26]), int(firstLine[27:29]), int(firstLine[30:32]), int(firstLine[33:35])).__str__()

		for line in lines[1:]:
			line = line.strip()
			parts = line.split('<br />')
			time = date(year, int(parts[0][0:2]), int(parts[0][3:5])).__str__()
			description = parts[0][11:].decode("utf-8")
			temperature = parts[1].replace('</p>', '')
			item = {"date": time, "description": description, "temperature": temperature}
			items.append(item)
		result = {"locationName":locationName, "id":name, "publishTime": publishTime, "items": items}
		return result
	def fetchWithID(self, name):
		locationName = self.locationNameWithID(name)
		if locationName is None:
			return None
		URLString = WeatherWeekURL % {"location": name}
		return self.handleLines(URLString, locationName, name)


class TestWeatherWeek(unittest.TestCase):
	def setUp(self):
		self.week = WeatherWeek()
	def testForecast(self):
		for item in self.week.locations():
			locationName = item['id']
			items = self.week.fetchWithID(locationName)
			self.assertTrue(items)
			self.assertTrue(items["publishTime"])
			self.assertTrue(items["items"])
			self.assertEqual(len(items["items"]), 7)

WeatherWeekTravelLocations = [
	{"location": u"陽明山", "id": "Yangmingshan"},
	{"location": u"拉拉山", "id": "Lalashan"},
	{"location": u"梨山", "id": "Lishan"},
	{"location": u"合歡山", "id": "HehuanMountain"},
	{"location": u"日月潭", "id": "SunMoonLake"},
	{"location": u"溪頭", "id": "Xitou"},
	{"location": u"阿里山", "id": "Alishan"},
	{"location": u"玉山", "id": "Yushan"},
	{"location": u"墾丁", "id": "Kenting"},
	{"location": u"龍洞", "id": "Longdong"},
	{"location": u"太魯閣", "id": "Taroko"},
	{"location": u"三仙台", "id": "Sanxiantai"},
	{"location": u"綠島", "id": "Ludao"},
	{"location": u"蘭嶼", "id": "Lanyu"}
	]

class WeatherWeekTravel(WeatherWeek):
	def locations(self):
		return WeatherWeekTravelLocations
	def fetchWithID(self, name):
		locationName = self.locationNameWithID(name)
		if locationName is None:
			return None
		URLString = WeatherTravelURL % {"location": name}
		return self.handleLines(URLString, locationName, name)

class TestWeatherWeekTravel(TestWeatherWeek):
	def setUp(self):
		self.week = WeatherWeekTravel()

Weather3DaySeaLocations = [
	{"location": u"黃海南部海面", "id": 1},
	{"location": u"花鳥山海面", "id": 2},
	{"location": u"東海北部海面",  "id": 3},
	{"location": u"浙江海面", "id": 4},
	{"location": u"東海南部海面", "id": 5},
	{"location": u"台灣北部海面",  "id": 6},
	{"location": u"台灣海峽北部", "id": 7},
	{"location": u"台灣海峽南部",  "id": 8},
	{"location": u"台灣東北部海面",  "id": 9},
	{"location": u"台灣東南部海面",  "id": 10},
	{"location": u"巴士海峽", "id": 11},
	{"location": u"廣東海面", "id": 12},
	{"location": u"東沙島海面",  "id": 13},
	{"location": u"中西沙島海面",  "id": 14},
	{"location": u"南沙島海面",  "id": 15}
	]

class Weather3DaySea(Forecast):
	def locations(self):
		return Weather3DaySeaLocations
	def fetchWithID(self, id):
		locationName = self.locationNameWithID(id)
		if locationName is None:
			return None

		URLString = Weather3DaySeaURL % {"#": int(id)}
		try:
			url = urllib.urlopen(URLString, proxies={})
		except:
			return None
		lines = url.readlines()
		didHandlingPublishTime = False
		items = []
		count = 0
		publishTime = ""
		time = ""
		description = ""
		wind = ""
		windScale = ""
		wave = ""

		for line in lines:
			line = line.rstrip()
			if didHandlingPublishTime:
				if count is 0:
					line = line.replace("<br />", "")
					parts = line.split("/")

					if len(parts) >  1:
						month = int(parts[0])
						day = int(parts[1])
						year = int(date.today().year)
						if date.today().month == 12 and month == 1:
							year = year + 1
						time = date(year, month, day).__str__()
				elif count is 1:
					description = line.replace("<br />", "").decode("utf-8")
				elif count is 2:
					wind = line.replace("<br />", "").decode("utf-8")
				elif count is 3:
					windScale = line.replace("<br />", "").decode("utf-8")
				elif count is 4:
					wave = line.replace("<br />", "").decode("utf-8")
				elif count is 5:
					item = {"date": time, "description": description, "wind": wind, "windScale": windScale, "wave": wave}
					items.append(item)
					if len(items) >= 3:
						break
				if count >= 5:
					count = 0
				else:
					count = count + 1
			if line.find("發布時間") > -1:
				line = line[25:].replace("</p><p>", "")
				month = int(line[0:2])
				year = int(date.today().year)
				if date.today().month == 12 and month == 1:
					year = year + 1
				publishTime = datetime(year, month, int(line[3:5]), int (line[6:8]), int(line[9:11])).__str__()
				didHandlingPublishTime = True
				count = 0
		result = {"locationName":locationName, "id":id, "publishTime": publishTime, "items": items}
		return result

class TestWeather3DaySea(unittest.TestCase):
	def setUp(self):
		self.sea = Weather3DaySea()
	def testForecast(self):
		for i in range(1, 15):
			result = self.sea.fetchWithID(i)
			self.assertTrue(result)
			self.assertTrue(result["publishTime"])
			self.assertTrue(result["items"])
			self.assertEqual(len(result["items"]), 3)

WeatherNearSeaLocations = [
	{"location": u"釣魚台海面", "id":1},
	{"location": u"彭佳嶼基隆海面", "id":2},
	{"location": u"宜蘭蘇澳沿海", "id":3},
	{"location": u"新竹鹿港沿海", "id":4},
	{"location": u"澎湖海面", "id":5},
	{"location": u"鹿港東石沿海", "id":6},
	{"location": u"東石安平沿海", "id":7},
	{"location": u"安平高雄沿海", "id":8},
	{"location": u"高雄枋寮沿海", "id":9},
	{"location": u"枋寮恆春沿海", "id":10},
	{"location": u"鵝鑾鼻沿海", "id":11},
	{"location": u"成功大武沿海", "id":12},
	{"location": u"綠島蘭嶼海面", "id":13},
	{"location": u"花蓮沿海", "id":14},
	{"location": u"金門海面", "id":15},
	{"location": u"馬祖海面", "id":16}
	]

class WeatherNearSea(Forecast):
	def locations(self):
		return WeatherNearSeaLocations
	def handleDate(self, line):
		line = line.strip()
		today = date.today()
		month = int(today.month)
		year = int(today.year)
		if month == 12 and int(line[0:2]) == 1:
			year = year + 1
		theDate = datetime(year, int(line[0:2]), int(line[3:5]), int(line[6:8]), int(line[9:11]))
		return theDate.__str__()
	def fetchWithID(self, id):
		locationName = self.locationNameWithID(id)
		if locationName is None:
			return None

		URLString = WeatherNearSeaURL % {"#": int(id)}
		try:
			url = urllib.urlopen(URLString, proxies={})
		except:
			return None
		
		lines = url.readlines()
		publishTime = ""
		validTime = ""
		validBeginTime = ""
		validEndTime = ""
		didHandledTime = False
		handlingData = False
		description = ""
		wind = ""
		windScale = ""
		wave = ""
		waveLevel = ""
		lineCount = 0
		for line in lines:
			line = line.rstrip()
			if line.find("發布時間:") > -1:
				line = line[20:].replace("<br />", "")
				publishTime = self.handleDate(line)
			elif line.find("有效時間:") > -1:
				line = line[20:]
				parts = line.split("~")
				if len(parts) > 1:
					validBeginTime = self.handleDate(parts[0])
					validEndTime = self.handleDate(parts[1])
					validTime = validBeginTime + "/" + validEndTime
				didHandledTime = True
			elif didHandledTime is True and line.startswith("<p>"):
				handlingData = True
				lineCount = 1
			elif handlingData is True:
				if line.find("</p>") > -1:
					result = {"locationName": locationName, "id": id, "description": description,
						"publishTime": publishTime, "validBeginTime": validBeginTime, 
						"validEndTime": validEndTime, "validTime": validTime,
						"wind": wind, "windScale": windScale, "wave": wave,
						"waveLevel": waveLevel
						}
					return result
				line = line.replace("<br />", "").decode("utf-8")
				if lineCount is 1:
					description = line
				elif lineCount is 2:
					wind = line
				elif lineCount is 3:
					windScale = line
				elif lineCount is 4:
					wave = line
				elif lineCount is 5:
					waveLevel = line
				lineCount = lineCount + 1
		return None

class TestWeatherNearSea(unittest.TestCase):
	def setUp(self):
		self.model = WeatherNearSea()
	def testForecast(self):
		for i in range(1, 16):
			result = self.model.fetchWithID(i)
			self.assertTrue(result)
			self.assertTrue(result["locationName"])
			self.assertTrue(result["id"])
			self.assertTrue(result["publishTime"])
			self.assertTrue(result["validBeginTime"])
			self.assertTrue(result["validEndTime"])
			self.assertTrue(result["validTime"])
			self.assertTrue(result["wind"])
			self.assertTrue(result["windScale"])
			self.assertTrue(result["wave"])
			self.assertTrue(result["waveLevel"])

WeatherTideLocations = [
	{"location": u"基隆", "id":1},
	{"location": u"福隆", "id":2},
	{"location": u"鼻頭角", "id":3},
	{"location": u"石門", "id":4},
	{"location": u"淡水", "id":5},
	{"location": u"大園", "id":6},
	{"location": u"新竹", "id":7},
	{"location": u"苗栗", "id":8},
	{"location": u"梧棲", "id":9},
	{"location": u"王功", "id":10},
	{"location": u"台西", "id":11},
	{"location": u"東石", "id":12},
	{"location": u"將軍", "id":13},
	{"location": u"安平", "id":14},
	{"location": u"高雄", "id":15},
	{"location": u"東港", "id":16},
	{"location": u"南灣", "id":17},
	{"location": u"澎湖", "id":18},
	{"location": u"蘇澳", "id":19},
	{"location": u"頭城", "id":20},
	{"location": u"花蓮", "id":21},
	{"location": u"台東", "id":22},
	{"location": u"成功", "id":23},
	{"location": u"蘭嶼", "id":24},
	{"location": u"馬祖", "id":25},
	{"location": u"金門", "id":26},
	]

class WeatherTide(Forecast):
	def locations(self):
		return WeatherTideLocations
	def handelWave(self, line, theDate):
		line = line.rstrip()[7:].replace("<br />", "")
		parts = line.split(" ")
		if len(parts) > 1:
			shortTime = parts[0]
			height = parts[1]
			hour = int(shortTime[0:2])
			minute = int(shortTime[3:5])
			longTime = datetime(theDate.year, theDate.month, theDate.day, hour, minute).__str__()
			return {"longTime": longTime, "shortTime": shortTime, "height": height}
		
	def fetchWithID(self, id):
		locationName = self.locationNameWithID(id)
		if locationName is None:
			return None

		URLString = WeatherTideURL % {"#": int(id)}
		try:
			url = urllib.urlopen(URLString, proxies={})
		except:
			return None
		lines = url.readlines()
		items = []
		theDate = None
		time = ""
		lunarTime = ""
		isHandlingItem = False
		low = {"longTime": "", "shortTime": "", "height": ""}
		high = {"longTime": "", "shortTime": "", "height": ""}
		tides = []
		for line in lines:
			line = line.rstrip()
			if isHandlingItem is False and line.startswith("<p>") and line.find("<br />") > -1:
				isHandlingItem = True
			if isHandlingItem is True:
				if line.startswith("<p>") and line.find("<br />") > -1:
					line = line.replace("<p>", "").replace("<br />", "")
					year = int(line[0:4])
					month = int(line[5:7])
					day = int(line[8:10])
					theDate = date(year, month, day)
					time = theDate.__str__()
				elif line.find("農曆") > -1:
					lunarTime = line.replace("<br />", "").decode("utf-8")
				elif line.find("乾潮") > -1:
					low = self.handelWave(line, theDate)
					low["name"] = u"乾潮"
					tides.append(low)
				elif line.find("滿潮") > -1:
					high = self.handelWave(line, theDate)
					high["name"] = u"滿潮"
					tides.append(high)
				elif line.find("--------") > -1:
					item = {"date": time, "lunarDate": lunarTime, "low": low, "high": high, "tides":tides}
					items.append(item)
					tides = []
					if len(items) >= 3:
						result = {"locationName": locationName, "id": id, "items": items}
						return result

class TestWeatherTide(unittest.TestCase):
	def setUp(self):
		self.model = WeatherTide()
	def testForecast(self):
		for i in range(1, 26):
			result = self.model.fetchWithID(i)
			self.assertEqual(int(len(result['items'])), 3)
			for item in result['items']:
				self.assertTrue(item['date'])
				self.assertTrue(item['lunarDate'])
				self.assertTrue(item['high'])
				self.assertTrue(item['low'])

WeatherImageURL = [

	{"id": "weather", "URL":"http://www.cwb.gov.tw/V6/forecast/fcst/Data/I04_small.jpg"},
	{"id": "weather_24", "URL":"http://www.cwb.gov.tw/V6/forecast/fcst/Data/SFC24.jpg"},

	{"id": "rain", "URL":"http://www.cwb.gov.tw/V6/observe/rainfall/Data/hk.jpg"},
	{"id": "rain_12", "URL":"http://www.cwb.gov.tw/V6/forecast/fcst/Data/QPF_ChFcstPrecip12.jpg"},
	{"id": "rain_24", "URL":"http://www.cwb.gov.tw/V6/forecast/fcst/Data/QPF_ChFcstPrecip24.jpg"},
	
	{"id": "radar", "URL":"http://www.cwb.gov.tw/V6/observe/radar/Data/MOS_1024/MOS.jpg"},
	{"id": "radar2", "URL":"http://www.cwb.gov.tw/V6/observe/radar/Data/MOS2_1024/MOS2.jpg"},

	{"id": "color_taiwan", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s3p/s3p.jpg"},
	{"id": "color_asia", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s1p/s1p.jpg"},
	{"id": "color_world", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s0p/s0p.jpg"},

	{"id": "hilight_taiwan", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s3q/s3q.jpg"},
	{"id": "hilight_asia", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s1q/s1q.jpg"},
	{"id": "hilight_world", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s0q/s0q.jpg"},

	{"id": "bw_taiwan", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s3o/s3o.jpg"},
	{"id": "bw_asia", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s1o/s1o.jpg"},
	{"id": "bw_world", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/s0o/s0o.jpg"},

	{"id": "light_taiwan", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/sbo/sbo.jpg"},
	{"id": "light_asia", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/sao/sao.jpg"},
	{"id": "light_world", "URL":"http://www.cwb.gov.tw/V6/observe/satellite/Data/sco/sco.jpg"},

	{"id": "wave", "URL":"http://www.cwb.gov.tw/V6/forecast/fcst/Data/I12_small.jpg"},
	{"id": "wave_24", "URL":"http://www.cwb.gov.tw/V6/forecast/fcst/Data/WFC24.jpg"},
	{"id": "wave_36", "URL":"http://www.cwb.gov.tw/V6/forecast/fcst/Data/WFC36.jpg"},
	{"id": "wave_48", "URL":"http://www.cwb.gov.tw/V6/forecast/fcst/Data/WFC48.jpg"},
]

WeatherOBSLocations = [
	{"location": u"基隆", "id": "46694", "area":u"北部", "areaID":"north"},
	{"location": u"台北", "id": "46692", "area":u"北部", "areaID":"north"},
	{"location": u"板橋", "id": "46688", "area":u"北部", "areaID":"north"},
	{"location": u"陽明山","id": "46693", "area":u"北部", "areaID":"north"},
	{"location": u"淡水", "id": "46690", "area":u"北部", "areaID":"north"},
	{"location": u"新店", "id": "A0A9M", "area":u"北部", "areaID":"north"},
	{"location": u"桃園", "id": "46697", "area":u"北部", "areaID":"north"},
	# {"location": u"新屋", "id": "C0C45", "area":u"北部", "areaID":"north"},
	{"location": u"新竹", "id": "46757", "area":u"北部", "areaID":"north"},
	{"location": u"雪霸", "id": "C0D55", "area":u"北部", "areaID":"north"},
	{"location": u"三義", "id": "C0E53", "area":u"北部", "areaID":"north"},
	{"location": u"竹南", "id": "C0E42", "area":u"北部", "areaID":"north"},

	{"location": u"台中", "id": "46749", "area":u"中部", "areaID":"center"},
	{"location": u"梧棲", "id": "46777", "area":u"中部", "areaID":"center"},
	{"location": u"梨山", "id": "C0F86", "area":u"中部", "areaID":"center"},
	{"location": u"員林", "id": "C0G65", "area":u"中部", "areaID":"center"},
	{"location": u"鹿港", "id": "C0G64", "area":u"中部", "areaID":"center"},
	{"location": u"日月潭","id": "46765", "area":u"中部", "areaID":"center"},
	{"location": u"廬山", "id": "C0I01", "area":u"中部", "areaID":"center"},
	{"location": u"合歡山","id": "C0H9C", "area":u"中部", "areaID":"center"},
	{"location": u"虎尾", "id": "C0K33", "area":u"中部", "areaID":"center"},
	{"location": u"草嶺", "id": "C0K24", "area":u"中部", "areaID":"center"},
	{"location": u"嘉義", "id": "46748", "area":u"中部", "areaID":"center"},
	{"location": u"阿里山","id": "46753", "area":u"中部", "areaID":"center"},
	{"location": u"玉山", "id": "46755", "area":u"中部", "areaID":"center"},

	{"location": u"台南", "id": "46741", "area":u"南部", "areaID":"south"},
	{"location": u"高雄", "id": "46744", "area":u"南部", "areaID":"south"},
	{"location": u"甲仙", "id": "C0V25", "area":u"南部", "areaID":"south"},
	{"location": u"三地門","id": "C0R15", "area":u"南部", "areaID":"south"},
	{"location": u"恆春", "id": "46759", "area":u"南部", "areaID":"south"},

	{"location": u"宜蘭", "id": "46708", "area":u"東部", "areaID":"east"},
	{"location": u"蘇澳", "id": "46706", "area":u"東部", "areaID":"east"},
	{"location": u"太平山","id": "C0U71", "area":u"東部", "areaID":"east"},
	{"location": u"花蓮", "id": "46699", "area":u"東部", "areaID":"east"},
	{"location": u"玉里", "id": "C0Z06", "area":u"東部", "areaID":"east"},
	{"location": u"成功", "id": "46761", "area":u"東部", "areaID":"east"},
	{"location": u"台東", "id": "46766", "area":u"東部", "areaID":"east"},
	{"location": u"大武", "id": "46754", "area":u"東部", "areaID":"east"},

	{"location": u"澎湖",  "id": "46735", "area":u"外島", "areaID":"island"},
	{"location": u"金門",  "id": "46711", "area":u"外島", "areaID":"island"},
	{"location": u"馬祖",  "id": "46799", "area":u"外島", "areaID":"island"},
	{"location": u"綠島",  "id": "C0S73", "area":u"外島", "areaID":"island"},
	{"location": u"蘭嶼",  "id": "46762", "area":u"外島", "areaID":"island"},
	{"location": u"彭佳嶼", "id": "46695", "area":u"外島", "areaID":"island"},
	{"location": u"東吉島", "id": "46730", "area":u"外島", "areaID":"island"},
	{"location": u"琉球嶼", "id": "C0R27", "area":u"外島", "areaID":"island"},
]

class WeatherOBS(Forecast):
	def locations(self):
		return WeatherOBSLocations
	def fetchWithID(self, id):
		locationName = self.locationNameWithID(id)
		if locationName is None:
			return None

		URLString = WeatherOBSURL % {"location": id}
		try:
			url = urllib.urlopen(URLString, proxies={})
		except:
			return None

		isHandlingTime = False

		lines = url.readlines()
		time = ""
		description = ""
		temperature = ""
		rain = ""
		windDirection = ""
		windScale = ""
		gustWindScale = ""
		
		for line in lines:
			line = line.rstrip()
			if isHandlingTime is True:
				if line.startswith("<") is not True:
					year = datetime.now().year
					month = int(line[0:2])
					day = int(line[3:5])
					hour = int(line[6:8])
					minute = int(line[9:11])
					time = datetime(year, month, day, hour, minute).__str__()
					isHandlingTime = False
			elif line.find("地面觀測") > -1:
				isHandlingTime = True
			elif line.find("天氣現象") > -1:
				description = line[len("天氣現象:"):len("<br />") * -1]
				try:
					description = description.decode("ascii")
				except:
					description = description.decode("utf-8")
			elif line.find("溫度") > -1:
				temperature = float(line[len("溫度(℃):"):len("<br />") * -1])
			elif line.find("累積雨量") > -1:
				rain = line[len("累積雨量(毫米):"):len("<br />") * -1]
			elif line.find("風向") > -1:
				windDirection = line[len("風向:"):len("<br />") * -1]
				try:
					windDirection = windDirection.decode("ascii")
				except:
					windDirection = windDirection.decode("utf-8")
			elif line.find("風力") > -1:
				windScale = line[len("風力(級):"):len("<br />") * -1]
				try:
					windScale = windScale.decode("ascii")
				except:
					windScale = windScale.decode("utf-8")
			elif line.find("陣風") > -1:
				gustWindScale = line[len("陣風(級):"):len("<br />") * -1]
				try:
					gustWindScale = gustWindScale.decode("ascii")
				except:
					gustWindScale = gustWindScale.decode("utf-8")
			elif line.find("</p>") > -1:
				result = {"locationName": locationName, "id": id, "time": time, "description": description, "temperature": temperature, "rain": rain, "windDirection": windDirection, "windScale": windScale, "gustWindScale": gustWindScale}
				return result

class TestWeatherOBS(unittest.TestCase):
	def setUp(self):
		self.model = WeatherOBS()
	def testForecast(self):
		for item in self.model.locations():
			result = self.model.fetchWithID(item['id'])
			self.assertTrue(result)
			self.assertTrue(result["locationName"])
			self.assertTrue(result["id"])
			self.assertTrue(result["time"])
			self.assertTrue(result["description"])
			self.assertTrue(result["temperature"])
			self.assertTrue(result["rain"])
			self.assertTrue(result["windDirection"])
			self.assertTrue(result["windScale"])
			self.assertTrue(result["gustWindScale"])

WeatherGlobalLocations = [
	{"location": u"東京", "id": "TOKYO", "area":u"亞洲", "areaID":"asia"},
	{"location": u"大阪", "id": "OSAKA", "area":u"亞洲", "areaID":"asia"},
	{"location": u"首爾", "id": "SEOUL", "area":u"亞洲", "areaID":"asia"},
	{"location": u"曼谷", "id": "BANGKOK", "area":u"亞洲", "areaID":"asia"},
	{"location": u"雅加達", "id": "JAKARTA", "area":u"亞洲", "areaID":"asia"},
	{"location": u"吉隆坡", "id": "KUALALUMPUR", "area":u"亞洲", "areaID":"asia"},
	{"location": u"新加坡", "id": "SINGAPORE", "area":u"亞洲", "areaID":"asia"},
	{"location": u"馬尼拉", "id": "MANILA", "area":u"亞洲", "areaID":"asia"},
	{"location": u"加德滿都", "id": "KATMANDU", "area":u"亞洲", "areaID":"asia"},
	{"location": u"胡志明市", "id": "HO-CHI-MINH", "area":u"亞洲", "areaID":"asia"},
	{"location": u"河內", "id": "HA-NOI", "area":u"亞洲", "areaID":"asia"},
	{"location": u"新德里", "id": "NEW-DELHI", "area":u"亞洲", "areaID":"asia"},
	{"location": u"伊斯坦堡", "id": "ISTANBUL", "area":u"亞洲", "areaID":"asia"},
	{"location": u"莫斯科", "id": "MOSCOW", "area":u"亞洲", "areaID":"asia"},
	{"location": u"海參威", "id": "VLADIVOSTOK", "area":u"亞洲", "areaID":"asia"},
	{"location": u"伯力", "id": "HABAROVSK", "area":u"亞洲", "areaID":"asia"},
	{"location": u"威靈頓", "id": "WELLINGTON", "area":u"亞洲", "areaID":"asia"},
	{"location": u"奧克蘭", "id": "AUCKLAND", "area":u"亞洲", "areaID":"asia"},
	{"location": u"墨爾本", "id": "MELBOURNE", "area":u"亞洲", "areaID":"asia"},
	{"location": u"雪梨", "id": "SYDNEY", "area":u"亞洲", "areaID":"asia"},
	{"location": u"伯斯", "id": "PERTH", "area":u"亞洲", "areaID":"asia"},
	{"location": u"布里斯班", "id": "BRISBANE", "area":u"亞洲", "areaID":"asia"},

	# {"location": u"關島", "id": "GUAM", "area":u"美洲", "areaID":"america"},
	{"location": u"檀香山", "id": "HONOLULU", "area":u"美洲", "areaID":"america"},
	{"location": u"洛杉磯", "id": "LOSANGELES", "area":u"美洲", "areaID":"america"},
	{"location": u"舊金山", "id": "SANFRANCISCO", "area":u"美洲", "areaID":"america"},
	{"location": u"西雅圖", "id": "SEATTLE", "area":u"美洲", "areaID":"america"},
	{"location": u"紐約", "id": "NEWYORK", "area":u"美洲", "areaID":"america"},
	{"location": u"芝加哥", "id": "CHICAGO", "area":u"美洲", "areaID":"america"},
	{"location": u"邁阿密", "id": "MIAMI", "area":u"美洲", "areaID":"america"},
	{"location": u"多倫多", "id": "TORONTO", "area":u"美洲", "areaID":"america"},
	{"location": u"溫哥華", "id": "VANCOUVER", "area":u"美洲", "areaID":"america"},
	{"location": u"蒙特婁", "id": "MONTREAL", "area":u"美洲", "areaID":"america"},
	{"location": u"墨西哥城", "id": "MEXICO-CITY", "area":u"美洲", "areaID":"america"},
	{"location": u"里約熱內盧", "id": "RIO-DE-JANEIRO", "area":u"美洲", "areaID":"america"},
	{"location": u"聖地牙哥（智利）", "id": "SANTIAGO", "area":u"美洲", "areaID":"america"},
	{"location": u"利瑪", "id": "LIMA", "area":u"美洲", "areaID":"america"},
	{"location": u"拉斯維加斯", "id": "LASVEGAS", "area":u"美洲", "areaID":"america"},
	{"location": u"華盛頓特區", "id": "WASHINGTON-DC", "area":u"美洲", "areaID":"america"},
	{"location": u"布宜諾斯艾利斯", "id": "BUENOS-AIRES", "area":u"美洲", "areaID":"america"},

	{"location": u"奧斯陸", "id": "OSLO", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"馬德里", "id": "MADRID", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"哥本哈根", "id": "COPENHAGEN", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"赫爾辛基", "id": "HELSINKI", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"法蘭克福", "id": "FRANKFURT", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"柏林", "id": "BERLIN", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"日內瓦", "id": "GENEVA", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"布魯塞爾", "id": "BRUXELLES", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"倫敦", "id": "LONDON", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"巴黎", "id": "PARIS", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"維也納", "id": "VIENNA", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"羅馬", "id": "ROME", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"威尼斯", "id": "VENEZIA", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"布達佩斯", "id": "BUDAPEST", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"雅典", "id": "ATHENS", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"華沙", "id": "WARSZAWA", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"布拉格", "id": "PRAHA", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"開羅", "id": "CAIRO", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"阿姆斯特丹", "id": "AMSTERDAM", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"約翰尼斯堡", "id": "JOHANNESBURG", "area":u"歐非", "areaID":"europe_africa"},
	{"location": u"斯德哥爾摩", "id": "STOCKHOLM", "area":u"歐非", "areaID":"europe_africa"},

	{"location": u"廣州", "id": "GUANGZHOU", "area":u"中國大陸", "areaID":"china"},
	{"location": u"香港", "id": "HONGKONG", "area":u"中國大陸", "areaID":"china"},
	{"location": u"福州", "id": "FUZHOU", "area":u"中國大陸", "areaID":"china"},
	{"location": u"昆明", "id": "KUNMING", "area":u"中國大陸", "areaID":"china"},
	{"location": u"重慶", "id": "CHONGQING", "area":u"中國大陸", "areaID":"china"},
	{"location": u"武漢", "id": "WUHAN", "area":u"中國大陸", "areaID":"china"},
	{"location": u"南昌", "id": "NANCHANG", "area":u"中國大陸", "areaID":"china"},
	{"location": u"杭州", "id": "HANGZHOU", "area":u"中國大陸", "areaID":"china"},
	{"location": u"上海", "id": "SHANGHAI", "area":u"中國大陸", "areaID":"china"},
	{"location": u"南京", "id": "NANJING", "area":u"中國大陸", "areaID":"china"},
	{"location": u"青島", "id": "QINGDAO", "area":u"中國大陸", "areaID":"china"},
	{"location": u"北京", "id": "BEIJING", "area":u"中國大陸", "areaID":"china"},
	{"location": u"開封", "id": "KAIFENG", "area":u"中國大陸", "areaID":"china"},
	{"location": u"西安", "id": "XIAN", "area":u"中國大陸", "areaID":"china"},
	{"location": u"瀋陽", "id": "SHENINAG", "area":u"中國大陸", "areaID":"china"},
	{"location": u"蘭州", "id": "LANZHOU", "area":u"中國大陸", "areaID":"china"},
	{"location": u"海口", "id": "HAIKOU", "area":u"中國大陸", "areaID":"china"}
]

class WeatherGlobal(Forecast):
	def locations(self):
		return WeatherGlobalLocations
	def fetchWithID(self, id):
		locationItem = None
		for item in  self.locations():
			if item['id'] == id:
				locationItem = item
				break
		if locationItem is None:
			return
		
		if locationItem["areaID"] is "asia":
			area = "AA"
		elif locationItem["areaID"] is "america":
			area = "AM"
		elif locationItem["areaID"] is "europe_africa":
			area = "EA"
		elif locationItem["areaID"] is "china":
			area = "CH"
		
		newid = id.capitalize()
		if id == 'LOSANGELES':
			newid = 'Los-angeles'
		if id == 'NEWYORK':
			newid = 'New-york'
		if id == 'JOHANNESBURG':
			newid = 'Johannesburg'

		URLString = WeatherGloabalURL % {"location": newid, "area": area}
		try:
			url = urllib.urlopen(URLString, proxies={})
		except:
			return ""
		lines = url.readlines()

		locationName = locationItem["location"]
		area = locationItem["area"]

		forecastDate = ""
		validDate = ""
		forecast = ""
		temperature = ""
		avgTemperature = ""
		avgRain = ""
		infoline = ""
	
		for line in lines:
			line = line.strip()
			if line.startswith('<li class="smallfield">'):
				infoline = line
				break
	
		infoline = infoline.strip()
		parts = infoline.split('<br />')
		l = 0
		h = 0
		for part in parts:
				part = re.sub(r'<.*?>' , '', part)
				someParts = part.split('：')
				if len(someParts) > 1:
					if someParts[0].endswith('平均最低溫度'):
						try:
							r = re.match('\d+', someParts[1])
							if r is not None:
								l = float(r.group(0))
						except:
							l = 0
							h = 0
					elif someParts[0].endswith('平均最高溫度'):
						try:
							r = re.match('\d+', someParts[1])
							if r is not None:
								h = float(r.group(0))
						except:
							l = 0
							h = 0
					elif someParts[0].endswith('平均降水量'):
						avgRain = someParts[1].strip()
					elif someParts[0].endswith('天氣'):
						forecast = someParts[1].strip()
						try:
							forecast = forecast.decode("ascii")
						except:
							forecast = forecast.decode("utf-8")
					elif someParts[0].endswith('溫度'):
						temperature = someParts[1].replace('℃', '').strip()
				avgTemperature = '%d' % ((l + h) / 2)
		result = {"locationName": locationName, "id": id, "area": area, "forecastDate": forecastDate, "validDate": validDate, "forecast": forecast,  "temperature": temperature, "avgTemperature": avgTemperature, "avgRain": avgRain}
		# for key in result.keys():
		# 	print result[key]
		return result


	def parseData(self, line):
		data  = ""
		line = line.replace("&nbsp;", " ")
		line = line.replace("&deg;", "°")
		hasQuote = False
		for aChar in line:
			if aChar is "<":
				hasQuote = True
			if hasQuote is False:
				data = data + aChar
			if aChar is ">":
				hasQuote = False
		data = data.strip()
		try:
			data = data.decode("ascii")
		except:
			data = data.decode("utf-8")
		return data

	def parseDate(self, dateString):
		date  = ""
		dateString = dateString.replace("&nbsp;", " ")
		hasQuote = False
		for aChar in dateString:
			if aChar is "<":
				hasQuote = True
			if (aChar.isdigit() or aChar.isspace() or aChar is "/" or aChar is "~") and hasQuote is False:
				date = date + aChar
			if aChar is ">":
				hasQuote = False
		date = date.strip()
		try:
			date = date.decode("ascii")
		except:
			date = date.decode("utf-8")
		return date

class TestWeatherGlobal(unittest.TestCase):
	def setUp(self):
		self.model = WeatherGlobal()
	def testForecast(self):
		for item in self.model.locations():
			result = self.model.fetchWithID(item['id'])
			self.assertTrue(result)
			self.assertTrue(result["locationName"])
			self.assertTrue(result["id"])
			# self.assertTrue(result["forecastDate"])
			# self.assertTrue(result["validDate"])
			self.assertTrue(result["forecast"])
			self.assertTrue(result["temperature"])


def main():
	unittest.main()


if __name__ == '__main__':
	main()

