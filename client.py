# Copyright Beatrice Tohni 2021
""" This file is part of wiggleVerse.

    wiggleVerse is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    wiggleVerse is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with wiggleVerse.  If not, see <https://www.gnu.org/licenses/>."""

import random
import queue
import curses
import sys
import logging
import screen
import threading
import time
import os.path

from time import strftime
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

    def set_nick(self, new_nick):
        self.nick = new_nick
        self.set_status()

    def set_status(self):
        connected = "Yes" if self.connected else 'No'
        time = strftime('%H:%M')
        self.screen.set_status(f'[{time}] Connected:{connected} Nick:{self.nick} Target:{self.default_target}')

    def parse_messages(self):
        while 1:
            message = self.buffer.get() # Blocks until new message comes in
            self.set_status()
            
            if message == '[wiggleVerse] DROPCON': # signal from received thread that we have lost connection
                self.default_target = None
                self.connected = False
                continue
            self.screen.put_line(self.server_parser.parse_message(message))

    def try_send_raw(self, text):
        try:
            if self.irc:
                self.set_status()
                self.irc.send_raw(text)
            else:
                self.screen.put_line('>>Not connected')
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
        /quit - Quits program
        /easter - Egg
        /raw <text> - Sends <text> to IRC server without processing
        /switch - Change the default target to which messages without a slash are sent
        NOTE: default target is changed on joining channel/using /msg manually
        /msg <recipient> <message> - Sends a message to recipient
        /list - Shows a list of available channels
        /names [channel] - Shows a list of names in the channel, or in the server if none given 
        /whois <nickname> - Shows information about the user
        /nick <newnick> - Change your nickname
        /join #<channel> - Join channel
        /part #<channel> - Part channel
        /topic #<channel> - Get channel topic
        /set - see all the settings
        /set <setting> - see the value for one setting
        /set <setting> <value> - change a setting
        /help - see this help message
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
            if not self.connected:
                self.irc.connect()
                if not self.irc.is_connected():
                    self.screen.put_line('>>Connection not successful')
                    self.connected = False
                else:
                    self.connected = True
            else:
                self.screen.put_line('>>You are already connected')

        elif parsed_command[0] == 'connect':
            if not self.connected:
                self.screen.put_line('>>Attemping to connect...')
                self.screen.put_line('>>Timeout is 30 seconds.')

                self.irc = Irc(parsed_command[1], parsed_command[2], 
                self.nick, self.user, self.real, self.parse_messages, self.buffer)
                self.irc.connect()

                if not self.irc.is_connected():
                    self.screen.put_line('>>Connection not successful')
                    self.connected = False
                else:
                    self.connected = True
                    logging.info('[Client] Successfully connected')
            else:
                self.screen.put_line('>>You are already connected')

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

        elif parsed_command[0] == 'switch':
            self.default_target = parsed_command[1]

        elif parsed_command[0] == 'msg':
            self.try_send_raw(f'PRIVMSG {parsed_command[1]} :{parsed_command[2]}')
            self.default_target = parsed_command[1]
            self.set_status()
            self.screen.put_line(f'-{parsed_command[1]}- <{self.nick}> {parsed_command[2]}')

        elif parsed_command[0] == 'list':
            self.try_send_raw(f'LIST')

        elif parsed_command[0] == 'whois':
            self.screen.put_line(f'*** WHOIS info for {parsed_command[1]} ***')
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
            self.default_target = parsed_command[1]
            self.try_send_raw(f'TOPIC {parsed_command[1]}')

        elif parsed_command[0] == 'part':
            self.try_send_raw(f'PART {parsed_command[1]}')
            if parsed_command[1] == self.default_target:
                self.default_target = None

        elif parsed_command[0] == 'topic':
            self.try_send_raw(f'TOPIC {parsed_command[1]}')

        elif parsed_command[0] == 'no_slash':
            if self.default_target == None:
                self.screen.put_line('>>No default target set')
            else:
                self.try_send_raw(f'PRIVMSG {self.default_target} :{line}')
                self.screen.put_line(f'-{self.default_target}- <{self.nick}> {line}')

        elif parsed_command[0] == 'getset':
            if parsed_command[1] == 'all':
                strings = self.settings.get_all()
                for line in strings:
                    self.screen.put_line('>>' + line)
            else:
                result = self.settings.get(parsed_command[1])
                if result:
                    self.screen.put_line(f'>>{parsed_command[1]}: {result}')
                else:
                    self.screen.put_line(f'>>{parsed_command[1]}: No such setting')

        elif parsed_command[0] == 'setset':
            result = self.settings.put(parsed_command[1], parsed_command[2])
            if result:
                self.screen.put_line(f'>>Set {parsed_command[1]} to {result}')
                # if we are not connected, reset state for settings to take effect
                if not self.irc:
                    self.reset_state()
            else:
                self.screen.put_line(f'>>No such setting {parsed_command[1]}')

        elif parsed_command[0] == 'version':
            self.screen.put_line('*** wiggleVerse version 0.39 ***')
            self.screen.put_line('This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version.')
            self.screen.put_line('This program is distributed in the hope that it will be useful,but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.')
            self.screen.put_line('You should have received a copy of the GNU General Public License (as COPYING) along with this program.  If not, see <https://www.gnu.org/licenses/>.')

        elif parsed_command[0] == 'help':
            if os.path.isfile('HELP'):
                self.screen.put_line('*** wiggleVerse help ***')
                with open('HELP') as f:
                    for line in f.readlines():
                        self.screen.put_line(line)
            else:
                self.screen.put_line('>>HELP file missing! Check README.md')

        elif parsed_command[0] == 'error':
            self.screen.put_line('>>' + parsed_command[1])

        else:
            self.screen.put_line(f'>>Unknown error parsing command: {line}') 

        self.set_status()
        
    def reset_state(self):
        self.default_target = None
        self.nick = self.settings.get('nick') or 'Wiggler' + str(random.randint(111,999))
        self.user = self.settings.get('user') or 'wiggler'
        self.real = self.settings.get('real') or 'A Very Cool Wiggler!'
        self.set_status()

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
        self.command_parser = CommandParser()
        # Create state the client needs to track
        self.irc = False
        self.connected = False
        self.reset_state()
        # This needs to be done after reset_state()
        self.server_parser = ServerParser(self.nick, self.set_nick)
        self.screen.put_line('>>WWWelcome to the wwwiggleVerse!!!')
        self.screen.put_line('>>This is free software, type /version for details')
        # for _ in range (3):
        #     with open('test.txt') as f:
        #         for line in f.readlines():
        #             self.screen.put_line(line)