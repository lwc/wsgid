



import unittest
from wsgid.options import parser

class ParserTest(unittest.TestCase):

  def setUp(self):
    parser.options = []


  def test_add_option_string(self):
    parser.add_option(name='test')

    self.assertEquals(1, len(parser.options))
    self.assertEquals('--test', parser.options[0].name)

  def test_do_not_add_noname_option(self):
    parser.add_option(help='Help op noname option')

    self.assertEquals(0, len(parser.options))

  def test_add_bool_option_default_true(self):
    parser.add_option(name = 'keep-alive', type = parser.BOOL, default_value = True)
    self.assertEquals('store_true', parser.options[0].action)

  def test_add_bool_option_default_false(self):
    parser.add_option(name = 'keep-alive', type = parser.BOOL, default_value = False)
    self.assertEquals('store_false', parser.options[0].action)
  
  def test_add_bool_option_no_default_value(self):
    parser.add_option(name = 'keep-alive', type = parser.BOOL)
    self.assertEquals('store_true', parser.options[0].action)

  def test_add_list_option(self):
    parser.add_option(name='loader-dir', type = parser.LIST)
    self.assertEquals('append', parser.options[0].action)

  def test_add_int_option(self):
    parser.add_option(name='loader-dir', type = parser.INT)
    self.assertEquals('store', parser.options[0].action)
    self.assertEquals('int', parser.options[0].type)

