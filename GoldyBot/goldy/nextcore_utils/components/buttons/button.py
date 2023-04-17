from __future__ import annotations

from enum import Enum
from typing import overload, Literal
from discord_typings import ButtonComponentData

from .. import BowlRecipe

class ButtonStyle(Enum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5

    BLURPLE = PRIMARY
    GREY = SECONDARY
    GREEN = SUCCESS
    RED = DANGER

# TODO: Create random custom id based on hash of button dict and time it was made.
random_custom_id = 1 # I know there's better ways to do this dw.

class Button(BowlRecipe):
    """A class used to create a slash command button."""
    @overload
    def __init__(self, style: ButtonStyle | int, label: str, custom_id: str = None, emoji: str = None, **extra: ButtonComponentData) -> ButtonComponentData:
        ...

    @overload
    def __init__(self, style: Literal[5], label: str, url: str, emoji: str = None, **extra: ButtonComponentData) -> ButtonComponentData:
        ...

    def __init__(self, style: ButtonStyle | int, label: str, custom_id: str = None, url: str = None, emoji: str = None, **extra: ButtonComponentData) -> ButtonComponentData:
        """
        Creates a discord button to use in action rows. 😋
        
        ⭐ Documentation at https://discord.com/developers/docs/interactions/message-components#buttons
        """
        global random_custom_id
        data: ButtonComponentData = {}

        if isinstance(style, ButtonStyle):
            style = style.value

        if custom_id is None:
            random_custom_id += 1
            custom_id = str(random_custom_id)

        data["type"] = 2 # ID type for button.
        data["style"] = style
        data["label"] = label

        if emoji is not None:
            # I don't personally use emojis any other way so for now I'll implement it like this. 
            # We may have an Emoji creator class in the future to improve things.
            data["emoji"] = {
                "id": None,
                "name": f"{emoji}"
            }

        if style == ButtonStyle.LINK.value:
            data["url"] = url
        else:
            data["custom_id"] = custom_id

        data.update(extra)

        super().__init__(data)