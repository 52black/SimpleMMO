import unittest
from mock import patch, Mock

import sys
sys.path.append(".")
from scriptserver import ZoneScriptRunner

class TestZoneScriptRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mongoengine_patch = patch('scriptserver.me')
        cls.mongoengine_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.mongoengine_patch.stop()

    def test___init__(self):
        zoneid = "zoneid"
        with patch('scriptserver.Object'):
            with patch.object(ZoneScriptRunner, 'load_scripts') as mock_load_scripts:
                zone_script_runner = ZoneScriptRunner(zoneid)
                self.assertTrue(zone_script_runner)
        self.assertEqual(1, mock_load_scripts.call_count)

    def test_load_scripts(self):
        expected = {}
        zoneid = "zoneid"
        with patch.object(ZoneScriptRunner, 'load_scripts'):
            with patch('scriptserver.Object'):
                zone_script_runner = ZoneScriptRunner(zoneid)

        with patch('scriptserver.ScriptedObject') as ScriptedObject:
                MockThing = Mock()
                with patch.dict('sys.modules', {'thing': MockThing, 'thing.fake': MockThing.fake,
                                                'thing.fake.chicken': MockThing.fake.chicken}):
                    MockThing.fake.chicken.Chicken.tick = Mock()
                    MockScriptedObject = Mock()
                    MockScriptedObject.scripts = ['thing.fake.chicken']
                    ScriptedObject.objects.return_value = [MockScriptedObject]
                    result = zone_script_runner.load_scripts()

        self.assertNotEqual(expected, result)
        self.assertIn('thing.fake.chicken', result)

    def test_start(self):
        # zone_script_runner = ZoneScriptRunner(zoneid)
        # self.assertEqual(expected, zone_script_runner.start())
        pass # TODO: implement your test here

    def test_tick(self):
        # zone_script_runner = ZoneScriptRunner(zoneid)
        # self.assertEqual(expected, zone_script_runner.tick())
        pass # TODO: implement your test here

if __name__ == '__main__':
    unittest.main()
