#!/usr/bin/env python2.7
import unittest

import sys
sys.path.append(".")

import settings

import client

authserver = None


class TestClient(unittest.TestCase):
    '''An integration test for the Client class.'''
    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        # Fire up a server to test against.
        import subprocess
        import requests
        cls.servers = []
        from collections import OrderedDict
        servers = OrderedDict()
        servers[settings.AUTHSERVER] = [sys.executable]+['authserver.py', '--dburi=sqlite://']
        servers[settings.CHARSERVER] = [sys.executable]+['charserver.py', '--dburi=sqlite://']
        servers['http://localhost:28017'] = ['mongod', '--rest', '--oplogSize=1', '--directoryperdb', '--smallfiles', '--dbpath=./mongodb-unittest/']
        servers[settings.ZONESERVER] = [sys.executable]+['masterzoneserver.py', '--dburi=sqlite://']
        for uri, args in servers.iteritems():
            print "Starting %s at %s" % (' '.join(args), uri)
            cmd = args
            s = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            cls.servers.append(s)
            status = None
            while status != 200:
                try:
                    r = requests.get(uri)
                    status = r.status_code
                except requests.ConnectionError:
                    continue

    @classmethod
    def tearDownClass(cls):
        from signal import SIGINT
        for server in cls.servers:
            server.send_signal(SIGINT)

    def test___init__(self):
        c = client.Client()
        self.assertTrue(c)

    def test___init___autoauth(self):
        c = client.Client(username=settings.DEFAULT_USERNAME, password=settings.DEFAULT_PASSWORD)
        self.assertTrue(c.cookies)
        self.assertTrue(c.cookies['user'])

    def test___init___autoauth_bad(self):
        with self.assertRaises(client.AuthenticationError):
            client.Client(username="BadUser", password="BadPassword")

    def test_authenticate(self):
        c = client.Client()
        result = c.authenticate(username=settings.DEFAULT_USERNAME, password=settings.DEFAULT_PASSWORD)
        self.assertTrue(result)

    def test_authenticate_bad(self):
        c = client.Client()
        result = c.authenticate(username='BadUser', password='BadPassword')
        self.assertFalse(result)

    def test_characters(self):
        c = client.Client(username=settings.DEFAULT_USERNAME, password=settings.DEFAULT_PASSWORD)
        self.assertTrue(c.characters)
        self.assertTrue('Graxnor' in c.characters)

    def test_characters_get_obj(self):
        c = client.Client(username=settings.DEFAULT_USERNAME, password=settings.DEFAULT_PASSWORD)
        self.assertTrue('Graxnor' in c.characters)
        self.assertTrue(c.characters['Graxnor'])

    def test_character_obj_zone(self):
        c = client.Client(username=settings.DEFAULT_USERNAME, password=settings.DEFAULT_PASSWORD)
        self.assertTrue(c.get_zone('Graxnor'))

    def test_get_zone_url(self):
        c = client.Client(username=settings.DEFAULT_USERNAME, password=settings.DEFAULT_PASSWORD)
        zoneid = c.get_zone('Graxnor')
        zoneurl = c.zone(zoneid)
        print zoneurl
        self.assertTrue('http' in zoneurl)


if __name__ == '__main__':
    unittest.main()
