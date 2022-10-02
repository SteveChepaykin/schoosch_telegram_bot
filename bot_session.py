class BotSession:
    counter: int = 0
    state: str = 'default'

    def process_input(self, input: str, **kwargs) -> str:
        if self.state == 'default':
            self.counter += 1
            if self.counter == 5:
                self.counter = 0
                return 'sendHelpReminder'
        elif self.state == 'waitname':
            if len(input.split(' ')) == 3:
                self.counter = 0
                self.state = 'default'
                return 'getlogin'
            else:
                self.counter += 1
                if self.counter == 2:
                    self.state = 'default'
                    self.counter = 0
                    return 'sendWrongName'
                else:
                    return 'sendNameReminder'

    def process_login(self) -> str:
        self.counter = 0
        self.state = 'waitname'
        return 'sendWaitLogin'

    def process_command(self, command: str, **kwargs) -> str:
        if command == 'input':
            return self.process_input(kwargs['input'], kwargs)
        if command == 'login':
            return self.process_login()
        if command == 'help':
            return 'getHelp'
        if command == 'tutorial':
            return 'getTutorial'
        if command == 'contact':
            return 'getContact'