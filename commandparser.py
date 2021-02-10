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
            opt_args = ['quit', 'disconnect', 'easter', 'list', 'reconnect']
            one_arg = ['raw', 'whois', 'nick', 'join', 'part']
            if opt_args.count(first_word) == 1:
                return (first_word, ' '.join(words[-len(words)+1:]))
            elif one_arg.count(first_word) == 1:
                try: 
                    return (first_word, ' '.join(words[1:]))
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
                    logging.debug(words)
                    return (first_word, words[1], int(words[2]))
                else:
                    return ('error', f'{first_word}: Incorrect number of arguments given')
            else:
                return ('error', f'{first_word}: No such command')