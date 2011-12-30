#!/usr/bin/env python
import sys
import time
import datetime
import simplejson
import pymongo
import pymongo.objectid
import pprint
import traceback
import redis
import logging
import pickle
from ui import Todolist

class MyMQ():
	def __init__(self):
		self.rd = redis.Redis()
		self.t = Todolist()

		# setup the logging
		logger = logging.getLogger('todolist_mq')
		logger.setLevel(logging.DEBUG)
		handler = logging.StreamHandler(sys.stdout)
		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		self.logger = logger

	def feed(self):
		try:
			data = self.rd.lpop('todolist-mq')
		except:
			traceback.print_exc()
			self.rd = redis.Redis()
			data = self.rd.lpop('todolist-mq')
		return data

	def pull_mq(self):
		
		data = self.feed()
		if not data:
			# Empty mq
			self.logger.info('Empty mq')
			return False

		try:
			ret = pickle.loads(data)
		except:
			traceback.print_exc()
			return

		self.logger.info(ret)

		self.t.set_user_id(ret['user_id'])

		for act in ret['operations']:
			assert 'projectid' in  act['data']
			if act.get('type') == 'create':
				self.t.create(act['data'])
			elif act.get('type') == 'edit':
				self.t.edit(act['data'])
			elif act.get('type') == 'complete':
				self.t.complete(act['data'])
			elif act.get('type') == 'uncomplete':
				self.t.uncomplete(act['data'])
			elif act.get('type') == 'move':
				self.t.move(act['data'])
			elif act.get('type') == 'delete':
				self.t.delete(act['data'])


	def run(self):
		while True:
			ret = self.pull_mq()
			if not ret: 
				time.sleep(1)

if __name__ == '__main__':
	mq = MyMQ()
	mq.run()
