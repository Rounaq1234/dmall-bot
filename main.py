import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import os

# Load token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🎁 Redeem Button
class RedeemButton(discord.ui.View):
    def __init__(self, label: str, url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label=label, style=discord.ButtonStyle.link, url=url))

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("Bot is online and ready to DM members with giveaway embeds!")

# 🔗 Create Invite Link
async def get_invite_link(ctx: commands.Context):
    for channel in ctx.guild.text_channels:
        if channel.permissions_for(ctx.guild.me).create_instant_invite:
            try:
                invite = await channel.create_invite(max_age=0, max_uses=0, reason="DM Giveaway Invite")
                return invite.url
            except:
                continue
    return "https://discord.com"

# 🎨 Giveaway Embed
def create_giveaway_embed(member: discord.Member, prize: str, guild: discord.Guild, invite_link: str):
    embed = discord.Embed(
        title="🎉 GIVEAWAY ENDED 🎉",
        description=f"Congratulations, {member.mention}! You won a **[1x] {prize}** giveaway!",
        color=discord.Color.purple(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name=f"[1x] {prize}",
        value=(
            f"**Ended:** {datetime.utcnow().strftime('%d %b %Y %I:%M %p')} (UTC)\n"
            f"**Hosted by:** [{guild.name}]({invite_link})\n"
            f"**Entries:** 723\n"
            f"**Winner:** {member.mention}"
        ),
        inline=False
    )

    embed.set_footer(text="Giveaways | Powered by Dyno Pro")
    return embed

# 📨 Command: DM All Members
@bot.command(name="dmall")
@commands.has_permissions(administrator=True)
async def dmall(ctx, *, prize: str = None):
    if not prize:
        return await ctx.send("❌ Please specify the prize!\nExample: `!dmall Nitro Classic`")

    await ctx.send("🎁 Generating invite link...")
    invite_link = await get_invite_link(ctx)

    await ctx.send(f"📨 Sending DMs to all members...\n🔗 Invite: {invite_link}")

    count = 0
    for member in ctx.guild.members:
        if member.bot:
            continue
        try:
            embed = create_giveaway_embed(member, prize, ctx.guild, invite_link)
            view = RedeemButton(label="🎁 Redeem Prize", url=invite_link)
            await member.send(embed=embed, view=view)
            count += 1
        except discord.Forbidden:
            continue
        except Exception as e:
            print(f"Error sending to {member}: {e}")

    await ctx.send(f"✅ Successfully sent DMs to **{count}** members!")

# 📨 Command: DM Role Members Only
@bot.command(name="drole")
@commands.has_permissions(administrator=True)
async def drole(ctx, role: discord.Role = None, *, prize: str = None):
    if not role or not prize:
        return await ctx.send("❌ Usage: `!drole @Role Prize Name`")

    await ctx.send(f"🎁 Generating invite link for role `{role.name}`...")
    invite_link = await get_invite_link(ctx)

    await ctx.send(f"📨 Sending DMs to members with role **{role.name}**...\n🔗 Invite: {invite_link}")

    count = 0
    for member in role.members:
        if member.bot:
            continue
        try:
            embed = create_giveaway_embed(member, prize, ctx.guild, invite_link)
            view = RedeemButton(label="🎁 Redeem Prize", url=invite_link)
            await member.send(embed=embed, view=view)
            count += 1
        except discord.Forbidden:
            continue
        except Exception as e:
            print(f"Error sending to {member}: {e}")

    await ctx.send(f"✅ Successfully sent DMs to **{count}** members with role `{role.name}`!")

# ⚠️ Error Handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing argument.\nUse: `!dmall prize` or `!drole @Role prize`")
    else:
        await ctx.send(f"⚠️ Unexpected error: {error}")

bot.run(TOKEN)
