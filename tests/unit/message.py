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

  def test_is_start_async_upload(self):
      parsed = Message(self._build_m2message("body", {'x-mongrel2-upload-start': '/tmp/m2upload.38dG47'}))
      self.assertTrue(parsed.is_upload_start())

  def test_get_start_async_upload_path(self):
      parsed = Message(self._build_m2message("body", {'x-mongrel2-upload-start': '/tmp/m2upload.38dG47'}))
      self.assertEquals('/tmp/m2upload.38dG47', parsed.async_upload_path)


  def test_is_finish_async_upload(self):
      parsed = Message(self._build_m2message("body", {'x-mongrel2-upload-start': '/tmp/m2upload.38dG47' ,'x-mongrel2-upload-done': '/tmp/m2upload.38dG47'}))
      self.assertTrue(parsed.is_upload_done())
      self.assertFalse(parsed.is_upload_start())

  def test_is_finish_async_upload_check_values(self):
      parsed = Message(self._build_m2message("body", {'x-mongrel2-upload-start': '/tmp/m2uplo' ,'x-mongrel2-upload-done': '/tmp/m2upload.38dG47'}))
      self.assertFalse(parsed.is_upload_done())

  def test_is_finish_async_upload_no_start_header(self):
      parsed = Message(self._build_m2message("body", {'x-mongrel2-upload-done': '/tmp/m2upload.38dG47'}))
      self.assertFalse(parsed.is_upload_done())

  def test_is_finish_async_upload_no_finish_header(self):
      parsed = Message(self._build_m2message("body", {'x-mongrel2-upload-start': '/tmp/m2upload.38dG47'}))
      self.assertFalse(parsed.is_upload_done())

  def _build_m2message(self, body, headers, uuid='uuid', connid = '1', path = '/'):
      hdr_content = json.dumps(headers)
      net_str = "{len_hdr}:{header},{len_body}:{body},".format(len_hdr = len(hdr_content), header = hdr_content, len_body = len(body), body = body)
      msg = "{uuid} {connid} {path} {netstring}".format(uuid = uuid, connid = connid, path = path, netstring = net_str)
      return msg

