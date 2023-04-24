from __future__ import annotations
from typing import overload, List, TYPE_CHECKING
from discord_typings import MessageReferenceData, InteractionMessageCallbackData, MessageData, InteractionCallbackData
from discord_typings.resources.channel import MessageBase

from aiohttp import FormData
from nextcore.http import Route
from nextcore.common import json_dumps

from ... import objects, utils

if TYPE_CHECKING:
    from ..components import GoldenBowl
    from ..embeds.embed import Embed

# TODO: Add more options to allow using channel instead of platter.

@overload
async def send_msg(
    platter: objects.GoldPlatter, 
    text: str = None, 
    embeds: List[Embed] = None, 
    bowls: List[GoldenBowl] = None, 
    reply: bool = False, 
    **extra: MessageData | InteractionCallbackData
) -> objects.Message: # Work in progress...
    """
    Allows you to create and send a message to the channel the command was invoked from as a form of reply.
    
    ------------------

    Parameters
    ----------
    ``platter``
        The gold platter from the command.
    ``text``
        The content of the message.
    ``embeds``
        Embeds to include in the message.
    ``bowls``
        Components to include in the message.
    ``reply``
        Whether goldy bot should liberally reply to the message the command was invoked.
    ``**extra``
        Allows you to pass the extra parameters that are missing.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

@overload
async def send_msg(
    channel, 
    text: str = None,
    embeds: List[Embed] = None, 
    bowls: List[GoldenBowl] = None, 
    **extra: MessageData | InteractionCallbackData
) -> objects.Message: # TODO: Add type to channel when channel object is available.
    """
    Allows you to create and send a message to this specific channel.
    
    ------------------

    Parameters
    ----------
    ``channel``
        The channel the message should be sent to.
    ``text``
        The content of the message.
    ``embeds``
        Embeds to include in the message.
    ``bowls``
        Components to include in the message.
    ``**extra``
        Allows you to pass the extra parameters that are missing.
        
    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

@overload
async def send_msg(
    member: objects.Member, 
    text: str = None, 
    embeds: List[Embed] = None, 
    bowls: List[GoldenBowl] = None, 
    **extra: MessageData | InteractionCallbackData
) -> objects.Message:
    """
    Allows you to create and send a message to this member's dms.
    
    ------------------

    Parameters
    ----------
    ``member``
        The member the message should be sent to.
    ``text``
        The content of the message.
    ``embeds``
        Embeds to include in the message.
    ``bowls``
        Components to include in the message.
    ``**extra``
        Allows you to pass the extra parameters that are missing.

    Returns
    -------
    ``GoldyBot.goldy.objects.message.Message``
        The message that was sent.
    """
    ...

async def send_msg(
    object: objects.GoldPlatter | objects.Member, 
    text: str = None, 
    embeds: List[Embed] = None, 
    bowls: List[GoldenBowl] = None, 
    reply: bool = False, 
    delete_after: float = None,
    **extra: MessageData | InteractionCallbackData
) -> objects.Message:
    
    message_data:MessageData = None
    goldy = object.goldy
    
    payload: MessageBase | InteractionMessageCallbackData = {}

    if text is not None:
        payload["content"] = text

    if embeds is not None:
        payload["embeds"] = embeds

    if bowls is not None:
        payload["components"] = bowls

        # Bowls need the command platter object when checking if it was the author who invoke a recipe.
        for bowl in bowls:
            bowl.cmd_platter = object

    payload.update(extra)


    # TODO: Add support for member and channel objects.
    # 24/04/2023: Let's scrap this and stick with platters for sending messages. 
    # Although this means we will have to find a way to somehow convert a member object to a platter or embed it perhaps.

    if object.type.value == 1:
        # Perform interaction response.
        # ------------------------------

        # Callback message.
        # ------------------
        if object.interaction_responded is False:

            await goldy.http_client.request(
                Route(
                    "POST", 
                    "/interactions/{interaction_id}/{interaction_token}/callback", 
                    interaction_id = object.data["id"], 
                    interaction_token = object.data["token"]
                ),
                rate_limit_key = goldy.nc_authentication.rate_limit_key,
                json = {
                    "type": 4, 
                    "data": payload
                }
            )

            object.interaction_responded = True

            # Get and return message data of original interaction response. 
            r = await goldy.http_client.request(
                Route(
                    "GET", 
                    "/webhooks/{application_id}/{interaction_token}/messages/@original", 
                    application_id = goldy.application_data["id"], 
                    interaction_token = object.data["token"]
                ),
                rate_limit_key = goldy.nc_authentication.rate_limit_key
            )

            message_data = await r.json()

            object.logger.debug("Interaction callback message was sent.")


        # Follow up message.
        # -------------------
        # Is sent when you want to respond again after sending the original response to an interaction command.
        else:

            r = await goldy.http_client.request(
                Route(
                    "POST", 
                    "/webhooks/{application_id}/{interaction_token}", 
                    application_id = goldy.application_data["id"], 
                    interaction_token = object.data["token"]
                ),
                rate_limit_key = goldy.nc_authentication.rate_limit_key,
                json = payload
            )

            message_data = await r.json()

            object.logger.debug("Interaction follow up message was sent.")

    else:
        # Perform normal message response.
        # ----------------------------------

        if reply:
            payload["message_reference"] = MessageReferenceData(
                message_id = object.data["id"],
                channel_id = object.data["channel_id"],
                guild_id = object.data["guild_id"]
            )

        form_data = FormData()
        form_data.add_field("payload_json", json_dumps(payload))

        r = await goldy.http_client.request(
            Route(
                "POST", 
                "/channels/{channel_id}/messages", 
                channel_id = object.data['channel_id']
            ),
            data = form_data,
            rate_limit_key = goldy.nc_authentication.rate_limit_key,
            headers = goldy.nc_authentication.headers,
        )

        message_data = await r.json()

        object.logger.debug("Message was sent.")


    message = objects.Message(message_data, goldy)

    if delete_after is not None:
        utils.delay(
            coro = message.delete(f"delete_after was set to {delete_after} seconds"), 
            seconds = delete_after, 
            goldy = goldy
        )

    return message