#!/usr/bin/python
#coding=utf-8
import web
import pdb, traceback
import pymongo
import pymongo.objectid
import copy
import pprint
import simplejson
import time
import datetime
import login_auth
import os
import pickle
import redis
from jinja2 import Environment,FileSystemLoader

def render_template(template_name, **context):
	extensions = context.pop('extensions', [])
	globals = context.pop('globals', {})

	jinja_env = Environment(
			loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
			extensions=extensions,
			)
	jinja_env.globals.update(globals)

	#jinja_env.update_template_context(context)

	return jinja_env.get_template(template_name).render(context)

urls = (
		'/', 'index',
		'/login/?', 'login',
		'/accounts/login/?', 'login',
		'/accounts/logout/?', 'logout',
		'/run_operations/?', "run_operations",
		'/poll_remote_operations/?', "poll_remote_operations"
	)
web.config.debug = False
app = web.application(urls, globals())


if web.config.get('_session') is None:
	session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'secret':''})
	web.config._session = session
else:
	session = web.config._session

render = web.template.render('.')


class Todolist:
	def __init__(self, user_id=None):
		if user_id:
			self.set_user_id(user_id)

		mongo = pymongo.Connection('localhost', 27017)
		self.jobs = mongo.todolist.jobs
	
	def set_user_id(self, user_id):
		self.user_id = pymongo.objectid.ObjectId( user_id )

	def fetch(self):
		cond = {'user_id' : self.user_id}
		_all_jobs = self.jobs.find(cond).sort("priority")
		all_jobs = []
		for j in _all_jobs:
			del j['_id']
			del j['user_id']
			all_jobs.append(j)

		#all_jobs = [j for j in _all_jobs]
		root_jobs = [j for j in all_jobs if j['parentid'] == '']
		child_jobs = [j for j in all_jobs if j['parentid'] != '']
		
		tree = root_jobs

		# TODO
		def __get_children(job):
			ret = []
			if len(child_jobs) < 1:
				return ret
			
			# bug here
			for i in range(len(child_jobs) - 1, -1, -1):
				child = child_jobs[i]
				if child['parentid'] == job['id']:
					del child_jobs[i]
					#del child['parentid']
					chs = get_children(child)
					if chs:
						child['ch'] = chs
					ret.append(child)
			return ret


		def get_children(job):
			ret = []
			for child in child_jobs:
				if child['parentid'] == job['id']:
					#del child['parentid']
					chs = get_children(child)
					if chs:
						child['ch'] = chs
					ret.append(child)
			return ret

		for i,job in enumerate(root_jobs):
			children = get_children(job)
			if children:
				root_jobs[i]['ch'] = children
	
		#pprint.pprint( root_jobs )
		return root_jobs


	def create(self, act):

		projectid = act.get('projectid')
		
		parentid = act.get('parentid')
		if parentid == None or parentid == 'None':
			parentid = ''

		priority = int( act.get('priority', 0) )
		obj = {'cp':False, 'id':projectid, 'nm':'', 'parentid':'', 'priority': priority, 'last_move':int(time.time()), 'parentid' : parentid, 'user_id' : self.user_id}
		self.jobs.save(obj)

		# Need to resort.
		self._resort(parentid)

	def edit(self, act):
		data = {}
		projectid = act.get('projectid', '')
		nm = act.get('name')
		no = act.get('description')
		if nm is not None:
			data['nm'] = nm

		if no is not None:
			data['no'] = no 

		cond = {'user_id' : self.user_id, 'id':projectid}
		self.jobs.update(cond, {'$set':data})

	def complete(self, act):
		projectid = act.get('projectid')

		cond = {'user_id' : self.user_id, 'id':projectid}
		self.jobs.update(cond, {'$set':{'cp':True}})

	def uncomplete(self, act):
		projectid = act.get('projectid')
		cond = {'user_id' : self.user_id, 'id':projectid}
		self.jobs.update(cond, {'$set':{'cp':False}})
		
	def delete(self, act):
		projectid = act.get('projectid')
		self.jobs.remove({'user_id' : self.user_id, 'id':projectid})
		self.jobs.remove({'user_id' : self.user_id, 'parentid':projectid})

	def _resort(self, parentid):
		jobs = self.jobs.find({'parentid':parentid, 'user_id' : self.user_id}).sort([('priority',pymongo.ASCENDING), ('last_move', pymongo.DESCENDING)])

		for i,job in enumerate(jobs):
			job['priority'] = i
			self.jobs.save(job)

	def move(self, act):
		data = {}
		projectid = act.get('projectid')
		parentid = act.get('parentid')
		if parentid == 'None':
			parentid = ''
		data['parentid'] = parentid

		priority = act.get('priority')
		if priority != None:
			data['priority']  = int(priority)
			data['last_move'] = int(time.time())

		self.jobs.update({'id':projectid, 'user_id' : self.user_id}, {'$set':data})

		# resort it by priority
		self._resort(parentid)



