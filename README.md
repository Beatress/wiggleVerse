# wiggleVerse
## A terminal based IRC client to have wiggly discussions of great import

## About
wiggleVerse is a single-server, single-window terminal-based IRC client built using only the Python standard library. It should run on any POSIX compliant operating system (macOS, Linux, BSD) that has a modern installation of Python. It was developed and tested using Python 3.9.1, but it should work with 3.7 or higher. It has not been tested on Windows at all and this usage should be considered unsupported.

## Video Demo
A video demo is now available [here](https://www.youtube.com/watch?v=6hQLUfXr64g) as presented to Ada Academy!

## Installation
* Simply `git clone` and `python3 wiggleVerse.py`. 
* Alternately, on macOS, you can do `chmod u+x wiggleVerse.py` and `./wiggleVerse.py`

## Commands
### Connecting and disconnecting

```
/connect <host> [port] - Connects to the server using client settings for nick, user, real
Port 6667 is the default port if none given
/disconnect - Disconnects from server
/reconnect - Reconnects to the last server connected to
/quit - Quits program
```

### Chatting
As this is a single window client, all messages from all channels will appear in one window. A user can message any channel or user using the `/msg` command. In addition, if a user types a message without any command, it will be sent to the default target. The default target can be changed with the `/switch` command manually. Also, when joining a channel or using the `/msg` command manually the default target is automatically changed for convenience.

```
/switch - Change the default target to which messages without a slash are sent
NOTE: default target is changed on joining channel/using /msg manually
/msg <recipient> <message> - Sends a message to recipient
```

### IRC Commands
For ease of use, aliases are provided for the most common commands. Any commands not implemented can be sent directly to the server using `/raw`

```
/raw <text> - Sends <text> to IRC server without processing
/list - Shows a list of available channels
/names [channel] - Shows a list of names in the channel, or in the server if none given 
/whois <nickname> - Shows information about the user
/nick <newnick> - Change your nickname
/join #<channel> - Join channel
/part #<channel> - Part channel
/topic #<channel> - Get channel topic
```

### Settings and Help
For convenience, the default user name, nickname, and 'real' name sent to the IRC server on connection are stored in a settings file `settings.json`. They can be modified using the following commands. If a settings file is not found, it will be created.
```
/set - See all the settings
/set <setting> - See the value for one setting
/set <setting> <value> - Change a setting
/help - See a basic help message
```

## Program Structure
The main entry point is `wiggleVerse.py`. This stub initiates logging, creates a Client object, and waits for a quit signal from the Client to cleanly close. It also uses the curses wrapper to easily set up and tear down the `curses` library for terminal interactivity

From here on, the following classes are used:
```
Client - Initializes a Screen, IRC, Settings, CommandParser, and ServerParser class. Controls the whole show!
CommandParser - Parses the commands that the user types
Exceptions - Common file that defines some custom exceptions
IRC - Controls the connection to an IRC network
IRCSocket - Handles some lower level implementation details
Screen - Handles all input and output on the terminal
Settings - Controls setting, reading, and saving of user settings
ServerParser - Formats incoming messages from the IRC server
```

As of current, too much functionality is in the Client class. A future refactor would move more of it to the IRC class. This would be greatly helpful before trying to implement multiple server support.

## Known bug
This application causes a small display bug in the terminal that it's ran in after `/quit` - you can close and reopen the terminal, or just type `reset` to fix it

## Future Features
This is a rather bare bones client created as a capstone project for my software development academy. There are many features that I would have liked to develop, including but not limited to:
* SSL support
* Multiple server support
* Multiple window support
* Support for all IRC functions
* Better handling of incoming messages (/me, colors, QUIT, etc)
* User selection of color theme

Future development of this software is pending more free time.

## License
wiggleVerse is licensed under the GNU GPLv2 and can be used in software licensed under the same or any later version. See the file COPYING for details.

## Credits
* Thanks to [Mackenzie Weber](https://github.com/MWeberLambdaweb19) and Vespurr for testing
* Thanks to Jupiter for unending cuteness
* Thanks to Ada Academy for making me an amazing programmer!
* Thanks to Chad Steadman for the very clearly written [IRCSocket class](https://github.com/chad-steadman/python-irc-client/blob/master/ircsocket.py), which I used as an initial guide
