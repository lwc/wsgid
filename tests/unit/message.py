#encoding: utf-8


import unittest
from wsgid.core.message import Message
import json



class PaserTest(unittest.TestCase):


  def setUp(self):
    self.server_id = "uuid"
    self.client_id = "42"
    self.path = "/some/path"
    self.header_json = json.dumps({'header':'value'})
    self.netstring = "%d:%s,4:body," % (len(self.header_json), self.header_json) 


  def test_parse_mongrel2_message(self):
    msg = "%s %s %s %s" % (self.server_id, self.client_id,\
        self.path, self.netstring)
    parsed_message = Message(msg)
    self.assertEquals(self.server_id, parsed_message.server_id)
    self.assertEquals(self.client_id, parsed_message.client_id)
    self.assertEquals(self.path, parsed_message.path)
    self.assertEquals(self.netstring, parsed_message.netstring)

  def test_parse_body_with_space(self):
    body_with_space = "%d:%s,12:body w space," % (len(self.header_json), self.header_json)
    msg = "%s %s %s %s" % (self.server_id, self.client_id,\
        self.path, body_with_space)
    parsed_message = Message(msg)
    self.assertEquals(self.server_id, parsed_message.server_id)
    self.assertEquals(self.client_id, parsed_message.client_id)
    self.assertEquals(self.path, parsed_message.path)
    self.assertEquals(body_with_space, parsed_message.netstring)

  def test_parse_headers_with_space(self):
    header_w_space = json.dumps({'name': 'value with space'})
    headers_with_space = "%d:%s,4:body," % (len(header_w_space), header_w_space)
    msg = "%s %s %s %s" % (self.server_id, self.client_id,\
        self.path, headers_with_space)
    parsed_message = Message(msg)
    self.assertEquals(self.server_id, parsed_message.server_id)
    self.assertEquals(self.client_id, parsed_message.client_id)
    self.assertEquals(self.path, parsed_message.path)
    self.assertEquals(headers_with_space, parsed_message.netstring)
    
  def test_parse_real_headers(self):
    headers = {'PATH': '/some/path', 'PATTERN': '/some.*', 'host': 'localhost'}
    headers_json = json.dumps(headers)
    
    netstring = "%d:%s,4:body," % (len(headers_json), headers_json)
    
    msg = "%s %s %s %s" % (self.server_id, self.client_id,\
                           self.path, netstring)
    
    parsed_message = Message(msg)
    
    self.assertEqual(netstring, parsed_message.netstring)
    self.assertEqual(headers, parsed_message.headers)
    
  def test_parse_real_body(self):
    body = "<html> <body> some content </body> </html>"
    
    netstring = "%d:%s,%d:%s," % (len(self.header_json), self.header_json,\
                                  len(body), body)
    
    msg = "%s %s %s %s" % (self.server_id, self.client_id,\
                           self.path, netstring)
    parsed_message = Message(msg)
    
    self.assertEqual(body, parsed_message.body)

  def test_message_is_disconnect(self):
    msg = "uuid 1 @* %s"
    header = json.dumps({'METHOD': 'JSON'})
    body = json.dumps({'type': 'disconnect'})
    netstring = "%d:%s,%d:%s," % (len(header), header, len(body), body)
    parsed = Message(msg % netstring)
    self.assertTrue(parsed.is_disconnect())



