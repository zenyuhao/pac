#!/usr/bin/env python
#-*-coding:utf-8 -*-
#author:Zen 2011

import BaseHTTPServer
import SocketServer
import sys,os
import cgi
import shutil

info={
}

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def store(username, line):
    print line
    os.system("echo \""+line+"\" >> "+info[username]["path_username"]+".path.tl")

def get_info():
    global info
    for i in range(1,len(sys.argv)):
        f = open(sys.argv[i], 'r+')
        username = sys.argv[i][:-5]
        info[username] = {}
        for line in f.readlines():
            kv=line[:-1].split("=")
            if len(kv)!=2:continue
            info[username][kv[0]]=kv[1]
        f.close()

def get_tl(username):
    replys = []
    f = open(info[username]["path_username"]+".path.tl", 'r+')
    for line in f.readlines():
        replys.append(line[:-1])
    f.close()
    return replys

class ZenHttp(BaseHTTPServer.BaseHTTPRequestHandler):
      def do_GET(self):
          filename=self.path[1:]
          print filename
          self.send_response(200)
          #self.send_header("content-type", "application/pdf;charset=utf-8")
          #self.send_header("content-type", "image/png;charset=utf-8")
          self.send_header("content-type", "text/html;charset=utf-8")
          self.end_headers()
          str=""
          try:
              str=open(filename,'rb').read()
          except:
              str="error!"
          self.wfile.write(str)

      def do_POST(self):
          username=self.path[6:-5]
          
          form = cgi.FieldStorage(
                 fp=self.rfile, 
                 headers=self.headers,
                 environ={'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers['Content-Type'],
                         })


          self.send_response(200)
          self.send_header("content-type", "text/html;charset=utf-8")
          self.end_headers()
          #self.wfile.write('Client: %s\n' % str(self.client_address))
          #self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
          #self.wfile.write('Path: %s\n' % self.path)
          #self.wfile.write('Form data:\n')

          # Echo back information about what was posted in the form
          for field in form.keys():
              field_item = form[field]
              if field_item.filename:
                  # The field contains an uploaded file
                  file_data = field_item.file.read()
                  file_len = len(file_data)
                  del file_data
                  self.wfile.write('\tUploaded %s as "%s" (%d bytes)\n' % \
                          (field, field_item.filename, file_len))
              else:
                  store(username, form[field].value.replace("\r\n", "<br>"))
                  # Regular form value
                  f = StringIO()
                  f.write('\
                  <!DOCTYPE html>\
                  <html lang="zh-cn">\
                  <script language=javascript>\n\
                  ie = (document.all)? true:false\n\
                  if (ie) {\n\
                  function ctlent(eventobject)\n\
                  {\n\
                  if(event.ctrlKey && window.event.keyCode==13) {\n\
                  this.document.form1.submit();\n\
                  }}}\n\
                  </script>\
                  <head>\
                  <meta charset="gbk" />\
                  <meta name="robots" content="all" />\
                  <meta name="author" content="w3school.com.cn" />\
                  </head>\
                  <body>\
                  <div align="center">\
                  <div style="width:900px>\
                  <div style="width:1000px;height:30px">\
                  <img width="18" height="18" src="/icon.jpg"> 为阿水量身打造的Path极简主义网页版 -- Power by Captain Zen\
                  </div>\
                  <div align="center">\
                  <form action="/path/'+info[username]["path_username"]+'.html" method=POST name=form1>\
                  <textarea cols=95 name=Content rows=12 wrap=virtual onkeydown=ctlent()></textarea>\
                  <input type=submit value="Submit" name=Submit style="display:none">\
                  </div>\
                  </form>')
                    
                  lines = get_tl(username)
                  for i in range(0, len(lines)):
                      f.write('<div>'+lines[len(lines)-1-i]+'</div>\n') 
                      f.write('<div>------------------------</div>\n') 

                  f.write('\
                  </div>\
                  </div>\
                  </body>\
                  </html>\
                  ')
                  f.seek(0)
                  shutil.copyfileobj(f, self.wfile)
                  f.close()
                  os.system("/root/fanfou/access_token/path_post.sh \""+form[field].value.replace("\r\n", "\\n")+"\" "+info[username]["path_access_token"])

      def handle_one_request(self):
        """Handle a single HTTP request.
 
        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.
 
        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(501, "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            method()
            #增加 debug info 及 wfile 判断是否已经 close
            if not self.wfile.closed:
                self.wfile.flush() #actually send the response if not already done.
        except socket.timeout, e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return

if __name__ == "__main__":

    get_info()
    print info

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.exit(1)

    # decouple from parent environment
    os.chdir("/root/pac") 
    os.setsid() 
    os.umask(0) 

    # do second fork
#    try: 
#        pid = os.fork() 
#        if pid > 0:
#            # exit from second parent, print eventual PID before
#            print "Daemon PID %d" % pid 
#            sys.exit(0) 
#    except OSError, e: 
#        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
#        sys.exit(1) 

    Handler=ZenHttp
    httpd = SocketServer.TCPServer(("104.131.159.210",80), Handler)
    print "serving at port 80"
    httpd.serve_forever()
