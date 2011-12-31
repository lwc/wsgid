#encoding: utf-8


import unittest

import zmq
from wsgid.core.wsgid import Wsgid
from wsgid.core.message import Message
import sys

from mock import patch, Mock, MagicMock

class WsgidTest(unittest.TestCase):

  def setUp(self):
    self.wsgid = Wsgid()
    self.sample_headers = {
          'METHOD': 'GET',
          'VERSION': 'HTTP/1.1',
          'PATTERN': '/root',
          'URI': '/more/path/',
          'PATH': '/more/path',
          'QUERY': 'a=1&b=4&d=4',
          'host': 'localhost',
          'content-length': '42',
          'content-type': 'text/plain',
          'x-forwarded-for': '127.0.0.1'
        }
  def tearDown(self):
    self.sample_headers = {}

  '''
   Creates the SCRIPT_NAME header from the mongrel2 PATTERN header.
   SCRIPT_NAME should be the PATTERN without any regex parts.
  '''
  def test_script_name_header_simple_path(self):
    self.sample_headers['PATTERN'] = "/py"
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals("/py", environ['SCRIPT_NAME'])

  def test_environ_script_name_header_more_comples_header(self):
    self.sample_headers['PATTERN'] = '/some/more/path/'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals("/some/more/path", environ['SCRIPT_NAME'])

  def test_environ_script_name_header_root(self):
    self.sample_headers['PATTERN'] = '/'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals("", environ['SCRIPT_NAME'])


  '''
   PATH_INFO comes from (URI - SCRIPT_NAME) or (PATH - SCRIPT_NAME)
  '''
  def test_environ_path_info(self):

    self.sample_headers['PATTERN'] = '/py'
    self.sample_headers['PATH'] = '/py/some/py/path'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals("/some/py/path", environ['PATH_INFO'])

  def test_environ_path_info_app_root(self):
    self.sample_headers['PATTERN'] = '/py'
    self.sample_headers['PATH'] = '/py'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals("", environ['PATH_INFO'])


  def test_environ_unquoted_path_info(self):
    self.sample_headers['PATTERN'] = '/py/'
    self.sample_headers['PATH'] = '/py/so%20me/special%3f/user%40path'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('/so me/special?/user@path', environ['PATH_INFO'])

  '''
   Generates de REQUEST_METHOD variable
  '''
  def test_environ_request_method(self):
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertTrue(environ.has_key('REQUEST_METHOD'))
    self.assertEquals('GET', environ['REQUEST_METHOD'])


  def test_environ_query_string(self):
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals("a=1&b=4&d=4", environ['QUERY_STRING'])

  def test_environ_no_query_string(self):
    #Not always we have a QUERY_STRING
    del self.sample_headers['QUERY']
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals("", environ['QUERY_STRING'])


  def test_environ_server_port(self):
    self.sample_headers['host'] = 'localhost:443'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('443', environ['SERVER_PORT'])

  def test_environ_server_port_default_port(self):
    self.sample_headers['host'] = 'localhost'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('80', environ['SERVER_PORT'])

  def test_environ_server_name(self):
    self.sample_headers['host'] = 'localhost:8080'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('localhost', environ['SERVER_NAME'])

  def test_environ_server_name_default_port(self):
    self.sample_headers['host'] = 'someserver'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('someserver', environ['SERVER_NAME'])

  '''
   HTTP_HOST must inclue the port, if present.
  '''
  def test_environ_http_host(self):
    self.sample_headers['host'] = 'localhost:8080'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('localhost:8080', environ['HTTP_HOST'])

  def test_environ_content_type(self):
    self.sample_headers['content-type'] = 'application/xml'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('application/xml', environ['CONTENT_TYPE'])

  def test_environ_no_content_type(self):
    del self.sample_headers['content-type']
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('', environ['CONTENT_TYPE'])

  def test_environ_content_length(self):
    self.sample_headers['content-length'] = '42'
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('42', environ['CONTENT_LENGTH'])

  def test_environ_no_content_length(self):
    del self.sample_headers['content-length']
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('', environ['CONTENT_LENGTH'])

  '''
   Comes from mongrel2 VERSION header
  '''
  def test_environ_server_protocol(self):
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertTrue(environ.has_key('SERVER_PROTOCOL'))
    self.assertEquals('HTTP/1.1', environ['SERVER_PROTOCOL'])


  def test_eviron_remote_addr(self):
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('127.0.0.1', environ['REMOTE_ADDR'])


  '''
   Non Standard headers (X-) are passed untouched
  '''
  def test_environ_non_standart_headers(self):
    self.sample_headers['X-Some-Header'] = 'some-value'
    self.sample_headers['x-other-header'] = 'other-value'

    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('some-value', environ['X-Some-Header'])
    self.assertEquals('other-value', environ['x-other-header'])

  def test_environ_http_host_header(self):
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('localhost', environ['HTTP_HOST'])

  '''
   All headers (but HTTP common headers and X- headers) must be HTTP_ suffixed
  '''
  def test_environ_other_headers(self):
    self.sample_headers['my_header'] = 'some-value'
    self.sample_headers['OTHER_HEADER'] = 'other-value'
    self.sample_headers['X-Some-Header'] = 'x-header'
    self.sample_headers['Accept'] = '*/*'
    self.sample_headers['Referer'] = 'http://www.someserver.com'

    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals('some-value', environ['HTTP_MY_HEADER'])
    self.assertEquals('other-value', environ['HTTP_OTHER_HEADER'])
    self.assertEquals('x-header', environ['X-Some-Header'])
    self.assertEquals('*/*', environ['HTTP_ACCEPT'])
    self.assertEquals('http://www.someserver.com', environ['HTTP_REFERER'])


  '''
   Test a complete request, with all typed of headers.
  '''
  def test_eviron_complete_request(self):
    request = {
          'METHOD': 'GET',
          'VERSION': 'HTTP/1.1',
          'PATTERN': '/py',
          'URI': '/py/some/path',
          'PATH': '/py/some/path',
          'QUERY': 'a=1&b=4&d=4',
          'host': 'localhost',
          'Accept': '*/*',
          'CUSTOM_HEADER': 'value',
          'User-Agent': 'some user agent/1.0',
          'content-length': '42',
          'content-type': 'text/plain',
          'x-forwarded-for': '127.0.0.1'
        }

    environ = self.wsgid._create_wsgi_environ(request)
    self.assertEquals(24, len(environ))
    self.assertEquals('GET', environ['REQUEST_METHOD'])
    self.assertEquals('HTTP/1.1', environ['SERVER_PROTOCOL'])
    self.assertEquals('/py', environ['SCRIPT_NAME'])
    self.assertEquals('a=1&b=4&d=4', environ['QUERY_STRING'])
    self.assertEquals('/some/path', environ['PATH_INFO'])
    self.assertEquals('localhost', environ['SERVER_NAME'])
    self.assertEquals('80', environ['SERVER_PORT'])
    self.assertEquals('value', environ['HTTP_CUSTOM_HEADER'])
    self.assertEquals('*/*', environ['HTTP_ACCEPT'])
    self.assertEquals('some user agent/1.0', environ['HTTP_USER-AGENT'])
    self.assertEquals('42', environ['CONTENT_LENGTH'])
    self.assertEquals('42', environ['content-length'])
    self.assertEquals('text/plain', environ['CONTENT_TYPE'])
    self.assertEquals('text/plain', environ['content-type'])
    self.assertEquals('localhost', environ['HTTP_HOST'])
    self.assertEquals('127.0.0.1', environ['REMOTE_ADDR'])

  '''
   Some values are fixed:
    * wsgi.multithread = False
    * wsgi.multiprocess = True
    * wsgi.run_once = True
    * wsgi.version = (1,0)
  '''
  def test_environ_fixed_values(self):
    environ = self.wsgid._create_wsgi_environ(self.sample_headers)
    self.assertEquals(False, environ['wsgi.multithread'])
    self.assertEquals(True, environ['wsgi.multiprocess'])
    self.assertEquals(True, environ['wsgi.run_once'])
    self.assertEquals((1,0), environ['wsgi.version'])
    self.assertEquals("http", environ['wsgi.url_scheme'])
    self.assertEquals(sys.stderr, environ['wsgi.errors'])

  def test_join_m2_chroot_to_async_upload_path(self):
      # The value in x-mongrel2-upload-{start,done} should be prepended with the
      # value of --m2-chroot, passed on the command line
      with patch('zmq.Context'):
          def _serve_request(wsgid, m2message, expected_final_path):
            with patch.object(wsgid, '_create_wsgi_environ'):
                wsgid._create_wsgi_environ.return_value = {}
                with patch("__builtin__.open") as mock_open:
                    with patch('os.unlink'):
                        wsgid._call_wsgi_app(message, Mock())
                        self.assertEquals(1, mock_open.call_count)
                        mock_open.assert_called_with(expected_final_path)

          sys.argv[1:] = ['--mongrel2-chroot=/var/mongrel2']
          wsgid = Wsgid(app = Mock(return_value=['body response']))

          message = self._create_fake_m2message('/uploads/m2.84Yet4')
          _serve_request(wsgid, message, '/var/mongrel2/uploads/m2.84Yet4')
          sys.argv[1:] = [] #Simulate --mongrel2-chroo not passed, assume "/"
          _serve_request(wsgid, message, '/uploads/m2.84Yet4')


  def test_remove_async_file_after_request_finishes_ok(self):
      # Since mongrel2 does not remove the originial temp file, wsgid
      # must remove it after the request was successfully (or not) handled.
      with patch('zmq.Context'):
          with patch('os.unlink') as mock_unlink:
            def _serve_request(wsgid, m2message):
                with patch.object(wsgid, '_create_wsgi_environ'):
                    wsgid._create_wsgi_environ.return_value = {}
                    with patch("__builtin__.open") as mock_open:
                        wsgid._call_wsgi_app(message, Mock())

            wsgid = Wsgid(app = Mock(return_value=['body response']))

            message = self._create_fake_m2message('/uploads/m2.84Yet4')
            _serve_request(wsgid, message)
            mock_unlink.assert_called_with('/uploads/m2.84Yet4')


  def test_remove_async_file_after_failed_request(self):
      # Even if the request failed, wsgid must remove the temporary file.
       with patch('zmq.Context'):
          with patch('os.unlink') as mock_unlink:
            def _serve_request(wsgid, m2message):
                with patch.object(wsgid, '_create_wsgi_environ'):
                    wsgid._create_wsgi_environ.return_value = {}
                    with patch("__builtin__.open") as mock_open:
                        wsgid._call_wsgi_app(message, Mock())

            wsgid = Wsgid(app = Mock(side_effect = Exception("Failed")))
            wsgid.log = Mock()
            sys.argv[1:] = []
            message = self._create_fake_m2message('/uploads/m2.84Yet4')
            _serve_request(wsgid, message)
            mock_unlink.assert_called_with('/uploads/m2.84Yet4')

  def test_protect_against_exception_on_file_removal(self):
        with patch('zmq.Context'):
          with patch('os.unlink') as mock_unlink:
            mock_unlink.side_effect = OSError("File does not exist")
            def _serve_request(wsgid, m2message):
                with patch.object(wsgid, '_create_wsgi_environ'):
                    wsgid._create_wsgi_environ.return_value = {}
                    with patch("__builtin__.open") as mock_open:
                        wsgid._call_wsgi_app(message, Mock())

            wsgid = Wsgid(app = Mock(return_value = ['body response']))
            wsgid.log = Mock()
            sys.argv[1:] = []
            message = self._create_fake_m2message('/uploads/m2.84Yet4')
            _serve_request(wsgid, message)
            self.assertEquals(1, wsgid.log.exception.call_count)

  def _create_fake_m2message(self, async_upload_path):
        message = Mock()
        message.headers = {'x-mongrel2-upload-start': async_upload_path,
                            'x-mongrel2-upload-done': async_upload_path}
        message.async_upload_path = async_upload_path
        message.server_id = 'uuid'
        message.client_id = '42'
        return message

