#       outcome/
# Serve AIML requests in the form:
#   POST:
#       { "msg": "hi there!" }
# to a HTTP client
#
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import io
import json
import sys

import aiml

#       understand/
# The Kernel object is the public interface to
# the AIML interpreter.
k = aiml.Kernel()

#       outcome/
# Use the 'learn' method to load the contents
# of an AIML file into the Kernel.
k.learn("std-startup.xml")

#       outcome/
# This command loads the 'standard' AIML files
# (TODO: Should we remove this? Users can type
# in the same command)
k.respond("load aiml b")

#       understand/
# Use a python class to handle HTTP POST requests
# with responses from the AIML kernel
class S(BaseHTTPRequestHandler):

    #       outcome/
    # Read the data sent as JSON and respond to
    # the user message (or the first message
    # if multiple are sent).
    def do_POST(self):
        global k
        content_length = int(self.headers['Content-Length'])
        data_s = self.rfile.read(content_length)
        try:
            data = json.loads(data_s)
            msg = data["msg"]
            if msg:
                if isinstance(msg, list):
                    msg = msg[0]
                self.respond_to(msg)
            else:
                self.send_response(404)
        except:
            print sys.exc_info()
            self.send_response(400)

    #       problem/
    # AIML can use variables to make the conversation
    # better (for example NAME or AGE). However, the
    # variables are set during the AIML conversation
    # which means they will vanish every time the
    # node restarts. This is awful because that means
    # ever time the node restarts the bot will forget
    # the user name, age, and other details and ask
    # her again!
    #
    #       way/
    # We will allow the user to use a key phrase
    #       EBRAINAIML SET xxxx
    # to set the various variables. A corresponding
    #       EBRAINAIML GET xxxx
    # will allow us to retrive them.
    # Otherwise we will simply let the AIML kernel
    # respond to the message.
    def respond_to(self, msg):
        pfx_get = "EBRAINAIML GET "
        pfx_set = "EBRAINAIML SET "
        if msg.startswith(pfx_get):
            name = msg[len(pfx_get):]
            if name:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(k.getPredicate(name))
            else:
                self.send_response(404)
        elif msg.startswith(pfx_set):
            cmd = msg[len(pfx_set):]
            if cmd:
                i = cmd.index(' ')
                if i < 1:
                    self.send_response(404)
                else:
                    name = cmd[:i].strip()
                    value = cmd[i:].strip()
                    k.setPredicate(name, value)
                    self.send_response(200)
            else:
                self.send_response(404)
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(k.respond(msg))


#       outcome/
# Start the HTTP server and handle keyboard interrupt
# as a shutdown
def run(server_class=HTTPServer, handler_class=S, port=8765):
    try:
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print 'Starting httpd...(localhost:%s)' % port
        httpd.serve_forever()
    except KeyboardInterrupt:
        print 'Shutting down...'
        httpd.socket.close()


if __name__ == "__main__":
    run()