class User:
	def __init__(self):
		mongo = pymongo.Connection('localhost', 27017)
		self.user = mongo.todolist.users
	
	def login(self,user_source, user_info):
		user_id = user_info.get('id')
		cond =  {'from':user_source, 'identify': user_id}
		u  = self.user.find_one(cond)
		if not u:
			cond['last_login'] = datetime.datetime.now()
			cond['extra'] = str( user_info )
			cond['nick_name'] = user_info['name']
			cond['last_login'] = datetime.datetime.now()
			_id = self.user.save(cond)
		else:
			u['last_login'] = datetime.datetime.now()
			_id = self.user.save(u)
		session.user_id = str(_id)
		return True
	
	def get_info(self):
		user_id = pymongo.objectid.ObjectId( session.get('user_id', '4dfc68590cc1750e36000000') )
		u = self.user.find_one({'_id': user_id })
		u['last_login'] = str(u['last_login'])[:-7]
		return u


class myStaticMiddleware(web.httpserver.StaticMiddleware):
    """WSGI middleware for serving static files."""
    def __init__(self, app, prefix='/media/'):
		web.httpserver.StaticMiddleware.__init__(self, app, "/media/")


class index:
	def GET(self):
		user_id = session.get('user_id')
		if not user_id:
			return render_template('index.html')
			#raise web.seeother('/login')

		t = Todolist(user_id)
		tree = t.fetch()
		u = User()
		json = simplejson.dumps(tree)
		return render_template('main.html', json=json, user_info=u.get_info())

class run_operations():
	
	def POST(self):
		r = redis.Redis()
		try:
			ret = {
				'operations' : simplejson.loads( web.input().get('operations') ),
				'user_id' : session.get('user_id'),
			}
			data = pickle.dumps(ret)
			#print  "orig: ", ret
			#print "loads: ", pickle.loads(data)
			r.rpush('todolist-mq', data)
			#data = r.lpop('todolist-mq')
			#print "loads: ", pickle.loads(data)
		except:
			traceback.print_exc()
			return 'Error args'

		return '{"error_encountered": false, "new_most_recent_operation_transaction_id": "4334041", "new_polling_interval_in_ms": 30000, "concurrent_remote_operation_transactions": [], "error_encountered_in_remote_operations": false}'

class poll_remote_operations():
	def POST(self):
		return '{"new_most_recent_operation_transaction_id": "4334041", "new_polling_interval_in_ms": 3000000, "concurrent_remote_operation_transactions": [], "error_encountered_in_remote_operations": false}'

class qq_auth():
	def GET(self):
		return '00111010000000111110101011777036521'

class logout():
	def GET(self):
		session.kill()
		raise web.seeother('/')

class login():
	def GET(self):
		login_error = '登录失败，可能是服务器与新浪oauth服务交互出现问题，请稍候重试，<a href="/">返回</a>'

		i = web.input()
		if i.get('act') == 'auth':
			try:
				token, secret = login_auth.get_weibo_token()
			except:
				web.header('Content-Type', 'text/html; charset=utf-8')
				traceback.print_exc()
				return login_error
			session.token = token
			session.secret = secret
			if web.ctx.env['SERVER_PORT'] == '9527':
				oauth_callback = web.urlquote('http://localhost:9527/login?act=callback')
			else:
				oauth_callback = web.urlquote('http://gaoding.me/login?act=callback')

			raise web.seeother('http://api.t.sina.com.cn/oauth/authorize?oauth_token=%(token)s&oauth_callback=%(oauth_callback)s' % locals())
		elif i.get('act') == 'callback':
			'''
			http://localhost:8080/login?act=callback&oauth_token=e43e721b87c0b1c5fc9ad0746fcd1c0f&oauth_verifier=186264
			'''
			token = i.get('oauth_token')
			secret = session.get('secret')
			oauth_verifier = i.get('oauth_verifier')
			
			try:
				token, secret, user_id = login_auth.get_weibo_access_token(token, secret, oauth_verifier)
				user_info = login_auth.get_weibo_info(token, secret)
			except:
				traceback.print_exc()
				web.header('Content-Type', 'text/html; charset=utf-8')
				return login_error

			user_info = simplejson.loads(user_info)
			
			user = User()
			user.login('weibo', user_info)

			raise web.seeother('/')

		return 'Access denied'

if __name__ == '__main__':
	app.run(myStaticMiddleware)
