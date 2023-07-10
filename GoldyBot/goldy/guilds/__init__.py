from __future__ import annotations

from typing import List, Tuple

from nextcore.http import Route, NotFoundError
from devgoldyutils import Colours

from .. import nextcore_utils
from .. import Goldy, LoggerAdapter, goldy_bot_logger
from ... import utils, errors
from ..database import DatabaseEnums

from .guild import Guild

import logging

class GuildManager():
    def __init__(self, goldy: Goldy) -> None:
        self.goldy = goldy
        self.allowed_guilds = goldy.config.allowed_guilds
        self.logger = LoggerAdapter(goldy_bot_logger, prefix=Colours.ORANGE.apply("GuildManager"))

        if self.allowed_guilds == []:
            raise AllowedGuildsNotSpecified(self.logger)
        
        self.guilds: List[Tuple[str|int, Guild]] = []

    # TODO: In the future we might have to add some sort of way to reload the guild config of a guild from the database. (or just run setup again on that particular guild if that works well)
    # I can see this being needed if the v5 framework is going to be running public invite-able bots.
    # Also maybe we should rerun the setup when we reload.

    async def setup(self):
        """Adds guilds specified in goldy.json to the database if not already added."""
        self.logger.info("Setting up guilds...")

        for allowed_guild in self.allowed_guilds:

            # Getting guild discord data
            # ---------------------------
            try:
                guild_data = await nextcore_utils.get_guild_data(allowed_guild[0], self.goldy)
            except NotFoundError:
                raise GuildNotFound(
                    allowed_guild[1], self.logger
                )

            guild = Guild(
                id = allowed_guild[0], 
                code_name = allowed_guild[1], 
                data = guild_data, 
                goldy = self.goldy
            )

            await guild.config_wrapper.update() # This should update the guild's config data which should also generate itself configuration in the database if it's missing.

            # Add guild to list.
            # --------------------
            self.guilds.append(
                (allowed_guild[0], guild)
            )

            self.logger.debug(f"Guild '{guild.code_name}' set up.")

        self.logger.info("Done setting up guilds.")


    def get_guild(self, guild_id: str | int) -> Guild | None:
        """Finds and returns goldy bot guild by id."""
        cache_tuple = utils.cache_lookup(
            key=guild_id,
            cache=self.guilds
        )

        if cache_tuple is None:
            return None

        return cache_tuple[1]
            

# Exceptions
# ------------
class AllowedGuildsNotSpecified(errors.GoldyBotError):
    def __init__(self, logger: logging.Logger = None):
        super().__init__(
            "Please add your guild id to the allowed_guilds in goldy.json",
            logger = logger
        )

class GuildNotFound(errors.GoldyBotError):
    def __init__(self, guild_code_name: str, logger: logging.Logger = None):
        super().__init__(
            f"We couldn't find the guild '{guild_code_name}' you entered in allowed_guilds! " \
            "Are you sure you have entered the guild id correctly and that goldy bot is currently present in that guild.",
            logger = logger
        )