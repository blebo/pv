#!/usr/bin/env python
"""
License: The MIT License (MIT)

Copyright (c) 2010 Edmund Tse

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import sys
from __init__ import *

if len(sys.argv) != 2:
	print "Fetches data from the inverter device via RS-232"
	print "Usage: %s <port>" % sys.argv[0]
	sys.exit(1)

print "Connecting to inverter..."
inv = Inverter()

try:
	inv.connect(sys.argv[1])
except serial.SerialException as e:
	print "Unable to connect to serial port %s:" % sys.argv[1], e
	sys.exit(1)

inv.reset()
inv.reset()
inv.reset()

sn = inv.discover()
if sn is None:
	print "Inverter is offline."
	sys.exit(1)

if not inv.register(sn):
	print "Inverter did not respond to select."
	sys.exit(1)

param_layout = inv.param_layout()
if param_layout is None:
	print "Cannot get inverter's parameters layout"
else:
	parameters = inv.parameters(param_layout)
	if parameters is not None:
		print "Inverter %s parameters:" % sn
		for field in parameters:
			print "%-10s: %s" % field


status_layout = inv.status_layout()
if status_layout is None:
	print "Cannot get inverter's status layout"
	sys.exit(1)

status = inv.status(status_layout)
if status is None:
	print "Error getting inverter status."
	sys.exit(1)

print "Inverter %s status:" % sn
for field in status:
	print "%-10s: %s" % field
