from __future__ import annotations

import os
from devgoldyutils import Colours
from typing import Tuple, List, TYPE_CHECKING

from ...goldy import get_goldy_instance
from ... import goldy_bot_logger, LoggerAdapter

if TYPE_CHECKING:
    from ..commands import Command

extensions_cache:List[Tuple[str, object]] = []
"""
This cache contains all the extensions that have been loaded and it's memory location to the class.
"""

class Extension():
    """
    The base class for a Goldy Bot extension. 

    ---------------

    ⭐ Example:
    -------------
    This is how you set up an extension in a GoldyBot module::
    
        class YourExtension(GoldyBot.Extension):
            def __init__(self):
                super().__init__()

            @GoldyBot.command()
            async def hello(self, platter: GoldyBot.GoldenPlatter):
                await platter.send_message("👋hello", reply=True)

        def load():
            YourExtension()

    More at our `docs`_.

    .. _docs: https://goldybot.devgoldy.me/goldy.extensions.html#how-to-create-an-extension
    """

    def __init__(self):
        """Tells Goldy Bot to Load this class as an extension."""
        self.goldy = get_goldy_instance()

        self.logger = LoggerAdapter(
            LoggerAdapter(goldy_bot_logger, prefix = "Extensions"), 
            prefix = Colours.GREY.apply(self.code_name)
        )

        # Cached commands list.
        self.commands: List[Command] = [

        ]

        self.__loaded_path = os.path.realpath(self.__class__.__module__) + ".py"

        if self.code_name.lower() in [extension.lower() for extension in self.goldy.config.ignored_extensions]:
            self.logger.info(f"Not loading the extension '{self.code_name}' as it's ignored.")
            return False

        # Adding to cache and loading commands.
        # ---------------------------------------        
        extensions_cache.append(
            (self.code_name, self)
        )

        self.logger.info("Extension initialized!")

    @property
    def code_name(self) -> str:
        return self.__class__.__name__
    
    @property
    def loaded_path(self) -> str:
        "The path where this extension was loaded."
        return self.__loaded_path

    async def unload(self) -> None:
        """Unloads and deletes itself from cache and all the commands with it."""
        for command in self.commands:
            await command.unload()

        extensions_cache.remove(
            (self.code_name, self)
        )

        self.logger.debug(f"Extension '{self.code_name}' removed!")

        return None