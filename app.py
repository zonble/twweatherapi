#!/usr/bin/env python
# encoding: utf-8

"""

Copyright (c) 2009-2010 Weizhong Yang (http://zonble.net)

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

import os
import weather
import plistlib, json
from flask import *
from werkzeug.contrib.cache import SimpleCache
from flaskext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.name = u"台灣天氣 API Server"
app.config.from_pyfile(os.path.join(app.root_path, 'config.py'))
app.pages = [
	{'function_name':u'overview', 'title':u'關心天氣'},
	{'function_name':u'forecast', 'title':u'48 小時天氣預報'},
	{'function_name':u'week', 'title':u'一週天氣'},
	{'function_name':u'week_travel', 'title':u'一週旅遊'},
	{'function_name':u'three_day_sea', 'title':u'三天海上預報'},
	{'function_name':u'nearsea', 'title':u'近海預報'},
	{'function_name':u'tide', 'title':u'潮汐預報'},
	{'function_name':u'obs', 'title':u'觀測站資料'},
	{'function_name':u'global_forecasts', 'title':u'全球天氣'},
	{'function_name':u'image', 'title':u'天氣雲圖'}
	]
db = SQLAlchemy(app)
db_session = db.session

cache = SimpleCache()
DEFAULT_CACHE_TIMEOUT = 30 * 60

class Device(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	device_id = db.Column(db.String(255), unique=True, nullable=False)
	device_name = db.Column(db.String(255))
	device_model = db.Column(db.String(40))
	app_name = db.Column(db.String(40))
	app_version = db.Column(db.String(40))
	os_name = db.Column(db.String(40))
	os_version = db.Column(db.String(40))
	access_date = db.Column(db.DateTime)
	note = db.Column(db.String(255))

def add_record(request):
	device_id = request.args.get('device_id', '')
	if not len(str(device_id)):
		return
	
	current_device = Device.query.filter_by(device_id=device_id).first()
	app.logger.debug(current_device)
	if not current_device:
		current_device = Device()
		current_device.device_id = device_id
		db_session.add(current_device)

	device_name = request.args.get('device_name', '')
	current_device.device_name = device_name if device_name else ""
	device_model = request.args.get('device_model', '')
	current_device.device_model = device_model if device_name else ""
	app_name = request.args.get('app_name', '')
	current_device.app_name = app_name if app_name else ""
	app_version = request.args.get('app_version', '')
	current_device.app_version = app_version if app_version else ""
	os_name = request.args.get('os_name', '')
	current_device.os_name = os_name if os_name else ""
	os_version = request.args.get('os_version', '')
	current_device.os_version = os_version if os_version else ""
	note = request.args.get('note', '')
	current_device.note = note if note else ""
	current_device.access_date = datetime.now()

	db_session.commit()

def _output(cachedData, request):
	outputtype = request.args.get('output', '')
	if outputtype == 'json':
		jsonText = json.dumps({"result":cachedData})
		response = make_response(jsonText)
		response.headers['Content-Type'] = 'application/json; charset=utf-8'
		return response
	else:
		pl = dict(result=cachedData)
		output = plistlib.writePlistToString(pl)
		response = make_response(output)
		response.headers['Content-Type'] = 'text/plist; charset=utf-8'
		return response

def getData(modelInstance, cache_key, request, fetchMethodName='fetchWithID', fetchParameter=None):
	cachedData = cache.get(cache_key)
	if cachedData is None:
		if fetchParameter is None:
			cmd = 'modelInstance.%(methodName)s()' %  {'methodName': fetchMethodName}
		else:
			cmd = 'modelInstance.%(methodName)s("%(fetchParameter)s")' %  {'methodName': fetchMethodName, 'fetchParameter': fetchParameter}
		result = eval(cmd)
		if result is not None:
			cachedData = result
			cache.set(cache_key, cachedData, timeout=DEFAULT_CACHE_TIMEOUT)
	if cachedData is None:
		return ""
	return cachedData

def getAllData(model, cache_key_prefix, request, fetchMethodName='fetchWithID', fetchItemsName='locations()', fetchItemKey='id'):
	cache_key = cache_key_prefix + '_all'
	cachedData = cache.get(cache_key)
	modelInstance = model()
	if cachedData is None:
		results = []
		items = eval('modelInstance.' + fetchItemsName)
		for item in items:
			item_id = item[fetchItemKey]
			item_cache_key = cache_key_prefix + '_' + str(item_id)
			result = getData(modelInstance, item_cache_key, request, fetchMethodName, str(item_id))
			results.append(result)
		if len(results):
			cachedData = results
			cache.set(cache_key, cachedData, timeout=DEFAULT_CACHE_TIMEOUT)
	return _output(cachedData, request)

def getSingleData(model, cache_key, request, fetchMethodName='fetchWithID', fetchParameter=None):
	cachedData = getData(model(), cache_key, request, fetchMethodName, fetchParameter)
	return _output(cachedData, request)

def getIndexPage(model, function_name, request, fetchItemsName='locations()'):
	cache_key = function_name + '_page'
	cache_title_key = function_name + '_title'
	cachedData = cache.get(cache_key)
	cachedTitle = cache.get(cache_title_key)
	if cachedData is None:
		title = ""
		for page in app.pages:
			if page['function_name'] == function_name:
				title = page['title']
				break

		modelInstance = model()
		result = eval('modelInstance.' + fetchItemsName)
		items = [{'location':u'全部地點', 'id':'all'}]
		items.extend(result)
		text = u'<h2>' + title + u'</h2>'
		text += u'<table>\n'
		text += u'<tr><th>地點</th><th colspan="2">輸出格式</th></tr>'
		for item in items:
			text += '<tr>'
			text += '<td>' + item['location'] + '</td>'
			text += u'<td class="data_link"><a title="以 Plist 格式輸出" href="' + url_for(function_name, location=item['id']) + '">Plist</a></td>'
			text += u'<td class="data_link"><a title="以 JSON 格式輸出" href="' + url_for(function_name, location=item['id'], output='json') + '">JSON</a></td>'
			text += '</tr>\n'
		text += '</table>\n'
		cachedData = text
		cachedTitle = title
		cache.set(cache_key, cachedData, timeout=DEFAULT_CACHE_TIMEOUT)
		cache.set(cache_title_key, cachedTitle, timeout=DEFAULT_CACHE_TIMEOUT)
	return render_template('index.html', app=app, text=Markup(cachedData), title=cachedTitle, side=Markup(sidebar()))

@app.route('/test', methods=['GET'])
def test():
	return str(Device.query)

@app.route('/warning', methods=['GET'])
def warning():
	return getSingleData(weather.WeatherWarning, 'warnings', request, 'fetch')

@app.route('/overview', methods=['GET'])
def overview():
	text = cache.get('overview')
	if text is None:
		overview = weather.WeatherOverview()
		overview.fetch()
		text = overview.plain
		cache.set('overview', text, timeout=DEFAULT_CACHE_TIMEOUT)
	return text

def handleRequest(model, function_name, request):
	add_record(request)
	location = request.args.get('location', '')
	cache_key_prefix = function_name + '_'
	if location == 'all' or location is u'all':
		return getAllData(model, cache_key_prefix, request)
	elif not len(location):
		return getIndexPage(model, function_name, request)
	else:
		return getSingleData(model, cache_key_prefix + location, request, 'fetchWithID', location)

@app.route('/forecast', methods=['GET'])
def forecast():
	return handleRequest(weather.WeatherForecast, 'forecast', request)

@app.route('/week', methods=['GET'])
def week():
	return handleRequest(weather.WeatherWeek, 'week', request)

@app.route('/week_travel', methods=['GET'])
def week_travel():
	return handleRequest(weather.WeatherWeekTravel, 'week_travel', request)

@app.route('/3sea', methods=['GET'])
def three_day_sea():
	return handleRequest(weather.Weather3DaySea, 'three_day_sea', request)

@app.route('/nearsea', methods=['GET'])
def nearsea():
	return handleRequest(weather.WeatherNearSea, 'nearsea', request)

@app.route('/tide', methods=['GET'])
def tide():
	return handleRequest(weather.WeatherTide, 'tide', request)

@app.route('/obs', methods=['GET'])
def obs():
	return handleRequest(weather.WeatherOBS, 'obs', request)

@app.route('/global', methods=['GET'])
def global_forecasts():
	return handleRequest(weather.WeatherGlobal, 'global_forecasts', request)

@app.route('/image', methods=['GET'])
def image():
	imageID = str(request.args.get('id', ''))
	if not len(imageID):
		text = u'<table>'
		text += u'<tr><th>代號</th><th colspan="2">圖片</th></tr>'
		for item in weather.WeatherImageURL:
			line = u'<tr>' 
			line += '<td>' + item['id'] + '</td>'
			line += '<td><a href="' + url_for('image', id=item['id']) + '">Cached Image</a></td>'
			line += '<td><a href="' + item["URL"] + '">Original Image</a></td>'
			line += '</tr>'
			text += line
		text += '</table>'
		return render_template('index.html', app=app, text=Markup(text), title=u'天氣雲圖', side=Markup(sidebar()))
		return None

	URL = None
	for item in weather.WeatherImageURL:
		if str(imageID) == str(item['id']):
			URL = item["URL"]
	if URL is None:
		abort(404)
		return

	should_redirect = request.args.get('redirect', '')
	if should_redirect is not None:
		redirect(URL)

	cache_key = 'image_' + imageID
	cachedData = cache.get(cache_key)
	if not cachedData:
		import urllib
		url = urllib.urlopen(URL, proxies={})
		imageData = url.read()
		if imageData is None:
			return redirect(URL)
		cachedData = imageData
		cache.set(cache_key, cachedData, timeout=DEFAULT_CACHE_TIMEOUT)
	response = make_response(cachedData)
	response.headers['Content-Type'] = 'image/jpeg'
	return response


def sidebar():
	text = u'<ul>'
	text += u'<li>重要天氣警告 <a href="' + url_for('warning') + \
		u'">Plist</a> <a href="' + url_for('warning', output='json') + \
		u'">JSON</a></li>'
	for page in app.pages:
		text += u'<li><a title="' + page['title'] + '" href="' + \
			url_for(page['function_name']) + '">' + page['title'] + u'</a></li>'
	text += u'</ul>'
	return text

@app.route('/')
def hello():
	text = sidebar()
	return render_template('index.html', app=app, text=Markup(text))

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
