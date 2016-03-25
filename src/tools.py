# -*- coding:utf-8 -*-

import redis


class Adsl(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = redis.StrictRedis(host=host, port=port, db=0)

    def getlines(self):
        ret = self.conn.keys()
        return ret

    def getall(self):
        lines = self.getlines()
        ret = []
        for line in lines:
            data = self.conn.hgetall(line)
            ret.append(data)
        return ret

    def getavailablelines(self):
        lines = self.getlines()
        ret = []
        for line in lines:
            status = self.getstatusbyline(line)
            if status == 'available':
                ret.append(line)
        return ret

    def getnumsavailablelines(self, num):
        availablelines = self.getavailablelines()
        ret = []
        if len(availablelines) > 0:
            if len(availablelines) > num:
                ret = availablelines[0:num]
            else:
                ret = availablelines

        for line in ret:
            self.setstatusbyline(line, 'using')

        return ret

    def getadslbyline(self, line):
        ret = self.conn.hget(line, 'ip_adsl')
        return ret

    def getidcbyline(self, line):
        ret = self.conn.hget(line, 'ip_idc')
        return ret

    def getstatusbyline(self, line):
        ret = self.conn.hget(line, 'status')
        return ret

    def setstatusbyline(self, line, status):
        key = 'status'
        value = status
        ret = self.conn.hset(line, key, value)
        return ret

    def setadslbyline(self, line, ip_adsl):
        key = 'ip_adsl'
        value = ip_adsl
        ret = self.conn.hset(line, key, value)
        return ret

    def setidcbyline(self, line, ip_idc):
        key = 'ip_idc'
        value = ip_idc
        ret = self.conn.hset(line, key, value)
        return ret

    def additem(self, line, ip_idc, ip_adsl):
        status = 'available'
        data = {'ip_idc': ip_idc, 'ip_adsl': ip_adsl, 'status': status}
        ret = self.conn.hmset(line, data)
        return ret

    def exists(self, line):
        return self.conn.exists(line)
