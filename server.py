import socket
import signal
import sys
import random

# Read a command line argument for the port where the server
# must run.
port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8080")

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

### Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://localhost:%d" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
""" % port
# Default: Login page.
login_page = "<h1>Please login</h1>" + login_form
# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form
# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://localhost:%d" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
""" % port

#### Helper functions
# Printing.
def print_value(tag, value):
    print "Here is the", tag
    print "\"\"\""
    print value
    print "\"\"\""
    print

# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)
# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)


# TODO: put your application logic here!
# Read login credentials for all the users
# Read secret data of all the users
# Building the passwords db
passwordsDictionary = {}
inPasswords = open("passwords.txt", "r+")
passwords = inPasswords.readlines()
numUsers = len(passwords)
for i in range(0,numUsers):
    curUserPas = passwords[i].split()
    passwordsDictionary[curUserPas[0]] = curUserPas[1]
print(passwordsDictionary)

# Building the secrets db
secretsDictionary = {}
inSecrets = open("secrets.txt", "r+")
secrets = inSecrets.readlines()
numSecrets = len(secrets)
for i in range(0,numSecrets):
    curSecret = secrets[i].split()
    secretsDictionary[curSecret[0]] = curSecret[1]
print(secretsDictionary)
cookiesDictonary = {}

### Loop to accept incoming HTTP connections and respond.
while True:
    client, addr = sock.accept()
    req = client.recv(1024)

    # Let's pick the headers and entity body apart
    header_body = req.split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    print_value('headers', headers)
    print_value('entity body', body)
    # TODO: Put your application logic here!
    # Parse headers and body and perform various actions
    headers_to_send = ''
    if headers.startswith('GET'):
        html_content_to_send = login_page
        cookies = headers
    elif headers.startswith('POST'):
        #Case Logout
        typeAction = body.split('=')
        if typeAction[0].__eq__('action'):
            headers_to_send = 'Set-Cookie: token=; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n'
            html_content_to_send = logout_page
        else:
            splitHeader = headers.split('\r\n')
            tokenData = splitHeader[len(splitHeader) - 1].split('=')
            cookieToken = tokenData[1]
            # Case C - cookie header present and valid
            if tokenData[0].startswith('Cookie'):
                if cookieToken in cookiesDictonary:
                    html_content_to_send = success_page + secretsDictionary[cookiesDictonary[cookieToken]]
                else:
                    html_content_to_send = bad_creds_page
            else:
                username = ''
                password = ''
                if typeAction[0].__eq__('username'):
                    enteredInfo = body.split('&')
                    usernameInfo = enteredInfo[0].split('=')
                    passwordInfo = enteredInfo[1].split('=')
                    username = usernameInfo[1]
                    password = passwordInfo[1]
                    #case B
                    if not username or not password:
                        html_content_to_send = bad_creds_page
                    #Case A
                    if username in passwordsDictionary:
                        if password.__eq__(passwordsDictionary[username]):
                            if username in secretsDictionary:
                                html_content_to_send = success_page + secretsDictionary[username]
                                rand_val = random.getrandbits(64)
                                cookiesDictonary[str(rand_val)] = username
                                headers_to_send = 'Set-Cookie: token=' + str(rand_val) + '\r\n'
                            else:
                                html_content_to_send = success_page 
                        else:
                            html_content_to_send = bad_creds_page
                    else: 
                        html_content_to_send = bad_creds_page
            # You need to set the variables:
            # (1) `html_content_to_send` => add the HTML content you'd
            # like to send to the client.
            # Right now, we just send the default login page.
            #html_content_to_send = login_page
    # But other possibilities exist, including
    # html_content_to_send = success_page + <secret>
    # html_content_to_send = bad_creds_page
    # html_content_to_send = logout_page
    
    # (2) `headers_to_send` => add any additional headers
    # you'd like to send the client?
    # Right now, we don't send any extra headers.

    # Construct and send the final response
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    print_value('response', response)    
    client.send(response)
    client.close()
    
    print "Served one request/connection!"
    print

# We will never actually get here.
# Close the listening socket
sock.close()
