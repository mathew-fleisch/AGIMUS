from .common import *
from utils.check_channel_access import *
from utils.media_utils import *
from utils.timekeeper import *

command_config = config["commands"]["clip"]
emojis = config["emojis"]

# Load JSON Data
f = open(command_config["data"])
clip_data = json.load(f)
f.close()

# clips() - Entrypoint for /clip command
# List the available clips by key and send to user as ephemeral
@slash.slash(
  name="clips",
  description="Retrieve the List of Clips.",
  guild_ids=config["guild_ids"]
)
async def clips(ctx:SlashContext):
  clips_list = "\n".join(clip_data)
  embed = discord.Embed(
    title="List of Clips",
    description=clips_list,
    color=discord.Color.blue()
  )
  try:
    await ctx.author.send(embed=embed)
    await ctx.reply(f"{emojis.get('tendi_smile_happy')} Sent you a DM with the full List of Clips!", hidden=True)
  except:
    await ctx.reply(embed=embed, hidden=True)


# clip() - Entrypoint for /clip command
# Parses a query, determines if it's allowed in the channel,
# and if allowed retrieve from metadata to do matching and
# then send the .mp4 file
@slash.slash(
  name="clip",
  description="Send a clip to the channel!",
  guild_ids=config["guild_ids"],
  options=[
    create_option(
      name="query",
      description="Which clip?",
      required=True,
      option_type=3
    ),
    create_option(
      name="private",
      description="Send clip to just yourself?",
      required=False,
      option_type=5,
    )
  ]
)
@check_channel_access(command_config)
async def clip(ctx:SlashContext, **kwargs):
  query = kwargs.get('query')
  private = kwargs.get('private')

  # Private drops are not on the timer
  clip_allowed = True
  if not private:
    clip_allowed = await check_timekeeper(ctx)

  if (clip_allowed):  
    q = query.lower().strip()
    clip_metadata = get_media_metadata(clip_data, q)

    if clip_metadata:
      try:
        filename = get_media_file(clip_metadata)
        await ctx.send(file=discord.File(filename), hidden=private)
        if not private:
          set_timekeeper(ctx)
      except BaseException as err:
        logger.info(f"ERROR LOADING CLIP: {err}")
        userid = command_config.get("error_contact_id")
        if userid:
          await ctx.send(f"{emojis.get('emh_doctor_omg_wtf_zoom')} Something has gone horribly awry, we may have a coolant leak. Contact Lieutenant Engineer <@{userid}>", hidden=True)  
    else:
      await ctx.send(f"{emojis.get('ezri_frown_sad')} Clip not found! To get a list of clips run: /clips", hidden=True)
  else:
    await ctx.send(f"{emojis.get('ohno')} Someone in the channel has already posted a clip too recently. Please wait a minute before another clip!", hidden=True)