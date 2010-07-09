"""
pv exposes a simple API to interface with some photovoltaic DC inverters via
RS-232.

pv was developed specifically for the Carbon Management Solutions CMS-2000
inverter, and is expected to work for the Solar Energy Australia Orion inverter
since they are essentially the same device with a different badge.

The communication protocol was based on examining the data exchange between
the inverter device and the official Pro Control 2.0.0.0 monitoring software
for the Orion inverter.


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
__author__ = 'Edmund Tse <tseedmund@gmail.com>'
__version__ = '0.1'
__all__ = ['Frame', 'Device', 'Inverter']
__date__ = '9 Jul 10'


from pv import Frame, Device, Inverter
