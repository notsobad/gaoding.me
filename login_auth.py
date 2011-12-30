#! /usr/bin/python
# -*- coding: utf-8 -*-

from urllib import quote, urlencode
import urllib2
import time
import uuid
import hmac, hashlib


APP_KEY = '1021057754' 
APP_SECRET = '1f88d9f5c022fd118f9e4daeaae2473e'

def get_weibo_token():
	URL = 'http://api.t.sina.com.cn/oauth/request_token'

	params = [
		('oauth_consumer_key', APP_KEY),
		('oauth_nonce', uuid.uuid4().hex),
		('oauth_signature_method', 'HMAC-SHA1'),
		('oauth_timestamp', int(time.time())),
		('oauth_version', '1.0'),
	]

	params.sort()

	p = 'GET&%s&%s' % (quote(URL, safe=''), quote(urlencode(params)))
	signature = hmac.new(APP_SECRET + '&', p, hashlib.sha1).digest().encode('base64').rstrip()

	params.append(('oauth_signature', quote(signature)))

	h = ', '.join(['%s="%s"' % (k, v) for (k, v) in params])

	r = urllib2.Request(URL, headers={'Authorization': 'OAuth realm="", %s' % h})

	data = urllib2.urlopen(r).read()
	token, secret = [pair.split('=')[1] for pair in data.split('&')]

	return token, secret

def get_weibo_info(token, secret):
	URI = 'http://api.t.sina.com.cn/account/verify_credentials.json'


	headers = [
		('oauth_consumer_key', APP_KEY),
		('oauth_nonce', uuid.uuid4().hex),
		('oauth_signature_method', 'HMAC-SHA1'),
		('oauth_timestamp', int(time.time())),
		('oauth_version', '1.0'),
		('oauth_token', token)
	]

	headers.sort()

	p = 'POST&%s&%s' % (quote(URI, safe=''), quote(urlencode(headers)))
	signature = hmac.new(APP_SECRET + '&' + secret, p, hashlib.sha1).digest().encode('base64').rstrip()

	headers.append(('oauth_signature', quote(signature)))

	h = ', '.join(['%s="%s"' % (k, v) for (k, v) in headers])

	r = urllib2.Request(URI, data='', headers={'Authorization': 'OAuth realm="", %s' % h})

	data = urllib2.urlopen(r).read()
	return data

def get_weibo_access_token(token, secret, verifier):
	URI = 'http://api.t.sina.com.cn/oauth/access_token'

	headers = [
		('oauth_consumer_key', APP_KEY),
		('oauth_nonce', uuid.uuid4().hex),
		('oauth_signature_method', 'HMAC-SHA1'),
		('oauth_timestamp', int(time.time())),
		('oauth_version', '1.0'),
		('oauth_token', token),
		('oauth_verifier', verifier),
		('oauth_token_secret', secret),
	]

	headers.sort()

	p = 'POST&%s&%s' % (quote(URI, safe=''), quote(urlencode(headers)))
	signature = hmac.new(APP_SECRET + '&' + secret, p, hashlib.sha1).digest().encode('base64').rstrip()

	headers.append(('oauth_signature', quote(signature)))

	h = ', '.join(['%s="%s"' % (k, v) for (k, v) in headers])

	r = urllib2.Request(URI, headers={'Authorization': 'OAuth realm="", %s' % h})

	data = urllib2.urlopen(r, data='').read()
	token, secret, user_id = [pair.split('=')[1] for pair in data.split('&')]

	return token, secret, user_id


if __name__ == '__main__':
	token, secret = get_weibo_token()
	
	print token, secret
	#print get_weibo_info(token, secret)
