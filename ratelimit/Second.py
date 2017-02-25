#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author:hidu
"""
import time
import threading

class RateLimitSecond(object):
    '''
    限制每秒qps速度
    '''
    def __init__(self,limit):
        '''
        init
        '''
        self.each_sec = 1.0 / limit
        self.limit = limit
        self.last_task = 0
        self.mutex = threading.Lock()
        self.start_time = time.time()
        self.req_total = 0

    def wait(self):
        '''
        等等获得继续运行资格
        '''
        while True:
            _sleep = self._try()
            if _sleep <= 0:
                break
            else:
                time.sleep(_sleep)
        self.req_total += 1

    def qps_info(self):
        '''
        获取速度信息
        '''
        _used = time.time() - self.start_time
        return {
            'req_total' : self.req_total,
            'qps' : '%.2f' % (self.req_total/_used),
            'used' : '%.2f' % _used,
        }
    
    def _try(self):
        '''
        判断是否可以继续运行，返回需要等待的时间
        '''
        self.mutex.acquire()
        now = time.time()
        sleep = 0
        if self.last_task < 1:
            self.last_task = now
        else:
            _time_fix = 0
            if self.req_total > 0:
                _qps = self.req_total/ (time.time() - self.start_time)
                _time_fix = 1.0/_qps - self.each_sec
                
            sleep = self.each_sec -(now - self.last_task) - _time_fix*10
            if sleep <= 0:
                self.last_task = now
        self.mutex.release()
        return sleep

if __name__ == '__main__':
    r = RateLimitSecond(10)
    start = time.time()
    
    def _print(i):
        '''
        打印数据
        '''
        r.wait()
        time.sleep(0.1 * (i % 10))
        print 'id=',i,' ,time=',time.time(),r.qps_info()
        
    ths = []
    for i  in range(100):
        t=threading.Thread(target=_print, args=(i, ))
        t.start()
        ths.append(t)
    for t in ths:
        t.join()
    print '=' * 100
    print 'used=',(time.time()-start)
    print 'qps_info',r.qps_info()