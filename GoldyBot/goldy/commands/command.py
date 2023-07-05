from __future__ import annotations
from abc import abstractmethod
from typing import Callable, Any, List, Dict, TYPE_CHECKING
from discord_typings import ApplicationCommandOptionData

from devgoldyutils import LoggerAdapter, Colours

from ..extensions import extensions_cache
from ... import goldy_bot_logger, utils

from . import params_utils
from ..nextcore_utils import front_end_errors
from ..objects import Invokable

if TYPE_CHECKING:
    from ... import Goldy, Extension
    from .. import objects

class Command(Invokable):
    """Class that all commands in goldy bot inherit from."""
    def __init__(
        self, 
        goldy: Goldy, 
        func: Callable[[Extension, objects.GoldPlatter], Any], 
        name: str = None, 
        description: str = None, 
        required_roles: List[str] = None, 
        slash_options: Dict[str, ApplicationCommandOptionData] = None, 
        hidden: bool = False, 
        pre_register = True
    ):
        self.func = func
        """The command's callback function."""

        self.extension_name = str(self.func).split(" ")[1].split(".")[0]
        """Returns extension's code name."""

        if name is None:
            name = func.__name__

        if description is None:
            description = "Oops daisy, looks like no description was set for this command."

        if required_roles is None:
            self.__required_roles = []
        else:
            self.__required_roles = [str(role) for role in required_roles]

        if slash_options is None:
            self.__slash_options = {}
        else:
            self.__slash_options = slash_options

        self.__hidden = hidden

        self.__params = params_utils.get_function_parameters(self)

        self._is_loaded = False
        self.__is_disabled = False

        super().__init__(
            name, 
            {
                "name": name,
                "description": description,
                "options": params_utils.params_to_options(self),
                "default_member_permissions": str(1 << 3) if hidden else None,
                "type": 1
            }, 
            func,
            goldy, 
            LoggerAdapter(LoggerAdapter(goldy_bot_logger, prefix=self.__class__.__name__), prefix=Colours.PINK_GREY.apply(name)),
            pre_register
        )

    @property
    def name(self) -> str:
        """The command's code name."""
        return self.get("name")

    @property
    def description(self) -> str:
        """The command's set description. None if there is no description set."""
        return self.get("description")

    @property
    def required_roles(self):
        """The code names for the roles needed to access this command."""
        return self.__required_roles

    @property
    def slash_options(self):
        """Allows you to customize slash command arguments and make them beautiful 🥰."""
        return self.__slash_options

    @property
    def hidden(self):
        """Should this command be hidden? For slash commands the command is just set to admins only."""
        return self.__hidden
    
    @property
    def params(self) -> List[str]:
        """List of command function parameters."""
        return self.__params

    @property
    def extension(self) -> Extension | None:
        """Finds and returns the object of the command's extension. Returns None if the extension doesn't exits. (failed to load)"""
        return (lambda x: x[1] if x is not None else None)(
            utils.cache_lookup(self.extension_name, extensions_cache)
        )

    @property
    def is_loaded(self) -> bool:
        """Returns whether the command has been loaded by the command loader or not."""
        return self._is_loaded

    @property
    def is_disabled(self) -> bool:
        """Returns whether the command is disabled or not."""
        return self.__is_disabled

    def disable(self) -> None:
        """A method to disable this command."""
        self.__is_disabled = True
        self.logger.debug(Colours.GREY.apply("Command has been disabled!"))

    def enable(self) -> None:
        """A method to enable this command."""
        self.__is_disabled = False
        self.logger.debug(Colours.GREEN.apply("Command has been enabled!"))

    @abstractmethod
    def register_sub_command(self, command: Command) -> None:
        """
        Method that is called when a sub command want's to register.

        You must override this to handle it for your command type.
        """
        ...

    @abstractmethod
    async def invoke(self, platter: objects.GoldPlatter, lambda_func: Callable) -> None:
        self.logger.debug("Attempting to invoke command...")

        if platter.guild.is_extension_allowed(self.extension) is False:
            raise front_end_errors.ExtensionNotAllowedInGuild(platter, self.logger)

        if self.is_disabled:
            raise front_end_errors.CommandIsDisabled(platter, self.logger)

        # I'm using a lambda function here so all the parameter bullshit 
        # can be handled by the child class instead of this method.
        if await self.goldy.permission_system.got_perms(platter):
            self.logger.info(
                Colours.BLUE.apply(
                    f"Command invoked by '{platter.author.username}#{platter.author.discriminator}'."
                )
            )
            return await lambda_func() 

        # If member has no perms raise MissingPerms exception.
        raise front_end_errors.MissingPerms(platter, self.logger)