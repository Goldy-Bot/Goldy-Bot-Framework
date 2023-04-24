from __future__ import annotations

from typing import Tuple, TYPE_CHECKING
from devgoldyutils import Colours
from discord_typings import InteractionCreateData, MessageData

from . import commands_cache, Command
from ..nextcore_utils.components import BowlRecipe, registered_recipes, GoldenBowl
from .. import utils, objects
from ... import LoggerAdapter, goldy_bot_logger
from ..objects.golden_platter import GoldPlatter

if TYPE_CHECKING:
    from .. import Goldy

class CommandListener():
    """Class that handles the invoking of commands."""
    def __init__(self, goldy: Goldy) -> None:
        self.goldy = goldy

        self.logger = LoggerAdapter(goldy_bot_logger, prefix=Colours.BLUE.apply("CommandListener"))

    async def start_listening(self) -> None:
        """Registers nextcore listeners and starts listening for commands."""

        # Slash command listener.
        # ------------------------
        self.goldy.shard_manager.event_dispatcher.add_listener(
            self.on_slash_cmd,
            event_name="INTERACTION_CREATE"
        )
        self.logger.info("Slash command listener set!")

        # Prefix command listener.
        self.goldy.shard_manager.event_dispatcher.add_listener(
            self.on_prefix_cmd,
            event_name="MESSAGE_CREATE"
        )
        self.logger.info("Prefix command listener set!")

        return None


    async def on_slash_cmd(self, interaction: InteractionCreateData) -> None:
        # Only respond to slash command interactions.

        guild = self.goldy.guilds.get_guild(interaction["guild_id"])

        if guild is not None:

            # Slash command.
            # ---------------
            if interaction["type"] == 2:

                command: Tuple[str, Command] = utils.cache_lookup(interaction["data"]["name"], commands_cache)

                if command is not None:
                    gold_platter = GoldPlatter(
                        data = interaction, 
                        type = objects.PlatterType.SLASH_CMD, 
                        command = command[1],
                        goldy = self.goldy,
                    )

                    await command[1].invoke(
                        gold_platter
                    )

            
            # Message components.
            # --------------------
            if interaction["type"] == 3:
                message_component: Tuple[str, BowlRecipe, GoldenBowl] = utils.cache_lookup(interaction["data"]["custom_id"], registered_recipes)

                if message_component is not None:
                    gold_platter = GoldPlatter(
                        data = interaction, 
                        type = objects.PlatterType.SLASH_CMD, 
                        command = message_component[1],
                        goldy = self.goldy,
                    )

                    await message_component[1].invoke(
                        gold_platter,
                        message_component[2].cmd_platter
                    )


        return None


    async def on_prefix_cmd(self, message: MessageData) -> None:
        guild = self.goldy.guilds.get_guild(message["guild_id"])

        # If user is bot return right away.
        if message["author"].get("bot", False):
            return

        if guild is not None:
            # Check if prefix is correct.
            if not guild.prefix == message["content"][0]:
                return
            
            # i really hope this doesn't break
            command:Tuple[str, Command] = utils.cache_lookup(message["content"].split(" ")[0][1:], commands_cache)

            if command is not None:

                if command[1].allow_prefix_cmd:
                    gold_platter = GoldPlatter(
                        data = message, 
                        type = objects.PlatterType.PREFIX_CMD, 
                        command = command[1],
                        goldy = self.goldy,
                    )
                    
                    await command[1].invoke(
                        gold_platter
                    )
        
        return None
