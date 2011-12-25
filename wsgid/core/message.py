#encoding: utf-8

import json

HEADER_UPLOAD_START = 'x-mongrel2-upload-start'
HEADER_UPLOAD_DONE = 'x-mongrel2-upload-done'

class Message(object):
  '''
    Represents a mongrel2 raw message
    Here we have:
     * server_id: The ID of the server that sent us this message
     * client_id: The id of the client that must receive our response
     * path: The path that was requested
     * netstring: More raw data. Here is the headers and the request body
     * headers: Mongrel headers already parsed. json -> dict
     * body: Original request body
  '''

  def __init__(self, m2message):
    self.server_id, self.client_id,\
        self.path, self.netstring = m2message.split(' ', 3)
    len_headers, rest = self.netstring.split(':', 1)

    self.headers = json.loads(rest[:int(len_headers)])
    rest_with_body = rest[int(len_headers)+1:]
    len_body , rest = rest_with_body.split(':', 1)
    self.body = rest[:int(len_body)]


  def is_disconnect(self):
    return self.path == '@*' and self.headers['METHOD'] == 'JSON'

  def is_upload_start(self):
      return 'x-mongrel2-upload-start' in self.headers and not self.is_upload_done()

  def is_upload_done(self):
      start = self.headers.get(HEADER_UPLOAD_START, 'start')
      finish = self.headers.get(HEADER_UPLOAD_DONE, 'done')
      return start == finish

  @property
  def async_upload_path(self):
      return self.headers.get(HEADER_UPLOAD_START, None)
