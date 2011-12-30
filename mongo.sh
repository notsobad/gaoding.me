
export PATH=$PATH:/opt/mongodb-1.8.1/bin:/opt/mongodb-1.8.2/bin

mongod --fork --dbpath=/opt/todo-db --logpath /var/log/mongod.log --logappend
