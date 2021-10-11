var express = require('express')
var router = express.Router();
var bodyParser = require('body-parser');
var util = require("util");
var db_config = require('../config/database')();
var conn = db_config.init();

router.use(bodyParser.urlencoded({extended : false}));
router.use(bodyParser.json());

router.post('/list',function(req, res, next){
	let sql = "select * from bro_info where status = 1";
	conn.query(sql, function(err, result,fields){
		if(err){
			console.log(err);
			res.send("error");
		}else{
           // console.log(result);
			var json = [];
            for(var i =0; i < result.length; i++){
				//console.log(result[i]);
                json.push({"b_id":result[i].b_id, "title":result[i].title, "start_time":result[i].start_time})  
            }
			console.log(json);
			res.end(JSON.stringify(json));
		}
	});
});

router.post('/search',function(req, res, next){
	get_text = req.body.text;
	let sql = "select * from bro_info where status = 1 AND title like '%"+get_text+"%'";
	conn.query(sql, function(err, result,fields){
		if(err){
			console.log(err);
			res.send("error");
		}else{
           // console.log(result);
			var json = [];
            for(var i =0; i < result.length; i++){
				//console.log(result[i]);
                json.push({"b_id":result[i].b_id, "title":result[i].title, "start_time":result[i].start_time})  
            }
			console.log(json);
			res.end(JSON.stringify(json));
		}
	});
});

router.post('/enter',function(req, res, next){
    get_id = req.body.id;
    get_b_id = req.body.b_id;

	if(!get_id || !get_b_id){
		res.status(400).send({msg:'no id or b_id parameter'});
	}

	let sql = "insert into bro_join (b_id, _id) values ("+get_b_id+","+get_id+")";
	conn.query(sql, function(err, result,fields){
		if(err){
			res.send(err);
		}else{
			res.send("ok");
		}
	});
});

router.post('/exit',function(req, res, next){
    get_id = req.body.id;
    get_b_id = req.body.b_id;

	if(!get_id || !get_b_id){
		res.status(400).send({msg:'no id or b_id parameter'});
	}

	let sql = "delete from bro_join where b_id = "+get_b_id+" AND _id = "+get_id+"";
	conn.query(sql, function(err, result,fields){
		if(err){
			res.send(err);
		}else{
			res.send("ok");
		}
	});
});

router.post('/start',function(req, res, next){
    get_id = req.body.id;
    get_title = req.body.title;

	if(!get_id || !get_title){
		res.status(400).send({msg:'no id or title parameter'});
	}

	let sql = "insert into bro_info (b_id, _id, title, start_time, status) values (0, "+get_id+",'"+get_title+"', now(),"+1+")";
	conn.query(sql, function(err, result,fields){
		if(err){
			res.send(err);
		}else{
			res.send("ok");
		}
	});
});

router.post('/stop',function(req, res, next){
    get_b_id = req.body.b_id;

	if(!get_b_id){
		res.status(400).send({msg:'no id or title parameter'});
	}

	let sql = "update bro_info set status=0,end_time=now() where b_id = "+get_b_id+" ";
	conn.query(sql, function(err, result,fields){
		if(err){
			res.send(err);
		}else{
			res.send("ok");
		}
	});
});

module.exports = router;
