
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from robot.api.deco import keyword, not_keyword, library
from ..librarycomponent import LibraryComponent


class FieldCommand(LibraryComponent):

    def __init__(self, library):
        super().__init__(library)

        self.field_commands = {
            'var': self.command_var
        }

    @keyword
    def test_field_command(self):
        logger.info("TEST MIJN KEYWORD")

    @not_keyword
    def command_var(self, *args):
        print(f"*DEBUG* COMMAND VAR args: {args}")
        value = BuiltIn().get_variable_value(args[0])
        return value

    @keyword(tags=('Apex', 'FieldCommands'))
    def register_field_commands(self, **commands_to_register):
        """Register fields commands.

        Field commands are used when filling or checking fields inside regions.
        When the value starts with ``$``, ``!`` or ``&`` the registered keyword will be called.

        The keywords should expect an array of values and should return a value.

        Example of generating a random string:
        | Generate text
        |     [Arguments]    ${nr_of_chars}    @args
        |     ${text}=    Generate Random String    ${nr_of_chars}    [LETTERS]
        |     RETURN    ${text}

        Register the function:
        | Default Suite Setup
        |     Register Field Commands
        |     ...    generatetext=Generate text

        Now it can be used for filling:
        |    Some region fill
        |    ...    text=$generatetext:10
        (``Some region fill`` is a wrapper arround one of the Apex Fill keywords: `Block Fill`, `Tab Fill`, `Tab Subregion Fill`)

        The value part will be split on ``:`` and passed to the registed function. In this case: ``['10']``
        """
        if type(commands_to_register) is not dict:
            raise AttributeError(f"Register Field Commands expect a dictionary as argument")

        self.field_commands.update(commands_to_register)
        print(f"*INFO* Test")

    @not_keyword
    def process_command(self, value):
        if type(value) is not str:
            return value
        
        used_value = None
        if value[0] in ['&', '!', '$']:
            args = value[1:].split(':')
            cmd_name = args.pop(0)
            logger.info(f"Command: {cmd_name}  args: {args}")
            if cmd_name in self.field_commands:
                cmd = self.field_commands[cmd_name]
                if type(cmd) is str:
                    # run as keyword
                    used_value = BuiltIn().run_keyword(cmd, *args)

                else:
                    # run as function
                    used_value = cmd(*args)

            else:
                raise AttributeError(f"Field command `{cmd_name}` not found")
            logger.info(f"Command: {cmd_name}  returned: {used_value}")

        else:
            used_value = value

        return used_value