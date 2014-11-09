#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################
#                                                                            #
#    This is an example of how to use the SerialAT class                     #
#                                                                            #
#    Python 3.X is not supported yet... :-(                                  #
#    Be sure you are using Python 2.X and have already installed PySerial    #
#    Python 2.X is available on: https://www.python.org/download             #
#    PySerial is available on: https://pypi.python.org/pypi/pyserial         #
#                                                                            #
##############################################################################

# Currently 'import SerialAT' is not supported
from SerialAT import *

if __name__ == '__main__': 
    
# First create a new instance of class SerialAT

    at = SerialAT()
    
# Then initialize the serial port

    at.serialInit('COM1',115200)
    
# Open the serial port

    at.serialOpen()
    
# Then you can send AT commands using SerialAT.AT() method
# This method requires three arguments
# The first string type argument is the AT command to be sent
# The second one is a dict which must include two keys: 'res' and 'end' 
# If you expect a response string like '+CREG:', you can put it as the value field
# of key 'res', the parameters after it will be automatically analyzed as long as
# they are received, or you can set it to None
# The value of key 'end' shall be a tuple, including all possible result strings
# of the command, it can also be set to None
# The third argument is the wait time in seconds

    result = at.AT('AT+CREG?',{'end':('OK','ERROR'),'res':'+CREG:'},0.200)
    
# AT() returns a dict
# 'suc' - succeeded to receive the response and result strings
# 'arg' - a list of strings : the parameters found from response string
# 'end' - the received result string
    
    if True == result['suc'] :
        print 'Succeeded to receive all expected strings'
    if False == result['suc'] :
        print 'Failed to reveive all expected strings'
        at.serialClose()
        exit()
    
    if 2 == len(result['arg']) :
        if 0 == cmp('1',result['arg'][1]) :
            print 'The network has been already registered'
        else :
            print 'The network has not been registered'

    if 0 == cmp('OK',result['end']) :
        print 'The result is OK'

# Reset the serial port   
    at.serialReset()
    
# Or close the serial port
    at.serialClose()

