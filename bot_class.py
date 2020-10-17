from fbchat import log, Client
from fbchat.models import *
import random
import datetime
import time
import pickle


class MessageBot(Client):
    def __init__(self, email, password, session_cookies):
        Client.__init__(self, email, password, session_cookies=session_cookies)
        self.cur_version = 'v0.3-Alpha'
        self.cur_dm = '0'   # For the DnD features, the current DM(Dungeon Master)
        self.current_rule = 'coc'   # The current rule for stat rolls (dnd/coc)
        try:
            # An alias is a way for the bot to refer to users while executing certain commands
            # An alias can be set by the user with the command !setalias <alias>
            # The format of the alias is as a dictionary where the key is the alias and value is the user_id
            with open('aliases.dat', 'rb') as alias_data:
                self.alias_data = pickle.load(alias_data)
        except FileNotFoundError:
            with open('aliases.dat', 'wb') as alias_data:
                self.alias_data = {}
                pickle.dump(self.alias_data, alias_data)
        try:
            # This file holds all the other random data thats saved by the bot
            with open('bot_data.dat', 'rb') as data:
                self.cur_dm = pickle.load(data)
        except FileNotFoundError:
            with open('bot_data.dat', 'wb') as data:
                self.cur_dm = '0'
                pickle.dump(self.cur_dm, data)
        try:
            with open('player_stats.dat', 'rb') as stats_data:
                self.stats_data = pickle.load(stats_data)
        except FileNotFoundError:
            with open('player_stats.dat', 'wb') as stats_data:
                self.stats_data = {}
                pickle.dump(self.stats_data, stats_data)

    def onMessage(self, author_id, message, message_object, thread_id, thread_type, **kwargs):
        # Only respond to messages with the '!' symbol
        if str(message_object.text)[0] == '!':
            user = self.fetchUserInfo(author_id)[f"{author_id}"]
            log.info(f"Attempting to respond to {user.name}: {message_object.text}")
            command = str(message_object.text.lower()).split(' ')
            main_command = command[0][1:]
            if main_command == 'version':
                self.sendMessage(self.cur_version, thread_id, thread_type)

            elif main_command == 'setalias':
                if len(command) > 1:
                    if command[1] != " " and command[1] not in self.alias_data.keys():
                        alias = command[1]
                        self.alias_data[alias.lower()] = author_id
                        with open('aliases.dat', 'wb') as alias_data:
                            pickle.dump(self.alias_data, alias_data)
                        self.send(Message(text=f'@{user.name} alias set to {alias.capitalize()}!', mentions=[Mention(thread_id, offset=0, length=len(user.name)+1)]), thread_id=thread_id, thread_type=thread_type)
                    else:
                        self.send(Message(text=f'@{user.name} That is an invalid alias(or an already existing one)!', mentions=[Mention(thread_id, offset=0, length=len(user.name)+1)]), thread_id=thread_id, thread_type=thread_type)

            elif main_command == 'clearalias':
                if len(command) > 1:
                    if command[1] in self.alias_data.keys():
                        if self.alias_data[command[1]] == author_id:
                            del self.alias_data[command[1]]
                            self.send(Message(text=f'@{user.name} Removed alias {command[1].capitalize()}!',
                                              mentions=[Mention(thread_id, offset=0, length=len(user.name) + 1)]),
                                      thread_id=thread_id, thread_type=thread_type)
                            with open('aliases.dat', 'wb') as alias_data:
                                pickle.dump(self.alias_data, alias_data)
                        else:
                            self.send(Message(text=f'@{user.name} That\'s not your alias!',
                                              mentions=[Mention(thread_id, offset=0, length=len(user.name) + 1)]),
                                      thread_id=thread_id, thread_type=thread_type)
                    else:
                        self.send(Message(text=f'@{user.name} That alias does not exist.',
                                          mentions=[Mention(thread_id, offset=0, length=len(user.name) + 1)]),
                                  thread_id=thread_id, thread_type=thread_type)

            elif main_command == 'setdm':
                if len(command) != 2:
                    self.send(Message(text=f'@{user.name} Invalid format. !setdm <alias>',
                                      mentions=[Mention(thread_id, offset=0, length=len(user.name) + 1)]),
                              thread_id=thread_id, thread_type=thread_type)
                else:
                    if command[1] not in self.alias_data.keys():
                        self.send(Message(text=f'@{user.name} That alias does not exist!', mentions=[Mention(thread_id, offset=0, length=len(user.name)+1)]), thread_id=thread_id, thread_type=thread_type)
                    else:
                        self.cur_dm = self.alias_data[command[1]]
                        user = self.fetchUserInfo(self.cur_dm)[f"{self.cur_dm}"]
                        self.send(Message(text=f'@{user.name} is now the DM!', mentions=[Mention(thread_id, offset=0, length=len(user.name)+1)]), thread_id=thread_id, thread_type=thread_type)

            elif main_command == 'displayaliases':
                aliases = ""
                for key in self.alias_data:
                    user = self.fetchUserInfo(self.alias_data[key])[f"{self.alias_data[key]}"]
                    aliases += f"{key} - {user.name}\n"
                self.sendMessage(f"The current aliases are:\n{aliases}", thread_id, thread_type)

            elif main_command == 'roll':
                upper_limit = 6
                dice = 0
                if len(command) == 1:
                    dice = random.randrange(1, upper_limit + 1)
                else:
                    if command[1][0] == 'd':
                        try:
                            upper_limit = int(command[1][1:])
                            dice = random.randrange(1, upper_limit + 1)
                        except ValueError:
                            upper_limit = 6
                            dice = random.randrange(1, upper_limit + 1)
                self.send(Message(text=f'@{user.name} Rolled {dice}!🎲(d{upper_limit})', mentions=[Mention(thread_id, offset=0, length=len(user.name)+1)]), thread_id=thread_id, thread_type=thread_type)

            elif main_command == 'blindroll':
                if len(command) == 2:
                    upper_limit = 6
                    dice = random.randrange(1, upper_limit + 1)
                else:
                    if command[2][0] == 'd':
                        try:
                            upper_limit = int(command[2][1:])
                            dice = random.randrange(1, upper_limit + 1)
                        except ValueError:
                            upper_limit = 6
                            dice = random.randrange(1, upper_limit + 1)
                if len(command) <= 3:
                    if command[1] in self.alias_data.keys():
                        user = self.fetchUserInfo(self.alias_data[command[1]])[f"{self.alias_data[command[1]]}"]
                        self.send(Message(text=f'@{user.name} Rolled {dice}!🎲(d{upper_limit})',
                                          mentions=[Mention(author_id, offset=0, length=len(user.name) + 1)]),
                                  thread_id=author_id, thread_type=ThreadType.USER)
                elif len(command) == 4:
                    if command[1] in self.alias_data.keys() and command[3] in self.alias_data.keys():
                        user = self.fetchUserInfo(self.alias_data[command[1]])[f"{self.alias_data[command[1]]}"]
                        self.send(Message(text=f'@{user.name} Rolled {dice}!🎲(d{upper_limit})',
                                          mentions=[Mention(self.alias_data[command[3]], offset=0, length=len(user.name) + 1)]),
                                  thread_id=self.alias_data[command[3]], thread_type=ThreadType.USER)

            elif main_command == 'setstat':
                if len(command) == 4:
                    if command[1] in self.alias_data.keys():
                        if self.alias_data[command[1]] not in self.stats_data.keys():
                            self.stats_data[self.alias_data[command[1]]] = {}
                        print(self.stats_data, command)
                        self.stats_data[self.alias_data[command[1]]][command[2]] = command[3]
                        self.send(Message(text=f'{command[1]} {command[2]} set to {command[3]}!'), thread_id=thread_id, thread_type=thread_type)
                        with open('player_stats.dat', 'wb') as stats_data:
                            pickle.dump(self.stats_data, stats_data)
                    else:
                        self.send(Message(text=f'@{user.name} That alias does not exist!', mentions=[Mention(thread_id, offset=0, length=len(user.name)+1)]), thread_id=thread_id, thread_type=thread_type)

            elif main_command == 'displaystats' or main_command == 'statsheet' or main_command == 'showstats':
                if len(command) == 2:
                    if command[1] in self.alias_data.keys():
                        if self.alias_data[command[1]] in self.stats_data.keys():
                            stats = f"{command[1].capitalize()}'s stats are:\n "
                            for stat in self.stats_data[self.alias_data[command[1]]]:
                                stats += f"{stat} : {self.stats_data[self.alias_data[command[1]]][stat]}\n"
                            self.sendMessage(f"{stats}", thread_id, thread_type)
                        else:
                            self.sendMessage(f"No stats yet!", thread_id, thread_type)
                    else:
                        self.send(Message(text=f'@{user.name} That alias does not exist!', mentions=[Mention(thread_id, offset=0, length=len(user.name)+1)]), thread_id=thread_id, thread_type=thread_type)

            elif main_command == 'statroll':
                if len(command) == 3:
                    if command[1] in self.alias_data.keys():
                        if command[2] in self.stats_data[self.alias_data[command[1]]].keys():
                            roll = random.randrange(1, 101)
                            result = ""
                            if roll == 100 or roll == 99:
                                result = "Critical Failure!"
                            elif roll == 1 or roll == 2:
                                result = "Spectacular Success!"
                            elif roll <= int(self.stats_data[self.alias_data[command[1]]][command[2]]):
                                result = "Success!"
                            else:
                                result = "Failure!"
                            self.sendMessage(f"{command[1].capitalize()} rolled {roll}! (d100) - {result}", thread_id, thread_type)
                        else:
                            self.sendMessage("Invalid stat!", thread_id, thread_type)
                    else:
                        self.send(Message(text=f'@{user.name} That alias does not exist!', mentions=[Mention(thread_id, offset=0, length=len(user.name)+1)]), thread_id=thread_id, thread_type=thread_type)




