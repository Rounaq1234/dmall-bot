import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ✅ Enable intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🎁 Redeem Button View
class RedeemButton(discord.ui.View):
    def __init__(self, label: str, url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label=label, style=discord.ButtonStyle.link, url=url))

# 🎉 Ready Event
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("Bot is ready to send giveaway-style DMs with dynamic invite links!")

# 🎨 Embed Builder
def create_giveaway_embed(member: discord.Member, prize: str, guild: discord.Guild):
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
            f"**Hosted by:** {guild.name}\n"
            f"**Entries:** 723\n"
            f"**Winner:** {member.mention}"
        ),
        inline=False
    )

    embed.set_footer(text="Giveaways")
    return embed

# 🔗 Create Server Invite
async def get_invite_link(ctx: commands.Context):
    """Create a permanent invite for the first accessible text channel."""
    invite_link = None
    for channel in ctx.guild.text_channels:
        if channel.permissions_for(ctx.guild.me).create_instant_invite:
            try:
                invite = await channel.create_invite(max_age=0, max_uses=0, reason="DM Giveaway Invite")
                invite_link = invite.url
                break
            except Exception as e:
                print(f"Could not create invite in {channel.name}: {e}")
                continue
    return invite_link or "https://discord.com"  # fallback

# 📨 Command 1: DM All Members
@bot.command(name="dmall")
@commands.has_permissions(administrator=True)
async def dmall(ctx, *, prize: str = None):
    """
    DM all members in giveaway style.
    Usage: !dmall Prize
    """
    if not prize:
        return await ctx.send("❌ Please specify the prize!\nExample: `!dmall Nitro Classic?`")

    await ctx.send("🎁 Generating server invite link...")
    invite_link = await get_invite_link(ctx)
    await ctx.send(f"📨 Sending giveaway-style DMs to all members...\n🔗 Invite: {invite_link}")

    count = 0
    for member in ctx.guild.members:
        if member.bot:
            continue
        try:
            embed = create_giveaway_embed(member, prize, ctx.guild)
            view = RedeemButton(label="Redeem Prize", url=invite_link)
            await member.send(embed=embed, view=view)
            count += 1
        except discord.Forbidden:
            continue
        except Exception as e:
            print(f"Error sending to {member}: {e}")
            continue

    await ctx.send(f"✅ Sent giveaway-style DMs to {count} members successfully!")

# 📨 Command 2: DM Members with a Specific Role
@bot.command(name="dmrole")
@commands.has_permissions(administrator=True)
async def dmrole(ctx, role: discord.Role, *, prize: str = None):
    """
    DM members with a specific role in giveaway style.
    Usage: !dmrole @Role Prize
    """
    if not prize:
        return await ctx.send("❌ Please specify the prize!\nExample: `!dmrole @Winners Nitro Classic?`")

    await ctx.send(f"🎁 Generating server invite link for role `{role.name}`...")
    invite_link = await get_invite_link(ctx)
    await ctx.send(f"📨 Sending giveaway-style DMs to members with role `{role.name}`...\n🔗 Invite: {invite_link}")

    members_with_role = [m for m in role.members if not m.bot]
    count = 0

    for member in members_with_role:
        try:
            embed = create_giveaway_embed(member, prize, ctx.guild)
            view = RedeemButton(label="Redeem Prize", url=invite_link)
            await member.send(embed=embed, view=view)
            count += 1
        except discord.Forbidden:
            continue
        except Exception as e:
            print(f"Error sending to {member}: {e}")
            continue

    await ctx.send(f"✅ Sent giveaway-style DMs to {count} members with the `{role.name}` role!")

# ⚠️ Error Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing arguments!\nUse:\n`!dmall Prize?` or `!dmrole @Role Prize?`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Could not find that role. Mention it correctly, e.g. `!dmrole @Winners Nitro?`")
    else:
        await ctx.send(f"⚠️ Unexpected error: {error}")

# 🚀 Run bot
bot.run(TOKEN)