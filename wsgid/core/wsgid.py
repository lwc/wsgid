#encoding: utf-8

import urllib
from message import Message
from . import StartResponse, get_main_logger
import zmq
from StringIO import StringIO
import sys
import os
from parser import parse_options

class Wsgid(object):

  def __init__(self, app = None, recv = None, send = None):
    self.app = app
    self.recv = recv
    self.send = send

    self.ctx = zmq.Context()
    self.log = get_main_logger()

  '''
   Start serving requests.
  '''
  def serve(self):
    recv_sock = self.ctx.socket(zmq.PULL)
    recv_sock.connect(self.recv)
    self.log.debug("Using PULL socket %s" % self.recv)

    send_sock = self.ctx.socket(zmq.PUB)
    send_sock.connect(self.send)
    self.log.debug("Using PUB socket %s" % self.send)

    self.log.info("All set, ready to serve requests...")
    while True:
      m2message = Message(recv_sock.recv())

      if m2message.is_disconnect():
        self.log.debug("Disconnect message received, id=%s" % m2message.client_id)
        continue

      if m2message.is_upload_start():
        self.log.debug("Starting async upload, file will be at: {0}".format(m2message.async_upload_path))
        continue


      # Call the app and send the response back to mongrel2
      self._call_wsgi_app(m2message, send_sock)

  def _call_wsgi_app(self, m2message, send_sock):
    environ = self._create_wsgi_environ(m2message.headers, m2message.body)
    upload_path = parse_options().mongrel2_chroot

    if m2message.is_upload_done():
        self.log.debug("Async upload done, reading from {0}".format(m2message.async_upload_path))
        parts = m2message.async_upload_path.split('/')
        upload_path = os.path.join(upload_path, *parts)
        environ['wsgi.input'] = open(upload_path)

    start_response = StartResponse()

    server_id = m2message.server_id
    client_id = m2message.client_id
    response = None
    try:
      body = ''
      response = self.app(environ, start_response)

      if start_response.body_written:
        body = start_response.body
      else:
        for data in response:
          body += data

      status = start_response.status
      headers = start_response.headers
      send_sock.send(str(self._reply(server_id, client_id, status, headers, body)))
    except Exception, e:
      # Internal Server Error
      send_sock.send(self._reply(server_id, client_id, '500 Internal Server Error', headers=[]))
      self.log.exception(e)
    finally:
      if hasattr(response, 'close'):
        response.close()
      if m2message.is_upload_done():
        self._remove_tmp_file(upload_path)

  def _remove_tmp_file(self, filepath):
      try:
        os.unlink(filepath)
      except OSError, o:
        self.log.exception(o)


  '''
   Constructs a mongrel2 response message based on the
   WSGI app response values.
   @uuid, @conn_id comes from Wsgid itself
   @headers, @body comes from the executed application

   @body is the raw content of the response and not [body]
   as returned by the WSGI app
   @headers is a list of tuples
  '''
  def _reply(self, uuid, conn_id, status, headers = [], body = ''):
    RAW_HTTP = "HTTP/1.1 %(status)s\r\n%(headers)s\r\n%(body)s"
    msg = "%s %d:%s, " % (uuid, len(conn_id), conn_id)
    params = {'status': status, 'body': body}

    headers += [('Content-Length', len(body))]
    raw_headers = ""
    for h,v in headers:
      raw_headers += "%s: %s\r\n" % (h,v)

    params['headers'] = raw_headers
    return msg + RAW_HTTP % params

  '''
   Creates a complete WSGI environ from the JSON encoded headers
   reveived from mongrel2.
   @json_headers should be an already parsed JSON string
  '''
  def _create_wsgi_environ(self, json_headers, body=None):
    environ = {}
    #Not needed
    json_headers.pop('URI', None)

    #First, some fixed values
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once'] = True
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.version'] = (1,0)
    self._set(environ, 'wsgi.url_scheme', "http")


    if body:
      environ['wsgi.input'] = StringIO(body)
    else:
      environ['wsgi.input'] = StringIO('')


    self._set(environ, 'REQUEST_METHOD', json_headers.pop('METHOD'))
    self._set(environ, 'SERVER_PROTOCOL', json_headers.pop('VERSION'))
    self._set(environ, 'SCRIPT_NAME', json_headers.pop('PATTERN').rstrip('/'))
    self._set(environ, 'QUERY_STRING', json_headers.pop('QUERY', ""))

    script_name = environ['SCRIPT_NAME']
    path_info = json_headers.pop('PATH')[len(script_name):]
    self._set(environ, 'PATH_INFO', urllib.unquote(path_info))

    server_port = '80'
    host_header = json_headers.pop('host')
    if ':' in host_header:
      server_name, server_port = host_header.split(':')
    else:
      server_name = host_header

    self._set(environ, 'HTTP_HOST', host_header)
    self._set(environ, 'SERVER_PORT', server_port)
    self._set(environ, 'SERVER_NAME', server_name)

    self._set(environ, 'REMOTE_ADDR', json_headers['x-forwarded-for'])

    self._set(environ, 'CONTENT_TYPE', json_headers.pop('content-type', ''))
    environ['content-type'] = environ['CONTENT_TYPE']

    self._set(environ, 'CONTENT_LENGTH', json_headers.pop('content-length', ''))
    environ['content-length'] = environ['CONTENT_LENGTH']

    #Pass the other headers
    for (header, value) in json_headers.iteritems():
      if header[0] in ('X', 'x'):
        environ[header] = str(value)
      else:
        # Change HTTP_ headers to CGI-like formatting
        header = header.upper()
        environ['HTTP_%s' % header] = str(value)

    return environ

  '''
   Sets a value in the environ object
  '''
  def _set(self, environ, key, value):
    environ[key] = str(value)


