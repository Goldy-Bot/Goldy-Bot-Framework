"""
Theses are errors that report back to the front end. 
For example if a command is missing a parameter it will raise a FrontEndError which will report back the command user.
"""
import logging as log

from ... import errors
from ..nextcore_utils import Colours
from .embeds.embed import Embed
from ..objects.gold_platter import GoldPlatter

class FrontEndErrors(errors.GoldyBotError):
    def __init__(
            self, 
            title: str,
            description: str,
            message: str,
            platter: GoldPlatter, 
            embed_colour = Colours.AKI_ORANGE,
            logger: log.Logger = None
        ):

        platter.goldy.async_loop.create_task(
            platter.send_message(
                embeds = [
                    Embed(
                        title = title,
                        description = description,
                        colour = embed_colour
                    )
                ],
                reply = True
            )
        )

        super().__init__(message, logger)


class MissingArgument(FrontEndErrors):
    def __init__(self, missing_args: list, platter: GoldPlatter, logger: log.Logger = None):
        command_args_string = ""
        for param in platter.command.params:
            command_args_string += f"{{{param}}} "

        missing_args_string = ""
        for arg in missing_args:
            missing_args_string += f"{arg}, "

        super().__init__(
            title = "🧡 Oops, your missing an argument.", 
            description = f"""
*You missed the argument(s): ``{missing_args_string[:-2]}``*

**Command Usage -> ``!{platter.command.name} {command_args_string[:-1]}``**
""", 
            message = f"The command author missed the arguments -> '{missing_args_string[:-2]}'.",
            platter = platter, 
            logger = logger
        )


class TooManyArguments(FrontEndErrors):
    def __init__(self, platter: GoldPlatter, logger: log.Logger = None):
        command_args_string = ""
        for param in platter.command.params:
            command_args_string += f"{{{param}}} "

        super().__init__(
            title = "❤ You gave me too many arguments.", 
            description = f"""
**Command Usage -> ``!{platter.command.name} {command_args_string[:-1]}``**
""", 
            message = f"The command author passed too many arguments.",
            platter = platter, 
            embed_colour = Colours.RED,
            logger = logger
        )