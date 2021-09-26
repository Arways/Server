var logger = require('morgan');
var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var session = require('express-session');
var cookieParser =require('cookie-parser');

var joinRouter = require('./routes/join');

app.use(bodyParser.urlencoded({extended: false}));
app.use(logger('dev'));

app.use(cookieParser());
app.use(session({
	secret: 'secret',
	resave: true,
	saveUninitialized: true
}));

app.use('/join',joinRouter);

app.listen(3000);
