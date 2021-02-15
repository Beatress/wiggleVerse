import logging

class CommandParser:
    def __init__(self):
        pass

    def parse_command(self, command):
        if command[0] != '/':
            # This is an attempted PRIVMSG attempt to the default channel
            return ('no_slash', command)
        else: # This is an attempted client command
            command = command[1:] # Remove the slash
            words = command.split(' ')
            first_word = words[0]
            opt_args = ['quit', 'disconnect', 'easter', 'list', 'reconnect', 'names']
            one_arg = ['raw', 'whois', 'nick', 'join', 'part', 'topic', 'switch']
            if opt_args.count(first_word) == 1:
                return (first_word, ' '.join(words[-len(words)+1:]))
            elif one_arg.count(first_word) == 1:
                try:
                    if first_word == 'raw':
                        return (first_word, ' '.join(words[1:]))
                    else:
                        return (first_word, words[1])
                except IndexError:
                    return ('error', f'{first_word}: Incorrect number of arguments given')
            elif first_word == 'msg':
                try:
                    return (first_word, words[1], ' '.join(words[2:]))
                except IndexError:
                    return ('error', f'{first_word}: Incorrect number of arguments given')
            elif first_word == 'connect':
                if len(words) == 2:
                    return (first_word, words[1], 6667) # Default port
                elif len(words) == 3:
                    try:
                        return (first_word, words[1], int(words[2]))
                    except ValueError:
                        return ('error', 'Connect: Non numeric port number given')
                else:
                    return ('error', f'{first_word}: Incorrect number of arguments given')
            elif first_word == 'set':
                if len(words) == 1: # get settings
                    return ('getset', 'all')
                elif len(words) == 2: # get a setting
                    return ('getset', words[1])
                elif len(words) == 3: # set a setting
                    return ('setset', words[1], words[2])
                else:
                    return ('error', 'Set: incorrect paramters')
                    
            else:
                return ('error', f'{first_word}: No such command')