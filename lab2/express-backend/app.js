const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const indexRouter = require('./routes');
const usersRouter = require('./routes/users');
const apiRouter = require('./routes/api');
const loadEnv = require('./config/loadEnv');
const connectDB = require('./config/database');
const cors = require('cors');
const app = express();

loadEnv();
connectDB();

app.use(cors());
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/api', apiRouter);

module.exports = app;
