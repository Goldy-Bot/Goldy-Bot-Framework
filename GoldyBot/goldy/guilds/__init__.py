from __future__ import annotations

from typing import List, Tuple

from .. import Goldy, utils
from ..database import DatabaseEnums
from ...errors import GoldyBotError

from .guild import Guild

class Guilds():
    def __init__(self, goldy:Goldy) -> None:
        self.goldy = goldy
        self.allowed_guilds = goldy.config.allowed_guilds

        if self.allowed_guilds == []:
            raise AllowedGuildsNotSpecified()
        
        self.guilds:List[Tuple[str|int, Guild]] = []

    # TODO: In the future we might have to add some sort of way to reload the guild config of a guild from the database. (or just run setup again on that particular guild if that works well)
    # I can see this being needed if the v5 framework is going to be running public invite-able bots.
    # Also maybe we should rerun the setup when we reload.

    async def setup(self):
        """Adds guilds specified in goldy.json to the database if not already added."""
        # TODO: Find better way to organize this code, it's too long and complex for my liking.
        # 08/04/2023: idk is it really that complex... i'll come back to it later...

        database = self.goldy.database.get_goldy_database(DatabaseEnums.GOLDY_MAIN)

        for guild in self.allowed_guilds:

            # Add guild to database.
            # --------------------------------
            guild_config_template = {
                "_id": guild[0],
                "code_name": guild[1],

                "prefix": "!",

                "roles": {

                },
                "channels": {

                },

                "allowed_extensions": [],
                "disallowed_extensions": [],
                "hidden_extensions": [],
            }

            guild_config = await database.find_one("guild_configs", query={"_id":guild[0]})

            if guild_config is None:
                guild_config = guild_config_template
                await database.insert("guild_configs", data=guild_config)
            else:
                for item in guild_config_template:

                    if item not in guild_config:
                        guild_config[item] = guild_config_template[item]

                await database.edit("guild_configs", query={"_id":guild[0]}, data=guild_config)
        

            # Add guild to list.
            # --------------------
            self.guilds.append(
                (guild[0], Guild(id=guild[0], code_name=guild[1], config_dict=guild_config))
            )


    def get_guild(self, guild_id:str|int) -> Guild | None:
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
class AllowedGuildsNotSpecified(GoldyBotError):
    def __init__(self):
        super().__init__(
            "Please add your guild id to the allowed_guilds in goldy.json"
        )