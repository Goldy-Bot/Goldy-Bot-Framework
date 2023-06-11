from __future__ import annotations

from typing import Tuple

import GoldyBot
from GoldyBot import cache_lookup, front_end_errors
from GoldyBot.goldy.extensions import extensions_cache

class Extensions(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

        # Hack to force this extension to load last. This works because I made Goldy bot load extensions backwards (quite goofy I know 🤓).
        #extensions_cache.remove((self.name, self))
        #extensions_cache.insert(0, (self.name, self))

        # TODO: FUCK we can't do that, we NEEEED to find a way to load this extension last.

        self.extension_enabled = GoldyBot.Embed(
            title = "💚 Enabled!",
            description = "Extension has been enabled. 👍",
            colour = GoldyBot.Colours.LIME_GREEN
        )

        self.extension_already_enabled = GoldyBot.Embed(
            title = "🧡 Already Enabled!",
            description = "That extension is already enabled.",
            colour = GoldyBot.Colours.AKI_ORANGE
        )

        self.extension_disabled = GoldyBot.Embed(
            title = "🖤 Disabled!",
            description = "Extension has been disabled. 👍",
            colour = GoldyBot.Colours.INVISIBLE # TODO: Replace this with black.
        )

        self.extension_already_disabled = GoldyBot.Embed(
            title = "🤎 Already Disabled!",
            description = "That extension is already disabled.",
            colour = GoldyBot.Colours.GREY # TODO: Replace this with brown.
        )

    @GoldyBot.command(hidden = True)
    async def extensions(self, platter: GoldyBot.GoldPlatter):
        ...

    @extensions.sub_command(
        description = "A command for enabling a Goldy Bot extension that is disabled.",
        slash_options = {
            "extension": GoldyBot.SlashOption(
                choices = [GoldyBot.SlashOptionChoice(extension[0], extension[0]) for extension in extensions_cache]
            )
        }
    )
    async def enable(self, platter: GoldyBot.GoldPlatter, extension: str):
        extension: GoldyBot.Extension = cache_lookup(extension, extensions_cache)[1]

        if extension.is_loaded:
            await platter.send_message(embeds = [self.extension_already_enabled], delete_after = 5)
            return

        await self.goldy.extension_loader.load([extension.loaded_path])
        await platter.send_message(embeds = [self.extension_enabled])

    @extensions.sub_command(
        description = "A command for disabling a Goldy Bot extension that is enabled.",
        slash_options = {
            "extension": GoldyBot.SlashOption(
                choices = [GoldyBot.SlashOptionChoice(extension[0], extension[0]) for extension in extensions_cache]
            )
        }
    )
    async def disable(self, platter: GoldyBot.GoldPlatter, extension: str):
        extension: GoldyBot.Extension = cache_lookup(extension, extensions_cache)[1]

        if not extension.is_loaded:
            await platter.send_message(embeds = [self.extension_already_disabled], delete_after = 5)
            return

        await extension.unload()
        await platter.send_message(embeds = [self.extension_disabled])

def load():
    Extensions()