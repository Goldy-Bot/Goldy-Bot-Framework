from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict
    from typing_extensions import Self
    from discord_typings import InteractionData

    from ...commands import Command
    from ...typings import GoldySelfT

from devgoldyutils import LoggerAdapter, Colours

from ...logger import goldy_bot_logger
from ...commands import CommandType
from ...errors import FrontEndError
from ...objects.platter import Platter

__all__ = (
    "Commands",
)

logger = LoggerAdapter(
    goldy_bot_logger, prefix = "Commands"
)

class Commands():
    """Brings valuable methods to the goldy class for managing loading and syncing of commands."""
    def __init__(self) -> None:
        super().__init__()

    async def invoke_command(self: GoldySelfT[Self], name: str, type: CommandType, data: InteractionData) -> bool: 
        """Invokes a goldy bot command. Returns False if command is not found."""
        for extension in self.extensions:

            for _class in extension._classes:

                for command in extension._commands[_class.__class__.__name__]:

                    if command.name == name and command.payload["type"] == type.value:
                        self.logger.info(
                            f"Invoking the command '{command.name}' in extension class '{_class.__class__.__name__}'..."
                        )

                        platter = Platter(data, self)
                        params = self.__interaction_data_to_params(data, command)

                        try:
                            await command.function(_class, platter, **params) # TODO: Pass slash option arguments.

                        except FrontEndError as e:
                            self.__send_front_end_error(e) # TODO: Complete these.
                            raise e

                        except Exception as e:
                            self.__send_unknown_error(e)
                            raise e

                        return True

        return False

    async def _sync_commands(self: GoldySelfT[Self]) -> None:
        """
        Registers all the commands from each extension in goldy bot's internal state with discord if not registered already.
        Also removes commands from discord that are no longer registered within the framework.
        """
        commands_to_register: List[Command] = []

        for extension in self.extensions:

            for commands in extension._commands.values():
                commands_to_register.extend(commands)

        test_guild_id = self.config.test_guild_id

        # TODO: get applications commands from discord and check if all of them have been added. If not create them again.

        registered_commands = await self.create_application_commands(
            payload = [command.payload for command in commands_to_register], 
            guild_id = test_guild_id
        )

        logger.info(
            Colours.GREEN.apply(str(len(registered_commands))) + " command(s) have been registered with discord!"
        )

    def __interaction_data_to_params(self, data: InteractionData, command: Command) -> Dict[str, str]:
        """A method that phrases option parameters from interaction data of a command."""
        logger.debug(
            f"Phrasing interaction data options into function parameters for command '{command.name}'..."
        )

        params = {}

        for option in data["data"].get("options", []):

            # Ignore sub commands and sub groups.
            if option["type"] == 1 or option["type"] == 2: 
                continue

            for key in command._slash_options:
                slash_option = command._slash_options[key]

                if slash_option.data["name"] == option["name"]:
                    params[key] = option["value"]
                    logger.debug(f"Command argument '{key}' found!")
                    break

        return params