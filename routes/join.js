var express = require('express')
var router = express.Router();
var bodyParser = require('body-parser');
var crypto = require('crypto');
var util = require("util");
var db_config = require('../config/database')();
var conn = db_config.init();

router.use(bodyParser.urlencoded({extended : false}));
router.use(bodyParser.json());

function createHash(password){
	return crypto.createHash('sha512').update(password + 'starstarstar').digest('hex');
}

router.post('/register',function(req, res, next){
	let sql = "insert into user_info values (0,'"+req.body.id+"', '"+createHash(req.body.password)+"')";
	conn.query(sql, function(err, result,fields){
		if(err){
			console.log(err);
			res.send("error");
		}else{
			res.send("ok");
		}
	});
});
router.post('/overlapId',function(req, res, next){
	get_id = req.body.id;
	if(!get_id){
		console.log('overlapId) no id paremeter0');
		res.status(400).send({msg:'no id parameter'});
	}
	else{
	let sql = "select * from user where id = '"+get_id+"'";
	conn.query(sql, function(err, result, fields){
		if(err){
			console.log('overlapId) db error');
			res.status(400).send({msg:'db error'});
		}
		else{
			if(result.length > 0 ){
				console.log("overla[Id) "+get_id+" overlap");
				res.status(409).send({msg:'overlap id'});
			}
			else{
				console.log('overlapId) '+get_id+"no overlap");
				res.status(200).send({msg:'no id overlap'});
			}
		}
	});
	}
});
router.post('/login',function(req,res,next){
	console.log("login) id:"+req.body.id+", password:"+req.body.password);
	if(!req.body.id | !req.body.password){
		res.status(400).send({msg:'no id or password parameter'});
	}
	else{
	
		let sql = "select * from user_info where id = '"+req.body.id+"' AND password = '"+createHash(req.body.password)+"'";
       		// console.log(sql);
        	conn.query(sql, function(err, result,fields){
                	if(err){
                        	res.status(400).send({msg:'db error'});
                	}else{
				if(result.length > 0){
					req.session.user = 
					{
						id:result[0]['id']
					};
					console.log("login) "+util.inspect(req.session.user));		
                        		res.status(200).send({msg:"login ok"});
					}
				else{
					res.status(401).send({msg:'login fail'});
				}
               	 	}
        	});
	}
});

router.get('/logout',function(req,res,next){
	if(req.session.user){
		console.log("logout) "+req.session.user.id);
		delete req.session.user;
		res.status(200).send({msg:"logout ok"});
	}
	else{
		res.status(401).send({msg:"Unauthorized - not login"});
	}
});


module.exports = router;
