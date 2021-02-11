import random
import queue
import curses
import sys
import logging
import screen
import threading
import time

from irc import Irc
from ircsocket import IrcSocket
from screen import Screen
from serverparser import ServerParser
from commandparser import CommandParser
from exceptions import *
from settings import Settings

class Client:
    """This is the main class of the program
    Each execution of the program will have only one client
    Each client has one screen and zero or more IRC classes"""

    def parse_messages(self):
        while 1:
            message = self.buffer.get() # Blocks until new message comes in
            
            if message == '[wiggleVerse] DROPCON': # signal from received thread that we have lost connection
                self.default_target = None
                self.connected = False
                continue
            self.screen.put_line(self.server_parser.parse_message(message))

    def try_send_raw(self, text):
        try:
            self.irc.send_raw(text)
        except OSError as err:
            logging.warning(err)
            self.default_target = None
            self.reset_state()
            self.connected = False

    def do_command(self, line):
        """This is a call back for screen
        It executes the command the user typed
        
        SUPPORTED COMMANDS:
        /disconnect - Disconnects from server
        /reconnect - Reconnects to the last server connected to
        /connect <host> [port] - Connects to the server using client settings for nick, user, real
        /quit [message] - Quits program with quit message [message] # TODO implement quit message
        /easter - Egg
        /raw <text> - Sends <text> to IRC server without processing
        /msg <recipient> <message> - Sends a message to recipient
        /list - Shows a list of available channels
        /names [channel] - Shows a list of names in the channel, or in the server if none given 
        /whois <nickname> - Shows information about the user
        /nick <newnick> - Change your nickname
        /join #<channel> - Join channel
        /part #<channel> - Part channel        
        """
        if line == '':
            return None

        parsed_command = self.command_parser.parse_command(line) # Returns a tuple
        if parsed_command[0] == 'disconnect':
            if self.connected and self.irc.is_connected():
                logging.info(f'[Client] User requested disconnect with message {parsed_command[1]}')
                self.irc.disconnect()
                self.connected = False
                self.reset_state()
                self.screen.put_line('>>Disconnected')
            else:
                self.screen.put_line('>>You are not connected')

        elif parsed_command[0] == 'reconnect':
            if not self.connected and not self.irc.is_connected():
                self.irc.connect()
                if not self.irc.is_connected():
                    self.screen.put_line('>>Connection not successful')
                    self.connected = False
                else:
                    self.connected = True

        elif parsed_command[0] == 'connect':
            self.screen.put_line('>>Attemping to connect...')

            self.irc = Irc(parsed_command[1], parsed_command[2], 
            self.nick, self.user, self.real, self.parse_messages, self.buffer)
            self.irc.connect()
            # TODO support alternate nick
            if not self.irc.is_connected():
                self.screen.put_line('>>Connection not successful')
                self.connected = False
            else:
                self.connected = True

        elif parsed_command[0] == 'quit':
            logging.info('[Client] User requested quit')
            if self.connected and self.irc.is_connected():
                logging.info(f'[Client] User requested disconnect with message {parsed_command[1]}')
                self.irc.disconnect()
                self.connected = False
            self.quit_signal.set() # Signals to main thread to quit

        elif parsed_command[0] == 'easter':
            self.screen.put_line(">>egg")

        elif parsed_command[0] == 'raw':
            self.try_send_raw(parsed_command[1])

        elif parsed_command[0] == 'msg':
            self.try_send_raw(f'PRIVMSG {parsed_command[1]} :{parsed_command[2]}')

        elif parsed_command[0] == 'list':
            self.try_send_raw(f'LIST')

        elif parsed_command[0] == 'whois':
            self.try_send_raw(f'WHOIS {parsed_command[1]}')

        elif parsed_command[0] == 'names':
            if parsed_command[1] == '':
                self.try_send_raw(f'NAMES *')
            else:
                self.try_send_raw(f'NAMES {parsed_command[1]}')

        elif parsed_command[0] == 'nick':
            self.try_send_raw(f'NICK {parsed_command[1]}')

        elif parsed_command[0] == 'join':
            self.try_send_raw(f'JOIN {parsed_command[1]}')

        elif parsed_command[0] == 'part':
            self.try_send_raw(f'PART {parsed_command[1]}')

        elif parsed_command[0] == 'no_slash':
            if self.default_target == None:
                self.screen.put_line('>>No default target set')
            else:
                self.irc.try_send_raw(f'PRIVMSG {self.default_target} :{line}')

        elif parsed_command[0] == 'error':
            self.screen.put_line('>>' + parsed_command[1])

        else:
            self.screen.put_line(f'>>Unknown error parsing command: {line}')

    def reset_state(self):
        self.default_target = None
        self.nick = self.settings.get('nick') or 'Wiggler' + str(random.randint(111,999))
        self.user = self.settings.get('user') or 'wiggler'
        self.real = self.settings.get('real') or 'A Very Cool Wiggler!'

    def __init__(self, screenObj, quit_signal):
        """Initialize all the things the client will need to control the entire user session"""
        # initialize screen
        self.screen = Screen(screenObj, self.do_command)
        self.screen.draw_screen()
        # Start listening for messages in the buffer
        self.buffer = queue.SimpleQueue()
        self.parse_message_thread = threading.Thread(target=self.parse_messages, daemon=True)
        self.parse_message_thread.start()
        # We are passed a signal to quit the program
        self.quit_signal = quit_signal
        # Initialize various helper classes
        self.settings = Settings()
        self.server_parser = ServerParser()
        self.command_parser = CommandParser()
        # Create state the client needs to track
        self.irc = False
        self.connected = False
        self.reset_state()
        self.screen.put_line('>>WWWelcome to the wwwiggleVerse!!!')
        # for _ in range (3):
        #     with open('test.txt') as f:
        #         for line in f.readlines():
        #             self.screen.put_line(line)