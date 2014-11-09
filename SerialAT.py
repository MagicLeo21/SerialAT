#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#                      Copyright (C) 2014 Chen Yan                           #
#                     Licensed under the MIT license                         #
#                                                                            #
#                         The MIT License (MIT)                              #
#                                                                            #
# Permission is hereby granted, free of charge, to any person obtaining a    #
# copy of this software and associated documentation files (the “Software”), #
# to deal in the Software without restriction, including without limitation  #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,   #
# and/or sell copies of the Software, and to permit persons to whom the      #
# Software is furnished to do so, subject to the following conditions:       #
#                                                                            #
# The above copyright notice and this permission notice shall be included in #
# all copies or substantial portions of the Software.                        #
#                                                                            #
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    #
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        #
# DEALINGS IN THE SOFTWARE.                                                  #
#                                                                            #
##############################################################################

import time
import serial

from shlex import shlex
from threading import Thread
from Queue import Queue

class _RecvThread (Thread) :

    __flg = None
    __ser = None
    __que = None

    def __init__ (self, port, queue) :
        Thread.__init__(self)
        self.__flg = False
        self.__ser = port
        self.__que = queue

    def stop (self) :
        self.__flg = False

    def run (self) :
        self.__flg = True
        while self.__flg :
            recv = self.__ser.readline(None)
            recv = recv.strip('\r \n')
            if 0 != len(recv) :
                print recv
                if 500 > self.__que.qsize() :
                    self.__que.put(recv)
            time.sleep(0.010)

class SerialAT () :

    __ser  = None
    __que  = None
    __rcvr = None

    def __init__ (self) :
        self.__ser  = serial.Serial()
        self.__que  = Queue()

    def serialInit (self,port,baud) :
        self.__ser.port         = port
        self.__ser.baudrate     = baud
        self.__ser.bytesize     = serial.EIGHTBITS
        self.__ser.parity       = serial.PARITY_NONE
        self.__ser.stopbits     = serial.STOPBITS_ONE
        self.__ser.timeout      = 0.100
        self.__ser.xonxoff      = False
        self.__ser.rtscts       = False
        self.__ser.dsrdtr       = False
        self.__ser.writeTimeout = 0.100
        return True

    def serialOpen (self) :
        if False == self.__ser.isOpen() :
            self.__ser.open()
        if False == self.__ser.isOpen() :
            return False
        else :
            self.__ser.flushInput()
            self.__ser.flushOutput()
            if None == self.__rcvr or not self.__rcvr.isAlive() :
                self.__rcvr = _RecvThread(self.__ser,self.__que)
                self.__rcvr.start()
            return True

    def serialClose (self) :
        if self.__ser.isOpen() :
            if self.__rcvr.isAlive() :
                self.__rcvr.stop()
                self.__rcvr.join()
            self.__ser.close()
        return True

    def serialReset (self) :
        if self.__ser.isOpen() :
            self.serialClose()
            self.serialOpen()
        return True

    def serialSetDtr (level) :
        if self.__ser.isOpen() :
            self.__ser.setDTR(level)
            return True
        return False

    def serialSetRts (level) :
        if self.__ser.isOpen() :
            self.__ser.setRTS(level)
            return True
        return False

    def __cmdSplit (self,cmd) :
        if ':' in cmd :
            pos = cmd.index(':') + 1
            lex = shlex(cmd[pos:].strip('\r \n'))
            lex.quotes = '"'
            lex.whitespace=','
            lex.whitesapce_split=True
            return list(lex)
        return None

    def __cmdSend (self,cmd) :
        if self.__ser.isOpen() :
            if None != cmd and len(cmd) :
                if not '\n' == cmd[-1] :
                    cmd = cmd + '\n'
                self.__ser.write(cmd)
            return True
        return False

    def __cmdRecv (self,set) :
        dict = {'suc':False,'end':None,'arg':None}
        tmpflg = False
        if None == set['res'] :
            tmpflg = True
        while 0 < self.__que.qsize() :
            recv = self.__que.get()
            if None != set['end'] :
                for end in set['end'] :
                    tmplen = len(end)
                    if 0 == cmp(recv[0:tmplen],end[0:tmplen]) :
                        dict['end'] = recv
                        if True == tmpflg :
                            dict['suc'] = True
                        return dict
            if None != set['res'] :
                tmplen = len(set['res'])
                if 0 == cmp(set['res'][0:tmplen],recv[0:tmplen]) :
                    dict['arg'] = self.__cmdSplit(recv)
                    if None == set['end'] :
                        dict['suc'] = True
                        return dict
                    tmpflg = True
                    continue
        return dict

    def AT (self,cmd,set,delay) :
        if self.__cmdSend(cmd) :
            time.sleep(delay)
        return self.__cmdRecv(set)

