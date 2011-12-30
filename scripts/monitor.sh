#!/bin/sh

export PATH=$PATH:/opt/mongodb-1.8.1/bin:/opt/mongodb-1.8.2/bin
ui_root=$(dirname $(dirname $0))
ui_log=/tmp/todolist.log
ui_port=8080

ps aux|grep [n]ginx -q || {
	#sudo /etc/init.d/nginx start
	ui_port=9527
}



ps aux|grep [m]ongod -q || {
		[ -f /opt/todo-db/mongod.lock ] && rm -f /opt/todo-db/mongod.lock
		mongod --fork --dbpath=/opt/todo-db --logpath /var/log/mongod.log --logappend
}

ps aux|grep [r]edis-server -q || {
	echo 'daemonize yes' | redis-server -
}

ps aux|grep [w]orker.py -q || {
	python $ui_root/worker.py >/tmp/worker.log 2>&1 &
}

[ $ui_port = 9527 ] && {
	cd $ui_root && python ui.py 9527
} || {
	cd $ui_root && \
		python ui.py $ui_port fcgi >$ui_log  2>&1 &
}
