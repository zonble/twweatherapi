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
from flask import Flask, request, make_response, Markup
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
cache = SimpleCache()

@app.route('/')
def hello():
	return 'Hello World!'

def _output(cachedData, request):
	outputtype = request.args.get('output', '')
	if outputtype == 'json':
		jsonText = json.dumps({"result":cachedData})
		response = make_response(jsonText)
		response.headers['Content-Type'] = 'text/plain; charset=utf-8'
		return response
	else:
		pl = dict(result=cachedData)
		output = plistlib.writePlistToString(pl)
		response = make_response(output)
		response.headers['Content-Type'] = 'text/plist; charset=utf-8'
		return response

def getData(modelInstance, cache_key, request, fetchMethodName='fetch', fetchParameter=''):
	cachedData = cache.get(cache_key)
	if cachedData is None:
		cmd = 'modelInstance.%(methodName)s(%(fetchParameter)s)' %  {'methodName': fetchMethodName, 'fetchParameter': fetchParameter}
		app.logger.debug(cmd)
		result = eval(cmd)
		if result is not None:
			cachedData = result
			cache.set(cache_key, cachedData, timeout=60 * 60)
	if cachedData is None:
		return ""
	return cachedData

def getAllData(model, cache_key_prefix, request, fetchMethodName='fetch', fetchItemsName='', fetchItemKey='id'):
	cache_key = cache_key_prefix + '_all'
	cachedData = cache.get(cache_key)
	modelInstance = model()
	if cachedData is None:
		results = []
		items = eval('modelInstance.' + fetchItemsName)
		for item in items:
			item_id = item[fetchItemKey]
			item_cache_key = cache_key_prefix + '_' + str(item_id)
			result = getData(modelInstance, item_cache_key, request, fetchMethodName, item_id)
			results.append(result)
		if len(results):
			cachedData = results
			cache.set(cache_key, cachedData, timeout=60 * 60)
	return _output(cachedData, request)

def getSingleData(model, cache_key, request, fetchMethodName='fetch', fetchParameter=''):
	cachedData = getData(model(), cache_key, request, fetchMethodName, fetchParameter)
	return _output(cachedData, request)

@app.route('/warning', methods=['GET'])
def warning():
	print request
	return getSingleData(weather.WeatherWarning, 'warnings', request)

@app.route('/overview', methods=['GET'])
def overviow():
	text = cache.get('overview')
	if text is None:
		overview = weather.WeatherOverview()
		overview.fetch()
		text = overview.plain
		cache.set('overview', text, timeout=60 * 60)
	return text

@app.route('/forecast', methods=['GET'])
def forecast():
	location = request.args.get('location', '')
	if not len(location):
		return None
	elif location == 'all':
		return getAllData(weather.WeatherForecast, 'forecast_', request, 'fetchWithID', 'locations()', 'id')
	else:
		return getSingleData(weather.WeatherForecast, 'forecast_' + location, request, 'fetchWithID', location)
	

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