class WsgidReplyTest(unittest.TestCase):


  def setUp(self):
    self.wsgid = Wsgid()
    self.sample_uuid = 'bb3ce668-4528-11e0-94e3-001fe149503a'
    self.sample_conn_id = '42'

  def test_reply_no_headers(self):
    m2msg = self.wsgid._reply(self.sample_uuid, self.sample_conn_id, '200 OK', body='Hello World\n')
    resp = "%s 2:42, HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\nHello World\n" % (self.sample_uuid)
    self.assertEquals(resp, m2msg)

  def test_reply_no_body(self):
    headers = [('Header', 'Value'), ('X-Other-Header', 'Other-Value')]
    m2msg = self.wsgid._reply(self.sample_uuid, self.sample_conn_id, '200 OK', headers=headers)
    resp = "%s 2:42, HTTP/1.1 200 OK\r\n\
Header: Value\r\n\
X-Other-Header: Other-Value\r\n\
Content-Length: 0\r\n\r\n" % (self.sample_uuid)
    self.assertEquals(resp, m2msg)

  def test_reply_with_body_andheaders(self):
    headers = [('Header', 'Value'), ('X-Other-Header', 'Other-Value')]
    body = "Hello World\n"
    m2msg = self.wsgid._reply(self.sample_uuid, self.sample_conn_id, '200 OK', headers=headers, body=body)
    resp = "%s 2:42, HTTP/1.1 200 OK\r\n\
Header: Value\r\n\
X-Other-Header: Other-Value\r\n\
Content-Length: 12\r\n\r\n\
Hello World\n" % (self.sample_uuid)
    self.assertEquals(resp, m2msg)


