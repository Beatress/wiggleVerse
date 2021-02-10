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
            command = self.buffer.get() # Blocks until new message comes in
            self.screen.put_line(self.server_parser.parse_message(command))

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

        TODO: list, whois, nick, join, part

        
        """
        if line == '':
            return None

        parsed_command = self.command_parser.parse_command(line) # Returns a tuple
        if parsed_command[0] == 'disconnect':
            if self.irc and self.irc.is_connected():
                logging.info(f'[Client] User requested disconnect with message {parsed_command[1]}')
                self.irc.disconnect()
                self.screen.put_line('Disconnected')
            else:
                self.screen.put_line('You are not connected')

        elif parsed_command[0] == 'reconnect':
            if self.irc and not self.irc.is_connected():
                self.irc.connect()
                if not self.irc.is_connected():
                    self.screen.put_line('Connection not successful')      

        elif parsed_command[0] == 'connect':
            self.screen.put_line('>> Attemping to connect...')
            nick = self.settings.get('nick') or 'Wiggler' + str(random.randint(111,999))
            user = self.settings.get('user') or 'wiggler'
            real = self.settings.get('real') or 'A Very Cool Wiggler!'
            self.irc = Irc(parsed_command[1], parsed_command[2], 
            nick, user, real, self.parse_messages, self.buffer)
            self.irc.connect()
            # TODO support alternate nick
            if not self.irc.is_connected():
                self.screen.put_line('>> Connection not successful')

        elif parsed_command[0] == 'quit':
            logging.info('[Client] User requested quit')
            if self.irc and self.irc.is_connected():
                logging.info(f'[Client] User requested disconnect with message {parsed_command[1]}')
                self.irc.disconnect()
            self.quit_signal.set() # Signals to main thread to quit

        elif parsed_command[0] == 'easter':
            self.screen.put_line("egg")

        elif parsed_command[0] == 'raw':
            try:
                self.irc.send_raw(parsed_command[1])
            # except SocketTimeout:
            #     logging.warning('Socket timeout')
            except OSError as err:
                logging.warning(err)
            # except SocketNotConnected:
            #     logging.debug('socket not connected')

        elif parsed_command[0] == 'error':
            self.screen.put_line(parsed_command[1])

        elif parsed_command[0] == 'msg':
            self.irc.send_raw(f'PRIVMSG {parsed_command[1]} :{parsed_command[2]}')

        elif parsed_command[0] == 'no_slash':
            if self.default_target == None:
                self.screen.put_line('No default target set')
            else:
                self.irc.send_raw(f'PRIVMSG {self.default_target} :{line}')

        else:
            self.screen.put_line(f'Unknown error parsing command: {line}')

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
        self.default_target = None
        self.irc = False
        self.screen.put_line('WWWelcome to the wwwiggleVerse!!!')
        for _ in range (4):
            with open('test.txt') as f:
                for line in f.readlines():
                    self.screen.put_line(line)