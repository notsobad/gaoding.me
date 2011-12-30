

var show_users = function(){ db.users.find().forEach(function(i){print(i.nick_name + '\t' + i.last_login); }); };
var show_jobs = function(u){ 
	var user = db.users.findOne({nick_name:u});
	if(!u){
		print('Not valid username');
		return false;
	}
	db.jobs.find({user_id: user._id }).forEach(function(i){
		print(i.nm);
	});
};

