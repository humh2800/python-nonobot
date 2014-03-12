# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import optparse
import unittest

import fixtures
import nonobot.plugins


SAMPLE_ARGUMENT_PLUGIN = """
def _arguments(o):
    o.add_option('--blah')
"""

SAMPLE_PLUGIN_METHOD = """
class Plugin:
    def __init__(self, config):
        pass
    def foo(self, line, **kwargs):
        pass
    def foo_doc(self, line, **kwargs):
        "THIS IS SOME DOC"
        pass
"""

SAMPLE_PLUGIN_STREAM = """
class Plugin:
    def __init__(self, config):
        pass
    def stream(self, line, **kwargs):
        "DOC STREAM"
        pass
"""


class PluginTest(unittest.TestCase):
    def test_get_all_plugin_modules(self):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/t1.py"
            open(test_file, 'w').write("")
            test_file2 = path + "/t2.py"
            open(test_file2, 'w').write("")
            ret = [x for x in nonobot.plugins.get_all_plugin_modules(path)]
            self.assertEqual(len(ret), 2)

    def test_get_all_plugin_modules_only_py(self):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/t1.rb"
            open(test_file, 'w').write("")
            test_file2 = path + "/t2.py"
            open(test_file2, 'w').write("")
            ret = [x for x in nonobot.plugins.get_all_plugin_modules(path)]
            self.assertEqual(len(ret), 1)

    def test_get_all_plugin_modules_no__init__(self):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "__init__.py"
            open(test_file, 'w').write("")
            test_file2 = path + "/t2.py"
            open(test_file2, 'w').write("")
            ret = [x for x in nonobot.plugins.get_all_plugin_modules(path)]
            self.assertEqual(len(ret), 1)

    def test_plugin_add_extra_options(self):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/t1.py"
            open(test_file, 'w').write(SAMPLE_ARGUMENT_PLUGIN)
            optp = optparse.OptionParser()
            nonobot.plugins.plugins_add_extra_options(path, optp)
            self.assertTrue(optp.has_option('--blah'))

    def test_plugin_methods(self):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/t1.py"
            open(test_file, 'w').write(SAMPLE_PLUGIN_METHOD)
            plugins = nonobot.plugins.get_plugins_methods(path, {'foo: bar'})
            self.assertEqual(len(plugins), 2)
            for i in plugins:
                if type(i) != str:
                    first_plugin = plugins[i]
            self.assertEqual(len(first_plugin), 2)
            self.assertIn('foo', first_plugin)
            self.assertIn('foo_doc', first_plugin)
            self.assertEqual(first_plugin['foo_doc']['doc'],
                             'THIS IS SOME DOC')
            self.assertIn('help', plugins)
            self.assertEqual(len(plugins['help']), 1)
            self.assertEqual(plugins['help'],
                             ['[t1] foo_doc: THIS IS SOME DOC'])

    def test_plugin_stream_method(self):
        with fixtures.cleaned_tempdir() as path:
            test_file = path + "/tstream.py"
            open(test_file, 'w').write(SAMPLE_PLUGIN_STREAM)
            plugins = nonobot.plugins.get_plugins_methods(path, {'foo: bar'})
            self.assertEqual(len(plugins), 2)
            for i in plugins:
                if type(i) != str:
                    first_plugin = plugins[i]
            self.assertEqual(len(first_plugin), 1)
            self.assertIn('stream', first_plugin)
            self.assertEqual(first_plugin['stream']['doc'],
                             'DOC STREAM')
            self.assertIn('help', plugins)
            self.assertEqual(len(plugins['help']), 1)
            self.assertEqual(plugins['help'], ['[tstream] DOC STREAM'])

    def test_plugin_class(self):
        config = {'hello': 'moto'}
        cl = nonobot.plugins.Base(config)
        self.assertIn('hello', cl.config)
