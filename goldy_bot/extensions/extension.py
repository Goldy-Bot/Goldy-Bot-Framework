from __future__ import annotations
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from typing import List, Dict, Optional, Literal, Callable, Type

    from GoldyBot.goldy.nextcore_utils.slash_options.slash_option import SlashOption

    from ..goldy import Goldy

    ExtensionClassT = Callable[[Goldy], None]

from devgoldyutils import LoggerAdapter

from ..logger import goldy_bot_logger
from ..commands import GroupCommand, Command

__all__ = (
    "Extension",
)

class Extension():
    """Class to create an extension in 🥞 pancake."""
    def __init__(self, name: str) -> None:
        self.name = name

        self._classes: List[object] = []
        self._commands: Dict[str, List[Command]] = {}

        self.logger = LoggerAdapter(goldy_bot_logger, prefix = "Extension")

    def mount(self, goldy: Goldy, *cls: ExtensionClassT) -> None:
        """Method to mount any classes you are using in your extension."""
        for _class in cls:
            self._classes.append(_class(goldy)) # TODO: Initialize class here

            self.logger.debug(
                f"Mounted class '{_class.__name__}' to extension '{self.name}'."
            )

    @overload
    def command(
        self,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Dict[str, SlashOption] = None,
        group: Literal[False] = False,
        wait: bool = False
    ) -> Callable[..., Callable]:
        ...

    @overload
    def command(
        self,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        group: Literal[True] = False,
        wait: bool = False
    ) -> Callable[..., GroupCommand]:
        ...

    def command(
        self,
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        slash_options: Dict[str, SlashOption] = None,
        group: bool = False,
        wait: bool = False
    ) -> Callable[..., GroupCommand] | Callable[..., Callable]:
        """
        Add a command to a Goldy Bot extension with this decorator.

        ---------------

        ⭐ Example:
        -------------
        This is how you create a command in GoldyBot::

            @extension.command()
            async def hello(self, platter: GoldyBot.GoldPlatter):
                await platter.send_message("👋hello", reply=True)

        .. note::

            Visit `here`_ to find out how to create extensions.

        .. _here: https://goldybot.devgoldy.xyz/goldy.extensions.html#how-to-create-an-extension
        """
        def decorate(func):
            def inner(func):
                command = Command(
                    function = func, 
                    name = name, 
                    description = description, 
                    slash_options = slash_options,
                    wait = wait
                )

                class_name = command.function.__qualname__.split(".")[0]

                if class_name not in self._commands:
                    self._commands[class_name] = []

                self._commands[class_name].append(command)

                return GroupCommand(command = command) if group else func

            return inner(func)

        return decorate