#!/usr/bin/python

import socket, os, urllib2, urllib

class Bot:
    ''' A Python IRC bot to connect to take cut and paste C source code
        and run a splint analysis on it and return the output '''

    #class variables
    socket = None
    server = ''
    nickname = ''
    channel = ''
    devKey = '979a06e7d12ca94a785b474c8e89d626'#enter your pastebin developer key here

        
    def __init__(self, server, channel, nickname):
        ''' A function to intialize the bot and connect to the server
            and begin reading to stream '''

        self.server   = server
        self.channel  = channel
        self.nickname = nickname

        self.ConnectToServer()
        self.ReadStream()


    def ReadStream(self):
        ''' a function to continuously read the stream and 
            and execute commands as required. This function runs 
            as long as the bot is alive '''

        while self.socket != None:#while the bot is connected
            buffer = self.socket.recv(2096)#read the socket's stream
            self.AnalyzeMessage(buffer)#anaylyze what was read


    def AnalyzeMessage(self, buffer):

        lines = buffer.split("\n")

        for line in lines:
            line = str(line).strip()

            arguments = line.split(None, 3)
            try:
                message   = arguments[3][1:]#see if there is a valid message send to the channel
            except:
                #probably just reading the messages from the server
                pass

            if line == '' or len(arguments) != 4:#if it's an empty line, skip it
                continue

            self.CheckCommand(message)


    def PostHelpMessage(self):
        ''' a function to post the help message when the user uses the !help command '''

        message = 'Type !splint followed by a pastebin link to run splint on C code, or !join followed by a channel to have me join a new channel'
        self.socket.send("PRIVMSG %s %s\r\n" % (self.channel, message))#print the response to the channel

    def CheckCommand(self, message):
        ''' a function to check if the user has entered
            a valid command and then execute it '''
        
        command = message.split(' ')#split the users input incase they entered an argument

        if command[0] == '!splint':#run splint
            print "Running Splint..."
            url = command[1]
            self.PutCodeIntoFile(url)
        elif command[0] == '!help':#give user some helpful informaton
            print 'Helping...'
            self.PostHelpMessage()
        elif command[0] == '!join':#join a new channel
            self.channel = command[1]
            self.JoinChannel()
        elif command[0] == '!q':#quit 
            print 'Quitting...'
            self.socket = None#set the socket to None and the bot will shut down
            return 4



    def PutCodeIntoFile(self, link):
        ''' function to get the paste code from pastebin
            and store it in a text file on the computer '''

        print "We have a splint user!"

        paste = link.split('pastebin.com/')[1] #get the paste code
        url   = 'http://pastebin.com/raw.php?i='+paste

        code  = urllib2.urlopen(url)#open the URL
        code  = code.read()#read the URL
        
        file = open('source.c','w+')#open a file to writet o
        file.write(code)#write the code to a file
        file.close()#close the file stream

        #execute splint from the command line and direct the
        #output to a file called output.txt
        os.system('splint source.c > output.txt')

        #read the output and post it to pastebin
        file = open('output.txt','r')
        output = file.read()
        self.PostToPasteBin(output)
        file.close()#close the file
        

    def PostToPasteBin(self, output):
        ''' functon to post the resulting output of splint 
            to a paste on pastebin '''

        #initialize all the pastebin API information
        postLink = 'http://pastebin.com/api/api_post.php'
        pastebin_vars = { 
                            'api_dev_key'    : self.devKey,
                            'api_option'     : 'paste',
                            'api_paste_code' : output
                        }
        #open a URL to the pastebin API and post the required information
        response = urllib2.urlopen(postLink,urllib.urlencode(pastebin_vars))
        url = response.read()#get the response
        self.socket.send("PRIVMSG %s %s\r\n" % (self.channel, url))#print the response to the channel
        print url#print the response to the command line

    def ConnectToServer(self):
        ''' a function to be ran as soon as the bot is initialized
            to create a socket to the server connect to it '''
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create the socket
            self.socket.connect((self.server, 6667))#connect to the socket

            print "Connected to:", self.server #we are connected

            #verify bot
            self.socket.send('PASS *********\r\n')
            self.socket.send('USER %s %s %s :Python IRC\r\n' % (self.nickname, self.nickname, self.nickname))
            self.socket.send('NICK %s\r\n' % self.nickname)

            self.JoinChannel()#connect to the room

        except Exception as e:#an error occured
            print e.message, e.args#print the error for debugging


    def JoinChannel(self):
        ''' a function to join a specified channel ''' 
        self.socket.send('JOIN ' + self.channel + '\r\n')
        print "Joined:", self.channel

            
#join the specified server, channel, and use the nickname
server = 'tigger.pearlstein.ca'
channel = '#test'
nickname = 'SplintMe'
bot = Bot(server, channel, nickname)


