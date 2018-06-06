#!/bin/bash

/usr/bin/nohup /usr/bin/python2.7 -u monitor.py > monitor.log 2>1& & echo $! > monitor.pid