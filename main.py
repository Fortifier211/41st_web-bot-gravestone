import os
import subprocess
import discord
from discord.ext import commands

from datetime import datetime
import pandas as pd
import sqlite3
import asyncio
import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from database import unmark_role_credited
from database import get_user_credits, update_user_credits, add_role_credits, get_all_role_credits, remove_role_credits, \
    get_all_non_stacking_role_credits, get_user_removed_credits, reset_user_stats  # Import the new function
from database import has_been_updated, mark_as_updated
from database import has_registered, mark_as_registered, update_user_credits, get_all_role_credits, \
    get_all_non_stacking_role_credits
from database import update_user_credits, get_user_credits
from database import update_user_credits
from database import get_user_removed_credits
from database import get_user_credits, update_user_credits, add_role_credits, get_all_role_credits, remove_role_credits, \
    get_all_non_stacking_role_credits, get_user_removed_credits, reset_user_stats, get_user_medals, get_user_purchases  # Import the new functions
from database import get_user_credits, update_user_credits, mark_role_credited, check_role_credited, get_user_roles_from_servers




from database import remove_registered_status

# Variable to store the state of automatic credit updating
auto_update_enabled = False
debug_mode_enabled = False

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content
intents.members = True  # Enable members intent

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store credits (used for real-time tracking)
credits_dict = {}

# Initialize role_credits from the database
role_credits = {role: credits for role, credits in get_all_role_credits()}
non_stacking_roles = {role: credits for role, credits in get_all_non_stacking_role_credits()}




role_credits = dict(get_all_role_credits())
non_stacking_role_credits = dict(get_all_non_stacking_role_credits())


# Function to read a file and return its contents
# Function to read a file and return its contents



# Channels where the bot commands are allowed
ALLOWED_CHANNEL_NAMES = ['bot-test', 'bot-commands']
REPORT_CHANNEL_NAME = 'bug-reports'
# Google Sheets setup

# Function to read a file and return its contents
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Read Google API key and bot token from files

bot_token_file = 'C:/41st/DiscordBOT/bot-token.txt'


bot_token = read_file(bot_token_file)

# Ensure the private key retains its original formatting
# In this case, we ensure that the \n newlines are correctly interpreted


# Print the key to verify its content and format



scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_info = {
    "type": "service_account",
    "project_id": "st-data-base-424621",
    "private_key_id": "c7344c235e31779eaa683760fbebbf58a0ceb4ed",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDCld9ww4chO98K\nL86IPiUodOE+6pG0BmeP8cpdtmIlBF0itw7SCjQ/MUK+zKzHg9BW0INDpniwcI7F\nbumxViG6IRU1An3gLf4jS/II+Q8B2LELxuRECsoJDBKrfDkg7zR6pUQZLrYaGEu5\n9Zo8Xa1Rh67gIDbVIWjWaJeWhzMXqbolcZAM/aWEUeEPj8zRHrF9V23oknr9yVFc\nK0qel+BLEEgU2mUgNE9lZK8npjzcxFKH5HCi7xsrPa1rAA6a82OqyJBiEqo/kmGP\nzvmrS7uqpQ6RTTg7Pp5nxH3Yo1SER1O5cfO7EpzwmLKmj2FbI8b1DkEG6oAJ4cFW\n26U00fVNAgMBAAECggEAFd1JUh5mXLGhij988YoqGrWnaa5p2NSvZllA5+7KcGZh\nILl5DNjgrgkW+uF8uJ5zFo4vcbaO8SR0pnKkB60p9QQqod45zqrcV5L9C00RBqAW\npMAgfhTIRuP4ZRR8RtsaBn3zfPDmvV/lgmu6fPX5t6OLXtu/zYsHgLAX+G4Qq6PQ\nc6F+IJ91yLDIw0I5r77YRQgvLDGoZRbYvTOOFQ+7YrBOQTkdywrhs2ZTvcViSTJt\n49y31PhnNnFjI+VwfV9MExseb9x67G2rszMYzLgqwDdULXfyV3v3HbC0xIKW0QFp\nQaKfUgHyPyqYxXTCTKHX3l0krhTjLMEIu7Le/BytcQKBgQDqJmM3uZrz7L5oHUM2\nyvEime78A1GFePPT7D7qsUxCJYpf+GykNv6k3D8pArC1rHhVgsLvO0li04i3hMwK\nhiw2M7Kuzrs2oplbvaLsyR1Ll1xeszS3KwwXZvHk0JUBf7D17k4MVko1Mc5zY62q\ntpWPGwpQ6fo7vrJIZEPg0Lq/nwKBgQDUvlPzTGCpzL6rATaVHwzhNowJLI9dk1Jv\nzuM41MI3TQZ/5+NKA3ew/fOiF0rn4ZEhX20F3Y7FCWXsHurcEx3lxLTEaNQWRplZ\nOUDomLoROgIIjo1RG+/UZjMnzGx84zTPbzqs9/92Tq63Zx8vJ63nv7Lm9l2oxfav\ntbNYhQ7zkwKBgQCwQ3uXPHKoQ0TG7Zhmi/lgWc7tCbZ5qqaqlwJ5/EPy233CZymp\nqPiitGYbgjnyWUYw4QHLw66n5aPauu460exAVUSikV+fbmHSDPy0EWWrPOM9Ktx5\nMr+kckuQO3CgMzbMu7snUGIGj1rhxFy80TvfAbUPWkOUbCabllb+y0J58wKBgQDH\nxZYFoJIgwM/GutPrggXRMiybrMlPgLjnnyoFwtxBm8Xfs/veE5WAkWgHrMG9Lzbe\nVMKGwH+BjQq1iG7Yi+cGTQnGaf3GkTMM8tN913TaGlOwf1Q6dvZlyDZ/R9oUCDMe\nGv/JTvQHv2kXdfF1kVgfiAbSFUTr6EF2zDQGiqP4mwKBgQCGsvm9OtrVJ7vhYOjH\nAB4k50/I8Wh+05ApDFE89BktVwyWk1dxm7wofY+GIHdAjSo5r7MW5DtYpOG/BjA0\nufTeuJxjv2XGODV6ceLTHHs7vB5TDWxmepJZ0JeBx1BuU7owf6hio7xBHaIlFyIc\nyGTdgE4pU3Be0PjRSvV0nb9+UA==\n-----END PRIVATE KEY-----\n",

    "client_email": "id-1st-database@st-data-base-424621.iam.gserviceaccount.com",
    "client_id": "105776929037903054810",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-1st-database@st-data-base-424621.iam.gserviceaccount.com"
}

# Debugging: print the private key section of the creds_info to verify correct format




creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
client = gspread.authorize(creds)
spreadsheet_name = '41st-database'
worksheet_user_credits = 'UserCredits'
worksheet_role_credits = 'RoleCredits'
worksheet_non_stacking_role_credits = 'NonStackingRoleCredits'

# Google Drive setup
drive_service = build('drive', 'v3', credentials=creds)


# Ensure continuous operation
async def keep_active():
    while True:
        await asyncio.sleep(3600)  # Keeps the loop running every hour

async def has_role_elsewhere(member, role_name):
    for guild in bot.guilds:
        if guild != member.guild:  # Prüfen Sie andere Server
            guild_member = guild.get_member(member.id)
            if guild_member and any(role.name == role_name for role in guild_member.roles):
                return True
    return False


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    for guild in bot.guilds:
        for member in guild.members:
            db_credits = get_user_credits(member.id, member.roles, role_credits, non_stacking_roles)
            if db_credits and len(db_credits) == 3:
                current_credits, max_credits, removed_credits = db_credits
            else:
                current_credits = 0
                max_credits = 0
                removed_credits = 0

            regular_credits = sum(role_credits.get(role.name, 0) for role in member.roles if role.name in role_credits)
            max_non_stacking_credit = max(
                (non_stacking_roles.get(role.name, 0) for role in member.roles if role.name in non_stacking_roles),
                default=0)

            total_credits = regular_credits + max_non_stacking_credit
            total_credits += current_credits - regular_credits - max_non_stacking_credit

            if current_credits != total_credits:
                update_user_credits(member.id, total_credits)
                credits_dict[member.id] = total_credits
                print(f'Updated credits for member {member.id}: {total_credits}')
            else:
                credits_dict[member.id] = current_credits

    # Send startup message to bot-commands channel
    startup_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    version = "1.5.1"
    embed = discord.Embed(
        title="Bot Startup",
        description=f"The bot has started successfully.\n\n**Startup Time:** {startup_time}\n**Version:** {version}",
        color=discord.Color.red()
    )
    channel = discord.utils.get(bot.get_all_channels(), name='bot-commands')
    if channel:
        await channel.send(embed=embed)

    bot.loop.create_task(keep_active())  # Start the keep active task

@bot.event
async def on_member_update(before, after):
    before_roles = set(role.name for role in before.roles)
    after_roles = set(role.name for role in after.roles)

    removed_roles = before_roles - after_roles
    added_roles = after_roles - before_roles

    server_ids = [850840453800919100, 1138926753931346090, 911409562970628167]

    if removed_roles or added_roles:
        db_credits = get_user_credits(after.id, after.roles, role_credits, non_stacking_roles)
        current_credits = db_credits[0] if db_credits else 0

        print(f"Current credits for user {after.id}: {current_credits}")
        print(f"Removed roles: {removed_roles}")
        print(f"Added roles: {added_roles}")

        # Calculate removed credits
        removed_credits = 0
        for role in removed_roles:
            if role in role_credits:
                # Check if the role is still present on another server
                has_role_elsewhere = False
                for server_id in server_ids:
                    if server_id != before.guild.id:
                        user_roles = get_user_roles_from_servers(after.id, [server_id], bot)
                        if role in user_roles:
                            has_role_elsewhere = True
                            break
                if not has_role_elsewhere:
                    removed_credits += role_credits[role]
                    unmark_role_credited(after.id, role)
                    print(f"Unmarking role {role} as credited for user {after.id}")

        print(f"Removed credits: {removed_credits}")

        # Calculate added credits, only if they have not been credited yet
        added_credits = 0
        for role in added_roles:
            if role in role_credits:
                credited = check_role_credited(after.id, role)
                print(f"Role {role} credited for user {after.id}: {credited}")
                if not credited:
                    added_credits += role_credits[role]
                    mark_role_credited(after.id, role)
                    print(f"Marking role {role} as credited for user {after.id}")

        print(f"Added credits: {added_credits}")

        # Debugging information for non-stacking roles
        max_after_non_stacking_credit = 0
        max_before_non_stacking_credit = 0

        if non_stacking_roles:
            max_after_non_stacking_credit = max(
                (non_stacking_roles.get(role, 0) for role in after.roles if role in non_stacking_roles), default=0)
            max_before_non_stacking_credit = max(
                (non_stacking_roles.get(role, 0) for role in before.roles if role in non_stacking_roles), default=0)

            for role in added_roles:
                if role in non_stacking_roles and non_stacking_roles[role] < max_before_non_stacking_credit:
                    print(f"Non-stacking role {role} added but gives no credits because user {after.id} has a higher role")

        new_credits = current_credits - removed_credits + added_credits + max_after_non_stacking_credit - max_before_non_stacking_credit
        print(f"New credits calculation: {new_credits}")

        # Update credits in the database
        print(f"Updating user credits: user_id={after.id}, current_credits={new_credits}, removed_credits={removed_credits}")
        update_user_credits(after.id, new_credits)
        credits_dict[after.id] = new_credits

        print(f'Updated credits for member {after.id}: {new_credits}')





def add_or_update_user(member):
    user_id = member.id
    current_credits = 0
    max_credits = 0
    removed_credits = 0

    # Calculate total credits from roles
    role_credits_sum = sum(role_credits.get(role.name, 0) for role in member.roles if role.name in role_credits)
    max_non_stacking_credit = max(
        (non_stacking_roles.get(role.name, 0) for role in member.roles if role.name in non_stacking_roles), default=0)
    total_credits = role_credits_sum + max_non_stacking_credit

    # Connect to the database
    connection = sqlite3.connect('credits.db')
    cursor = connection.cursor()

    # Check if user already exists in the database
    cursor.execute('SELECT user_id FROM user_credits WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()

    if data:
        # User exists, update their credits
        cursor.execute('UPDATE user_credits SET current_credits = ?, max_credits = ? WHERE user_id = ?',
                       (total_credits, total_credits, user_id))
        print(f'Updated credits for existing user {user_id}: {total_credits}')
    else:
        # User does not exist, add them with calculated credits
        cursor.execute(
            'INSERT INTO user_credits (user_id, current_credits, max_credits, removed_credits) VALUES (?, ?, ?, ?)',
            (user_id, total_credits, total_credits, removed_credits))
        print(f'Added new user {user_id} with credits: {total_credits}')

    # Commit the transaction and close the connection
    connection.commit()
    connection.close()

updated_users = set()

@bot.event
async def on_message(message):
    print("on_message event triggered.")  # Debug: Event triggered
    print(f"Received message from {message.author.name}: {message.content}")  # Debug: Message received

    # Check if the message is from a guild channel
    if isinstance(message.channel, discord.DMChannel):
        print("Message is from a DM channel, ignoring.")  # Debug: DM Channel
        return

    # Check if the message is in the 'bot-commands' channel
    if message.channel.name not in ALLOWED_CHANNEL_NAMES:
        print("Message is not in the allowed channel.")  # Debug: Wrong channel
        return

    # Process commands as usual
    await bot.process_commands(message)

    # Check if the message is from '41st Utilities'
    if message.author.name == "41st Utilities":
        print("Message is from '41st Utilities'.")  # Debug: Command check

        # Check if the message has embeds
        if message.embeds:
            print("Message contains embeds.")  # Debug: Embed check
            embed = message.embeds[0]
            embed_dict = embed.to_dict()
            print(f"Embed content: {embed_dict}")  # Debug: Embed content

            try:
                # Extract user mention from the embed
                description = embed_dict.get('description', '')
                print(f"Embed description: {description}")  # Debug: Embed description
                if description:
                    user_mention = description.split()[0]
                    print(f"User mention found in embed: {user_mention}")  # Debug: User mention in embed
                else:
                    user_mention = None
                    print("No user mention found in the embed.")  # Debug: User mention not found

                # Extract credit value from the embed description with markdown handling
                credit_value_match = re.search(r'`(\d+)`', description)
                if credit_value_match:
                    credit_value = int(credit_value_match.group(1))
                    print(f"Credit value extracted from embed: {credit_value}")  # Debug: Credit value in embed
                else:
                    print("No credit value found in the embed.")  # Debug: Credit value not found in embed
                    return

                if user_mention:
                    # Extract the user ID from the mention
                    user_id = int(re.findall(r'\d+', user_mention)[0])
                    print(f"Extracted user ID: {user_id}")  # Debug: Extracted user ID

                    # Fetch the member object to get roles
                    member = message.guild.get_member(user_id)
                    if not member:
                        print(f"Member with ID {user_id} not found in the guild.")
                        return

                    # Debug: Before update
                    old_credits = get_user_credits(user_id, member.roles, role_credits, non_stacking_roles)[0]
                    print(f"Old credits for user {user_id}: {old_credits}")

                    # Directly update the user's credits in the database
                    update_user_credits(user_id, credit_value)

                    # Verify the update by querying the database again
                    new_credits = get_user_credits(user_id, member.roles, role_credits, non_stacking_roles)[0]
                    if new_credits == credit_value:
                        print(f"Successfully updated credits for user {user_id} to {new_credits}")  # Debug: Updated credits
                        credits_dict[user_id] = new_credits  # Update the in-memory cache
                    else:
                        print(f"Failed to update credits for user {user_id}. Expected {credit_value}, but got {new_credits}")  # Debug: Update failed

                    # Clone the message and notify about the update only if the message is from the correct guild
                    if message.guild.id == 850840453800919100:
                        # Format the new message
                        new_message = f"{user_mention} {credit_value}"
                        print(f"Formatted new message: {new_message}")  # Debug: Formatted message

                        # Send the cloned message to the same channel
                        await message.channel.send(new_message)
                        print("Cloned message sent.")  # Debug: Message sent

                        # Notify about the update
                        update_notification = f"Credits for {user_mention} have been updated to {credit_value}."
                        await message.channel.send(update_notification)
                        print(f"Update notification sent: {update_notification}")  # Debug: Update notification sent
                    else:
                        print("Message is not from the correct guild, skipping clone and notification.")  # Debug: Wrong guild
                else:
                    print("User mention not found, unable to format the message.")  # Debug: User mention missing
            except Exception as e:
                print(f"Error processing .credits command from embed: {e}")  # Debug: Exception
        else:
            print("Message does not contain embeds.")  # Debug: No embed
            print("No user mention found in the message.")  # Debug: User mention missing
            print("No credit value found in the message.")  # Debug: Credit value missing
    else:
        print("Message is not from '41st Utilities'.")  # Debug: Command not matched

    print("Processed commands.")  # Debug: Processed commands

def read_medals(file_path):
    medals = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().rsplit(' ', 1)
            if len(parts) == 2:
                medal_name, credit_amount = parts
                try:
                    medals[medal_name] = int(credit_amount)
                except ValueError:
                    print(f"Zeile übersprungen aufgrund ungültigen Formats: {line.strip()}")
    return medals

# Lade die Medaillen in ein Dictionary
medals = read_medals('Regiment medals python.txt')



# Function to add a medal to a user and update their credits
async def add_medal_to_user(user_id, medal_name):
    if medal_name not in medals:
        return False, "Medal not found."

    credit_amount = medals[medal_name]

    # Fetch current user credits
    current_credits, max_credits, removed_credits = get_user_credits(user_id, [], {}, {})

    # Update the user's credits
    new_credits = current_credits + credit_amount
    update_user_credits(user_id, new_credits)

    return True, f"Added {medal_name} to user with ID {user_id}, adding {credit_amount} credits."


# Function to remove a medal from a user and update their credits
async def remove_medal_from_user(user_id, medal_name):
    if medal_name not in medals:
        return False, "Medal not found."

    credit_amount = medals[medal_name]

    # Fetch current user credits
    current_credits, max_credits, removed_credits = get_user_credits(user_id, [], {}, {})

    # Update the user's credits
    new_credits = current_credits - credit_amount
    update_user_credits(user_id, new_credits)

    return True, f"Removed {medal_name} from user with ID {user_id}, subtracting {credit_amount} credits."













def is_allowed_channel():
    async def predicate(ctx):
        ALLOWED_CHANNEL_NAMES = ['bot-commands', 'bot-test']  # List of allowed channels
        if ctx.channel.name not in ALLOWED_CHANNEL_NAMES:
            await ctx.send(f"This command can only be used in the #{' or #'.join(ALLOWED_CHANNEL_NAMES)} channels.")
            return False
        return True

    return commands.check(predicate)


def is_Technical_Commander():
    async def predicate(ctx):
        bot_dev_role = discord.utils.get(ctx.guild.roles, name="Technical Commander")
        if bot_dev_role in ctx.author.roles:
            return True
        await ctx.send("You do not have permission to use this command.")
        return False

    return commands.check(predicate)


# Function to get user roles from servers
def get_user_roles_from_servers(user_id, server_ids):
    all_roles = set()
    for server_id in server_ids:
        server = bot.get_guild(server_id)
        if server:
            member = server.get_member(user_id)
            if member:
                all_roles.update({role.name for role in member.roles})
    return all_roles

# List of server IDs to check
server_ids = [850840453800919100, 1138926753931346090, 911409562970628167]







@bot.command()
@is_allowed_channel()
async def hello(ctx):
    embed = discord.Embed(
        title="Hello!",
        description="Greetings from the bot.",
        color=discord.Color.red()
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)
    print(f"Message sent to {ctx.channel.name}")


@bot.command()
@is_Technical_Commander()
async def addrole(ctx, credit_amount: int, *, role_name: str):
    try:
        role_credits[role_name] = credit_amount
        add_role_credits(role_name, credit_amount)

        for guild in bot.guilds:
            for member in guild.members:
                if discord.utils.get(member.roles, name=role_name):
                    db_credits = get_user_credits(member.id)
                    current_credits = db_credits[0] if db_credits else 0
                    new_credits = current_credits + credit_amount
                    credits_dict[member.id] = new_credits
                    update_user_credits(member.id, new_credits)

        embed = discord.Embed(
            title="Role Added",
            description=f'Role {role_name} with {credit_amount} credits has been added.',
            color=discord.Color.red()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        activity_channel = discord.utils.get(ctx.guild.text_channels, name="database-activity")
        if activity_channel:
            await activity_channel.send(f"Added role {role_name} with {credit_amount} credits.")

        await ctx.send(embed=embed)
    except ValueError as ve:
        embed = discord.Embed(
            title="Error",
            description=f'Error adding role: {ve}',
            color=discord.Color.red()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Unexpected Error",
            description=f'Unexpected error: {e}',
            color=discord.Color.red()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)


@bot.command()
@is_Technical_Commander()
async def removerole(ctx, *, role_name: str):
    try:
        if role_name not in role_credits:
            embed = discord.Embed(
                title="Error",
                description=f'Role {role_name} does not exist.',
                color=discord.Color.red()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            return

        for guild in bot.guilds:
            for member in guild.members:
                if discord.utils.get(member.roles, name=role_name):
                    db_credits = get_user_credits(member.id)
                    current_credits = db_credits[0] if db_credits else 0
                    new_credits = current_credits - role_credits[role_name]
                    credits_dict[member.id] = new_credits
                    update_user_credits(member.id, new_credits)

        remove_role_credits(role_name)
        del role_credits[role_name]

        embed = discord.Embed(
            title="Role Removed",
            description=f'Role {role_name} has been removed.',
            color=discord.Color.red()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        activity_channel = discord.utils.get(ctx.guild.text_channels, name="database-activity")
        if activity_channel:
            await activity_channel.send(f"Removed role {role_name}.")

        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Unexpected Error",
            description=f'Unexpected error: {e}',
            color=discord.Color.red()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)



@bot.command()
@is_allowed_channel()
async def report(ctx, *, problem: str = None):
    if problem is None:
        bug_report_info = (
            "To report a bug, please use the following command:\n"
            "`!report_bug <description of the problem>`\n"
            "For example: `!report_bug The credits command is not working correctly.`"
        )
        embed_info = discord.Embed(
            title="How to Report Bugs",
            description=bug_report_info,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_info)
        return

    report_channel = discord.utils.get(ctx.guild.text_channels, name=REPORT_CHANNEL_NAME)
    if report_channel:
        try:
            await report_channel.send(f'Report from {ctx.author.mention}: {problem}')
            embed = discord.Embed(
                title="Report Sent",
                description=f'Thank you for your report. It has been sent to the #{REPORT_CHANNEL_NAME} channel.',
                color=discord.Color.red()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

            # Send message to user explaining the !report_bug command
            bug_report_info = (
                "Thank you for your report. If you encounter any bugs, please use the `!report_bug` command to report them. "
                "For example: `!report_bug The credits command is not working correctly.`"
            )
            embed_info = discord.Embed(
                title="How to Report Bugs",
                description=bug_report_info,
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_info)
        except discord.errors.Forbidden:
            embed = discord.Embed(
                title="Error",
                description=f'Error: Missing permissions to send a message in the #{REPORT_CHANNEL_NAME} channel.',
                color=discord.Color.red()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Error",
            description=f'Error: The report channel #{REPORT_CHANNEL_NAME} does not exist.',
            color=discord.Color.red()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)


@bot.command()
@is_allowed_channel()
async def report_bug(ctx, *, problem: str):
    report_channel = discord.utils.get(ctx.guild.text_channels, name=REPORT_CHANNEL_NAME)
    if report_channel:
        try:
            await report_channel.send(f'Bug report from {ctx.author.mention}: {problem}')
            embed = discord.Embed(
                title="Bug Report Sent",
                description=f'Thank you for your bug report. It has been sent to the #{REPORT_CHANNEL_NAME} channel.',
                color=discord.Color.red()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            embed = discord.Embed(
                title="Error",
                description=f'Error: Missing permissions to send a message in the #{REPORT_CHANNEL_NAME} channel.',
                color=discord.Color.red()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Error",
            description=f'Error: The report channel #{REPORT_CHANNEL_NAME} does not exist.',
            color=discord.Color.red()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)


@bot.command()
@is_allowed_channel()
async def version(ctx):
    version_info = (
        "Version: ```V1.5~Clone```\n"
        "Date: ```05.06.2024```\n"
        "Programmer: ```Sykles```"
    )
    embed = discord.Embed(
        description=version_info,
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# Remove the existing help command
bot.remove_command('help')

@bot.command(name='help')
@is_allowed_channel()
async def help_command(ctx):
    bot_dev_role = discord.utils.get(ctx.guild.roles, name="Technical Commander")
    is_bot_dev = bot_dev_role in ctx.author.roles

    user_commands = (
        f"**List of available commands:**\n\n"
        f"**!hello**: Sends a simple greeting message.\n"
        f"**!credits**: Displays your current credits.\n"
        f"**!whoami**: Sends your information, including join date and credits, via direct message.\n"
        f"**!report <problem>**: Sends a report message to the designated 'bug' channel.\n"
        f"**!version**: Displays the current version of the bot.\n"
        f"**!help**: Lists all available commands and their descriptions.\n"
        f"**!ggn_store**: Displays Geetsly's Gaming Network Store Conversions.\n"
        f"**!store <category>**: Displays store items for a specific credit category.\n"
        f"**!register**: Registers a new user in the database.\n"
        f"**!purchase **: Command to buy items.\n"
        f"** **\n"
    )
    admin_commands = (
        f"**Developer Commands:**\n"
        f"** **\n"
        f"**!addrole <credit_amount>  <role_name>**: Adds a role with a specific credit amount.\n"
        f"**!removerole <role_name>**: Removes a role and its associated credits.\n"
        f"**!exportdb**: Exports the database to an Excel file.\n"
        f"**!debug**: Runs a series of tests on all commands to check for errors.\n"
        f"**!add <@user> <amount> <comment,not necessary>**: Adds credits to a user.\n"
        f"**!remove <@user> <amount> <comment,not necessary> **: Sets the credit amount of a user.\n"
        f"**!setUserCredits <@user><ammount>**: Resets all credits for a user to zero.\n"
        f"**!save_db**: Saves all data to the SQL database.\n"
        f"**!resetStats <@user>**: Resets all data for a specific user.\n"
        f"**!id <@user>**: Sends all information about the mentioned user via direct message.\n"
        f"**!registerRemove <@user>**: Resets the register status of a user.\n"
        f"**!registerEveryone **: registers every user on the server in the database.\n"
        f"**!removeNonCTs **: removes every user without the clone trooper role from the db.\n"
        f"**!useritems <@user> **: shows all itmes an user has .\n"
    )

    help_message = user_commands
    if is_bot_dev:
        help_message += admin_commands

    embed = discord.Embed(
        description=help_message,
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)


@bot.command()
@is_Technical_Commander()
async def exportdb(ctx):
    await ctx.send("Starting the export process...")
    print("Export process started")

    # Connect to the database
    connection = sqlite3.connect('credits.db')
    cursor = connection.cursor()
    print("Connected to the database")

    # Fetch user credits
    cursor.execute('SELECT user_id, current_credits, max_credits, removed_credits FROM user_credits')
    user_credits = cursor.fetchall()
    print(f"Fetched user credits: {user_credits}")

    # Create a dataframe
    df = pd.DataFrame(user_credits, columns=['user_id', 'current_credits', 'max_credits', 'removed_credits'])

    # Get nicknames for users
    guild = ctx.guild
    nicknames = []
    for user_id in df['user_id']:
        member = guild.get_member(int(user_id))
        if member:
            nicknames.append(member.display_name)  # Use the server nickname
            print(f"Fetched nickname for user {user_id}: {member.display_name}")
        else:
            nicknames.append("Unknown User")
            print(f"User ID {user_id} not found in guild, set nickname to 'Unknown User'")

    df.insert(1, 'nickname', nicknames)  # Insert nickname as the second column
    print("Nicknames inserted into dataframe")

    # Fetch role credits
    cursor.execute('SELECT role_name, credit_amount FROM role_credits')
    role_credits = cursor.fetchall()
    print(f"Fetched role credits: {role_credits}")

    # Fetch non-stacking role credits
    cursor.execute('SELECT role_name, credit_amount FROM non_stacking_role_credits')
    non_stacking_role_credits = cursor.fetchall()
    print(f"Fetched non-stacking role credits: {non_stacking_role_credits}")

    connection.close()
    print("Database connection closed")

    # Google Sheets setup
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = {
        "type": "service_account",
        "project_id": "st-data-base-424621",
        "private_key_id": "c7344c235e31779ae6a83760febb58a0ceb4ed",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDCld9ww4chO98K\nL86IPiUodOE+6pG0BmeP8cpdtmIlBF0itw7SCjQ/MUK+zKzHg9BW0INDpniwcI7F\nbumxViG6IRU1An3gLf4jS/II+Q8B2LELxuRECsoJDBKrfDkg7zR6pUQZLrYaGEu5\n9Zo8Xa1Rh67gIDbVIWjWaJeWhzMXqbolcZAM/aWEUeEPj8zRHrF9V23oknr9yVFc\nK0qel+BLEEgU2mUgNE9lZK8npjzcxFKH5HCi7xsrPa1rAA6a82OqyJBiEqo/kmGP\nzvmrS7uqpQ6RTTg7Pp5nxH3Yo1SER1O5cfO7EpzwmLKmj2FbI8b1DkEG6oAJ4cFW\n26U00fVNAgMBAAECggEAFd1JUh5mXLGhij988YoqGrWnaa5p2NSvZllA5+7KcGZh\nILl5DNjgrgkW+uF8uJ5zFo4vcbaO8SR0pnKkB60p9QQqod45zqrcV5L9C00RBqAW\npMAgfhTIRuP4ZRR8RtsaBn3zfPDmvV/lgmu6fPX5t6OLXtu/zYsHgLAX+G4Qq6PQ\nc6F+IJ91yLDIw0I5r77YRQgvLDGoZRbYvTOOFQ+7YrBOQTkdywrhs2ZTvcViSTJt\n49y31PhnNnFjI+VwfV9MExseb9x67G2rszMYzLgqwDdULXfyV3v3HbC0xIKW0QFp\nQaKfUgHyPyqYxXTCTKHX3l0krhTjLMEIu7Le/BytcQKBgQDqJmM3uZrz7L5oHUM2\nyvEime78A1GFePPT7D7qsUxCJYpf+GykNv6k3D8pArC1rHhVgsLvO0li04i3hMwK\nhiw2M7Kuzrs2oplbvaLsyR1Ll1xeszS3KwwXZvHk0JUBf7D17k4MVko1Mc5zY62q\ntpWPGwpQ6fo7vrJIZEPg0Lq/nwKBgQDUvlPzTGCpzL6rATaVHwzhNowJLI9dk1Jv\nzuM41MI3TQZ/5+NKA3ew/fOiF0rn4ZEhX20F3Y7FCWXsHurcEx3lxLTEaNQWRplZ\nOUDomLoROgIIjo1RG+/UZjMnzGx84zTPbzqs9/92Tq63Zx8vJ63nv7Lm9l2oxfav\ntbNYhQ7zkwKBgQCwQ3uXPHKoQ0TG7Zhmi/lgWc7tCbZ5qqaqlwJ5/EPy233CZymp\nqPiitGYbgjnyWUYw4QHLw66n5aPauu460exAVUSikV+fbmHSDPy0EWWrPOM9Ktx5\nMr+kckuQO3CgMzbMu7snUGIGj1rhxFy80TvfAbUPWkOUbCabllb+y0J58wKBgQDH\nxZYFoJIgwM/GutPrggXRMiybrMlPgLjnnyoFwtxBm8Xfs/veE5WAkWgHrMG9Lzbe\nVMKGwH+BjQq1iG7Yi+cGTQnGaf3GkTMM8tN913TaGlOwf1Q6dvZlyDZ/R9oUCDMe\nGv/JTvQHv2kXdfF1kVgfiAbSFUTr6EF2zDQGiqP4mwKBgQCGsvm9OtrVJ7vhYOjH\nAB4k50/I8Wh+05ApDFE89BktVwyWk1dxm7wofY+GIHdAjSo5r7MW5DtYpOG/BjA0\nufTeuJxjv2XGODV6ceLTHHs7vB5TDWxmepJZ0JeBx1BuU7owf6hio7xBHaIlFyIc\nyGTdgE4pU3Be0PjRSvV0nb9+UA==\n-----END PRIVATE KEY-----\n",
        "client_email": "id-1st-database@st-data-base-424621.iam.gserviceaccount.com",
        "client_id": "1057769920937093504810",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-1st-database%40st-data-base-424621.iam.gserviceaccount.com"
    }

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    client = gspread.authorize(creds)
    print("Authenticated with Google Sheets API")

    try:
        # Open the Google Sheet
        sheet = client.open("41st-database")
        print("Opened Google Sheet '41st-database'")

        # Update the 'UserCredits' sheet
        worksheet = sheet.worksheet("UserCredits")
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print("Updated 'UserCredits' sheet")

        # Update the 'RoleCredits' sheet
        role_credits_df = pd.DataFrame(role_credits, columns=['role_name', 'credit_amount'])
        role_credits_worksheet = sheet.worksheet("RoleCredits")
        role_credits_worksheet.clear()
        role_credits_worksheet.update([role_credits_df.columns.values.tolist()] + role_credits_df.values.tolist())
        print("Updated 'RoleCredits' sheet")

        # Update the 'NonStackingRoleCredits' sheet
        non_stacking_role_credits_df = pd.DataFrame(non_stacking_role_credits, columns=['role_name', 'credit_amount'])
        non_stacking_role_credits_worksheet = sheet.worksheet("NonStackingRoleCredits")
        non_stacking_role_credits_worksheet.clear()
        non_stacking_role_credits_worksheet.update(
            [non_stacking_role_credits_df.columns.values.tolist()] + non_stacking_role_credits_df.values.tolist())
        print("Updated 'NonStackingRoleCredits' sheet")

        await ctx.send("Export completed successfully.")
        print("Export process completed successfully")

    except gspread.exceptions.SpreadsheetNotFound:
        await ctx.send("Error: The Google Sheet '41-database' was not found.")
        print("Error: The Google Sheet '41-database' was not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")


@bot.command()
@is_allowed_channel()
async def ggn_store(ctx):
    store_info = (
        "**Geetsly's Gaming Network Store Conversions:**\n"
        "(Please note that these are not prices for credit values. These are credit value conversions, "
        "meaning that a store item which is 15,000 credits is purchasable with $10.00 USD.)\n\n"
        "credits: `7,500` - `$5.00 USD`\n"
        "credits: `10,000` - `$7.50 USD`\n"
        "credits: `12,500` - `$10.00 USD`\n"
        "credits: `15,000` - `$10.00 USD`\n"
        "credits: `20,000` - `$15.00 USD`\n"
        "credits: `25,000` - `$20.00 USD`\n"
        "credits: `30,000` - `$25.00 USD`\n"
        "credits: `40,000` - ``$30.00 USD`\n"
        "credits: `45,000` - `$30.00 USD`\n\n"
        "**EXCEPTIONS/SPECIFICS:**\n"
        "'Phase-1 In Game' - `$10.00 USD`\n"
        "'Custom Visor' - `$15.00 USD`\n"
        "'2003 Helmet' - `$20.00 USD`"
    )
    additional_info = (
        "Please remember to DM 'Forceps' CC-3432 for any GGN-Store purchases."
    )
    embed = discord.Embed(
        description=f'{store_info}\n\n{additional_info}',
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


@bot.command()
@is_allowed_channel()
async def store(ctx, category: int = None):
    store_categories = {
        1: (
            "credits: ```7,500``` - ```$5.00 USD```\n"
            "7,500 - 'Helmet Attachments'\n"
            "Choose from one of our pre-existing helmet attachment options. These options currently include: Flashlights, Antennas, Communicators, and the Heavy Sunvisor.\n"
            "7,500 - 'Rangefinder Down'\n"
            "A Rangefinder lowered over the eyes. (For SGT+ only.)\n"
            "7,500 - 'Helmet Tubes/Pipes'\n"
            "Adds some tubes to your helmet so you can survive without oxygen for a while. "
        ),
        2: (
            "credits: ```10,000``` - ```$7.50 USD```\n"
            "10,000 - 'Build-Your-Own Attachment'\n"
            "A custom attachment brainstormed by you, built by the Art Team Leads. NOTE: Your attachment can not resemble other attachments, such as a rangefinder.\n"
            "10,000 - 'Specialist Binoculars'\n"
            "Allows for binoculars to be added to your helmet. NOTE: Not all helmets are compatible.\n"
            "10,000 - 'Specialist Binoculars Up'\n"
            "Allows for raised binoculars. NOTE: You must already have access to the binoculars."
        ),
        3: (
            "credits: ```15,000``` - ```$10.00 USD```\n"
            "15,000 - 'Flight Computer/Targeting Visor'\n"
            "An external holographic visor. (The Flight Computer is only available to ACE pilots of SGT+. The Targeting visor is only available to Spec Ops helmets (Strike Cadre Helmet).)\n"
            "20,000 - 'Clone Gunner Helmet'\n"
            "A new helmet template. Google 'Clone Heavy Gunner' for reference.\n"
            "20,000 - 'Hooded Helmet'\n"
            "Stylish and Sneaky. (Only for SOF.)"
        ),
        4: (
            "credits: ```30,000``` - ```$25.00 USD```\n"
            "30,000 - 'Phase 1 ARF Helmet'\n"
            "The ARF Helmet from 'Star Wars The Clone Wars'.\n"
            "30,000 - 'Snowtrooper/Flametrooper Helmet'\n"
            "BRING IN THE FLAMETHROWERS!\n"
            "30,000 - 'Custom Visor'\n"
            "Clearance to a one color visor. NOTE: Troopers may get a refund upon reaching the rank of 2LT or higher, or RC.\n"
            "35,000 - 'BARC Helmet and Skin'\n"
            "'For the mysterious types.' Receive access to the 41st BARC Helmet as well as permission to use the 91st Recon Corps in game.\n"
            "35,000 - 'Phase 1 Helmet and Skin'\n"
            "A Phase 1 helmet, along with clearance to wear the corresponding skin in game."
        ),
        5: (
            "credits: ```40,000``` - ```$30.00 USD```\n"
            "40,000 - '2003 Helmet Variants'\n"
            "The classic style. Available for all helmet templates.\n"
            "45,000 - 'Desert Trooper Helmet (And Skin for PC Only.)'\n"
            "'I hate sand.' Receive the 41st Desert Trooper Helmet as well as access to the 501st Legion in game, if you are on PC. NOTE: Google Clone Desert Trooper for a reference.\n"
            "50,000- 'Halfbody art piece'"
        )

    }

    async def send_dm(content):
        max_length = 2000
        for i in range(0, len(content), max_length):
            await ctx.author.send(content[i:i + max_length])

    if category is None:
        summary = (
            "Please use the extended command `!store #` to view all the items in each price category. Here is a key:\n"
            "```\n"
            " 07,500 - !store 1\n"
            " 10,000 - !store 2\n"
            " 15,000 - !store 3\n"
            " 30,000 - !store 4\n"
            " 40,000 - !store 5\n"
            " !store 0 to see all"
            "```\n"
        )

        embed = discord.Embed(
            title="Store Categories",
            description=summary,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif category == 0:
        all_store_info = "\n\n".join(store_categories.values())
        await send_dm(all_store_info)
        embed = discord.Embed(
            title="Store Categories",
            description="I have sent you a DM with all the store categories.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif category in store_categories:
        embed = discord.Embed(
            title=f"Store Category {category}",
            description=store_categories[category],
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Invalid Category",
            description="Invalid category. Please use a number between 0 and 5.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
@is_allowed_channel()
@commands.has_any_role('Economy Admin', 'Economy Lead', 'Commander')
async def id(ctx, member: discord.Member):
    try:
        user_id = member.id
        credits_data = get_user_credits(user_id, member.roles, role_credits, non_stacking_roles)
        current_credits = credits_data[0] if credits_data else 0
        max_credits = credits_data[1] if len(credits_data) > 1 else 0
        removed_credits = credits_data[2] if len(credits_data) > 2 else 0
        joined_at = member.joined_at.strftime("%b %d, %Y")

        embed = discord.Embed(
            title="User Information",
            color=discord.Color.red()
        )
        embed.add_field(name="ID", value=f"{user_id}", inline=False)
        embed.add_field(name="Name" ,value=f"{member.display_name}", inline=False)
        embed.add_field(name="Current Credits", value=f"{current_credits}", inline=False)
        embed.add_field(name="Max Credits", value=f"{max_credits}", inline=False)
        embed.add_field(name="Removed Credits", value=f"{removed_credits}", inline=False)
        embed.add_field(name="Joined At", value=f"{joined_at}", inline=False)
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)

        await ctx.send(embed=embed)
        print(f"User info for {user_id} sent in embed.")  # Debug: Embed sent
    except Exception as e:
        await ctx.send(f"An error occurred while fetching user info: {e}")

# Start troll commands

@bot.command()
@is_allowed_channel()
async def goodmorning(ctx):
    user_id = "647240663796023297"  # Replace with the actual user ID of "therealsqueak"
    user = await bot.fetch_user(user_id)
    if user:
        await ctx.send(f"Good morning, {user.mention}!")
        print(f"Sent good morning message and pinged {user.display_name} ({user_id}).")
    else:
        await ctx.send("Could not find the user therealsqueak.")
        print("Could not find the user therealsqueak.")


@bot.command()
@is_allowed_channel()
async def men_mental_health(ctx):
    user_id = "821881416325005354"  # Replace with the actual user ID of "therealsqueak"
    user = await bot.fetch_user(user_id)
    if user:
        await ctx.send(f"We love you, even if your brothers tell you they are fine, please ask them how they really feel because often you can't see how bad someone is doing , {user.mention}!")
        print(f"Sent good morning message and pinged {user.display_name} ({user_id}).")
    else:
        await ctx.send("Could not find the user zworldandsnap.")
        print("Could not find the user zworldandsnap.")

@bot.command()
@is_allowed_channel()
async def drugs(ctx):
    await ctx.send("Deathsticks ?")


@bot.command()
@is_allowed_channel()
async def Sykles(ctx):
    await ctx.send("tf are you tring to do here")
# Note: You can get the user's ID by enabling Developer Mode in Discord,
# right-clicking on the user, and selecting "Copy ID".
@bot.command()
@is_allowed_channel()
async def happy3years(ctx):
    message = "```Happy 3rd 41st anniversary Izzy, but you don't get a medal```"
    await ctx.send(message)
    print("Sent anniversary message.")


@bot.command()
@is_allowed_channel()
async def bitches(ctx):
    message = "you have no bitches"
    await ctx.send(message)
    print("no bitches.")

@bot.command()
@is_allowed_channel()
async def no_you(ctx):
    message = "What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little 'clever' comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You're fucking dead, kiddo."
    await ctx.send(message)
    print("no bitches.")

@bot.command()
@is_allowed_channel()
async def monte(ctx):
    user_id = "1047317588755095592"  # Replace with the actual user ID of "monte"
    user = await bot.fetch_user(user_id)
    if user:
        await ctx.send(f" touch grass, {user.mention}!")
        print(f"Sent touch crazy message and pinged {user.display_name} ({user_id}).")
    else:
        await ctx.send("Could not find the user monte.")
        print("Could not find the user monte.")

# End troll commands
# Start DB commads

@bot.command()
@is_allowed_channel()
async def register(ctx):
    user_id = ctx.author.id

    # Check if the user has already registered
    if has_registered(user_id):
        await ctx.send(f"{ctx.author.mention}, you have already used the !register command.")
        return

    # Get all role credits from the database
    role_credits = dict(get_all_role_credits())
    non_stacking_role_credits = dict(get_all_non_stacking_role_credits())

    # Calculate credits based on roles
    credits = 0
    added_non_stacking_roles = set()
    for role in ctx.author.roles:
        role_name = role.name
        if role_name in role_credits:
            credits += role_credits[role_name]
        if role_name in non_stacking_role_credits and role_name not in added_non_stacking_roles:
            credits += non_stacking_role_credits[role_name]
            added_non_stacking_roles.add(role_name)

    # Update credits in the database
    update_user_credits(user_id, credits)

    # Mark the user as registered
    mark_as_registered(user_id)

    await ctx.send(f"{ctx.author.mention}, you have been registered with {credits} credits.")


@bot.command()
@is_Technical_Commander()  # Ensure only admins can use this command
async def registerRemove(ctx, member: discord.Member):
    user_id = member.id

    # Remove the registered status!Re
    remove_registered_status(user_id)

    await ctx.send(f"{member.mention}'s register status has been reset. They can use the !register command again.")





@bot.command()
@is_Technical_Commander()  # Ensure only authorized users can run this command
async def registerEveryone(ctx):
    clone_trooper_role = discord.utils.get(ctx.guild.roles, name="Clone Trooper")
    registered_count = 0

    for guild in bot.guilds:
        for member in guild.members:
            user_id = member.id

            # Skip bot accounts
            if member.bot:
                continue

            # Check if the member has the "Clone Trooper" role
            if clone_trooper_role not in member.roles:
                continue

            # Calculate credits based on roles
            credits = 0
            added_non_stacking_roles = set()
            for role in member.roles:
                role_name = role.name
                if role_name in role_credits:
                    credits += role_credits[role_name]
                if role_name in non_stacking_role_credits and role_name not in added_non_stacking_roles:
                    credits += non_stacking_role_credits[role_name]
                    added_non_stacking_roles.add(role_name)

            # Update credits in the database
            update_user_credits(user_id, credits)

            # Mark the user as registered
            if not has_registered(user_id):
                mark_as_registered(user_id)
                registered_count += 1

            # Notify about the update (optional)
            await ctx.send(f"{member.mention} has been registered with {credits} credits.")

    await ctx.send(
        f"All members with the 'Clone Trooper' role have been registered. Total registered: {registered_count}")


@bot.command()
@is_Technical_Commander()  # Ensure only authorized users can run this command
async def removeNonCTs(ctx):
    clone_trooper_role_name = "Clone Trooper"
    removed_count = 0

    for guild in bot.guilds:
        for member in guild.members:
            user_id = member.id

            # Check if the member has the "Clone Trooper" role
            if any(role.name == clone_trooper_role_name for role in member.roles):
                continue

            # If the member does not have the "Clone Trooper" role, remove them from the database
            remove_user_from_db(user_id)
            removed_count += 1
            print(f"Removed user {user_id} from the database.")

    await ctx.send(f"Removed {removed_count} users who do not have the 'Clone Trooper' role.")






@bot.command()
@is_Technical_Commander()  # Ensure only authorized users can run this command
async def cleardb(ctx):
    try:
        # Connect to the database
        connection = sqlite3.connect('credits.db')
        cursor = connection.cursor()

        # List of tables to be cleared
        tables = ['user_credits', 'role_credits', 'non_stacking_role_credits', 'update_status', 'register_status']

        # Clear all tables
        for table in tables:
            cursor.execute(f'DELETE FROM {table}')

        # Commit the changes and close the connection
        connection.commit()
        connection.close()

        await ctx.send("All data has been cleared from the database.")
        print("All data has been cleared from the database.")

    except Exception as e:
        await ctx.send(f"An error occurred while clearing the database: {str(e)}")
        print(f"An error occurred while clearing the database: {str(e)}")


def remove_user_from_db(user_id):
    # Connect to the database
    connection = sqlite3.connect('credits.db')
    cursor = connection.cursor()

    # Remove the user from the database
    cursor.execute('DELETE FROM user_credits WHERE user_id = ?', (user_id,))
    connection.commit()
    connection.close()
    print(f"User {user_id} removed from the database.")


@bot.command()
@is_Technical_Commander()
@is_allowed_channel()
@commands.has_any_role('Economy Admin', 'Economy Lead', 'Commander')
async def save_db(ctx):
    try:
        # Absolute path to the database
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'credits.db')

        print(f"Attempting to save database to {db_path}")

        if os.path.exists(db_path):
            print(f'Database found at {db_path}')
        else:
            raise FileNotFoundError(f'Database not found at {db_path}')

        connection = sqlite3.connect(db_path)
        df_users = pd.read_sql_query("SELECT * FROM user_credits", connection)
        df_roles = pd.read_sql_query("SELECT * FROM role_credits", connection)
        df_non_stacking_roles = pd.read_sql_query("SELECT * FROM non_stacking_role_credits", connection)
        df_removed_credits = pd.read_sql_query("SELECT * FROM removed_credits", connection)

        # Log the data frames to ensure they are loaded correctly
        print("User Credits DataFrame:\n", df_users)
        print("Role Credits DataFrame:\n", df_roles)
        print("Non-Stacking Role Credits DataFrame:\n", df_non_stacking_roles)
        print("Removed Credits DataFrame:\n", df_removed_credits)

        connection.close()

        embed = discord.Embed(
            title="Save Successful",
            description="Database has been saved locally.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        embed = discord.Embed(
            title="File Not Found Error",
            description=f"The database file was not found: {e}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        embed = discord.Embed(
            title="SQLite Error",
            description=f"An SQLite error occurred while saving the database: {e}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"Unexpected error: {e}")
        embed = discord.Embed(
            title="Unexpected Error",
            description=f"An unexpected error occurred while saving the database: {e}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command()
@is_Technical_Commander()
@is_allowed_channel()
async def resetStats(ctx, user: discord.Member):
    try:
        reset_user_stats(user.id)
        credits_dict[user.id] = 0
        await ctx.send(f"All statistics for {user.mention} have been reset.")
    except Exception as e:
        await ctx.send(f"An error occurred while resetting statistics for {user.mention}: {e}")

# End Db commads

@bot.command()
@is_Technical_Commander()
async def kill(ctx):
    await ctx.invoke(save_db)
    await ctx.send("Bot is shutting down...")
    await bot.close()


# Start Credit commands



@bot.command()
@is_allowed_channel()
@is_Technical_Commander()
@commands.has_any_role('Economy Admin', 'Economy Lead', 'Commander')
async def add(ctx, member: discord.Member, amount: int, *, comment: str = None):
    try:
        user_id = member.id
        credits_data = get_user_credits(user_id, member.roles, role_credits, non_stacking_roles)
        current_credits = credits_data[0] if credits_data else 0
        new_credits = current_credits + amount

        update_user_credits(user_id, new_credits)

        # Log activity in database-activity channel
        activity_channel = discord.utils.get(ctx.guild.text_channels, name="database-activity")
        if activity_channel:
            log_message = f"Added {amount} credits to {member.mention}. New balance: {new_credits} credits."
            if comment:
                log_message += f" Comment: {comment}"
            await activity_channel.send(log_message)

        await ctx.send(f"Added {amount} credits to {member.mention}. New balance: {new_credits} credits.")
        print(f'Added {amount} credits to {member.mention} (ID: {member.id}). New balance: {new_credits}')
    except Exception as e:
        await ctx.send(f"An error occurred while adding credits: {e}")
        print(f"An error occurred while adding credits: {e}")


@bot.command()
@is_allowed_channel()
@is_Technical_Commander()

async def remove(ctx, member: discord.Member, amount: int, *, comment: str = None):
    try:
        user_id = member.id
        credits_data = get_user_credits(user_id, member.roles, role_credits, non_stacking_roles)
        current_credits = credits_data[0] if credits_data else 0
        new_credits = current_credits - amount
        removed_credits = amount  # Die Anzahl der entfernten Credits

        update_user_credits(user_id, new_credits, removed_credits)

        # Log activity in database-activity channel
        activity_channel = discord.utils.get(ctx.guild.text_channels, name="database-activity")
        if activity_channel:
            log_message = f"Removed {amount} credits from {member.mention}. New balance: {new_credits} credits."
            if comment:
                log_message += f" Comment: {comment}"
            await activity_channel.send(log_message)

        await ctx.send(f"Removed {amount} credits from {member.mention}. New balance: {new_credits} credits.")
        print(f'Removed {amount} credits from {member.mention} (ID: {member.id}). New balance: {new_credits}')
    except Exception as e:
        await ctx.send(f"An error occurred while removing credits: {e}")
        print(f"An error occurred while removing credits: {e}")


@bot.command()
@is_Technical_Commander()
@commands.has_any_role('Economy Admin', 'Economy Lead', 'Commander')
async def setUserCredits(ctx, member: discord.Member, credits: int, *, comment: str = None):
    try:
        user_id = member.id
        executor_name = ctx.author.display_name

        # Connect to the database
        connection = sqlite3.connect('credits.db')
        cursor = connection.cursor()

        # Check if user already exists in the database
        cursor.execute('SELECT user_id FROM user_credits WHERE user_id = ?', (user_id,))
        data = cursor.fetchone()

        if data:
            # User exists, update their credits
            cursor.execute('UPDATE user_credits SET current_credits = ?, max_credits = ? WHERE user_id = ?',
                           (credits, credits, user_id))
            print(f'Updated credits for user {user_id}: {credits}')
        else:
            # User does not exist, add them with the provided credits
            cursor.execute(
                'INSERT INTO user_credits (user_id, current_credits, max_credits, removed_credits) VALUES (?, ?, ?, ?)',
                (user_id, credits, credits, 0))
            print(f'Added new user {user_id} with credits: {credits}')

        # Commit the transaction and close the connection
        connection.commit()
        connection.close()

        # Log the transaction

        await ctx.send(f"Credits for {member.display_name} have been set to {credits}.")
        print(f"Credits for {member.display_name} ({user_id}) have been set to {credits}.")
    except Exception as e:
        await ctx.send(f"An error occurred while setting credits: {e}")
        print(f"An error occurred while setting credits: {e}")





@bot.command()
@is_allowed_channel()
async def credits(ctx):
    user_id = ctx.author.id
    member = ctx.author

    # Ensure user_roles contains unique role objects
    user_roles = list(set(member.roles))

    # Retrieve credits directly from the database
    credits = get_user_credits(user_id, user_roles, role_credits, non_stacking_roles)
    if credits:
        description = f'You have {credits[0]} credits.'
    else:
        description = 'You do not have any credits.'

    print(f'Credits for user {user_id}: {credits[0] if credits else 0}')

    embed = discord.Embed(
        title="Your Credits",
        description=description,
        color=discord.Color.red()
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)
    print(f"Message sent to {ctx.channel.name}")



@bot.command()
@commands.has_any_role('Economy Admin', 'Economy Lead', 'Commander')
async def check_credits(ctx, member: discord.Member):
    try:
        user_id = member.id
        credits_data = get_user_credits(user_id, member.roles, role_credits, non_stacking_roles)
        current_credits = credits_data[0] if credits_data else 0
        max_credits = credits_data[1] if len(credits_data) > 1 else 0
        removed_credits = credits_data[2] if len(credits_data) > 2 else 0

        embed = discord.Embed(
            title="User Credit Information",
            color=discord.Color.red()
        )
        embed.add_field(name="ID", value=f"{user_id}", inline=False)
        embed.add_field(name="Nickname", value=f"{member.display_name}", inline=False)
        embed.add_field(name="Current Credits", value=f"{current_credits}", inline=False)
        embed.add_field(name="Max Credits", value=f"{max_credits}", inline=False)
        embed.add_field(name="Removed Credits", value=f"{removed_credits}", inline=False)
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)

        await ctx.send(embed=embed)
        print(f"Credit info for {user_id} sent in embed.")  # Debug: Embed sent
    except Exception as e:
        await ctx.send(f"An error occurred while fetching credit info: {e}")

# Implement the add_medal command
@bot.command(name='add_medal')
@commands.has_any_role('Technical Commander', 'Commander')  # Adjust roles as needed
async def add_medal(ctx, member: discord.Member, *, medal_name: str):
    success, message = await add_medal_to_user(member.id, medal_name)
    if success:
        await ctx.send(f"{member.mention} has been awarded the {medal_name} medal.")
    else:
        await ctx.send(f"Failed to add medal: {message}")

# Implement the remove_medal command
@bot.command(name='remove_medal')
@commands.has_any_role('Technical Commander', 'Commander')  # Adjust roles as needed
async def remove_medal(ctx, member: discord.Member, *, medal_name: str):
    success, message = await remove_medal_from_user(member.id, medal_name)
    if success:
        await ctx.send(f"The {medal_name} medal has been removed from {member.mention}.")
    else:
        await ctx.send(f"Failed to remove medal: {message}")


@bot.command()
@is_Technical_Commander()
@is_allowed_channel()
async def botTest(ctx):
    test_results = []
    test_user_id = 583621855986843659  # The user ID to test with

    async def run_command(command, *args):
        try:
            await command(ctx, *args)
            test_results.append(f"✅ {command.name} passed.")
        except Exception as e:
            test_results.append(f"❌ {command.name} failed: {e}")

    member = ctx.guild.get_member(test_user_id)

    # Run all commands
    await run_command(hello)
    await run_command(credits)

    await run_command(whoami)
    await run_command(report, "Test report")
    await run_command(version)
    await run_command(addrole, "TEST", 10)
    await run_command(removerole, "TEST")
    await run_command(exportdb)
    await run_command(ggn_store)

    await run_command( help_command)


    await run_command(save_db)  # Test save_db


    embed = discord.Embed(
        title="Bot Test Results",
        description=f'```\n{"\n".join(test_results)}\n```',
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


# Function to get user purchases
def get_user_purchases(user_id):
    with sqlite3.connect('credits.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT item_name FROM user_purchases WHERE user_id = ?', (user_id,))
        items = cursor.fetchall()
        return [item[0] for item in items]


# Function to add a purchase
def add_user_purchase(user_id, item_name):
    with sqlite3.connect('credits.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_purchases (user_id, item_name) VALUES (?, ?)', (user_id, item_name))
        conn.commit()


# Dictionary of store items with item names as keys and prices as values
store_items = {
    "Flashlight": 7500,
    "Antenna": 7500,
    "Communicator": 7500,
    "Heavy Attachments": 7500,
    "Rangefinder Down": 7500,
    "Helmet Tubes": 7500,
    "Binoculars": 10000,
    "Binoculars Up": 10000,
    "Flight Computer": 15000,
    "Clone Gunner": 20000,
    "Hood": 20000,
    "ARF": 30000,
    "Snowtrooper/Flametrooper": 30000,
    "Custom Visor": 30000,
    "BARC": 35000,
    "Phase 1": 35000,
    "2003 Helmets": 40000,
    "Desert": 45000,
    "Halfbody": 50000,
    # Add other items here
}

@bot.command()
@is_allowed_channel()
async def purchase(ctx, *, item_name: str = None):
    # Define the items_list here
    items_list = "\n".join(store_items.keys())

    if item_name is None:
        message = (
            "To purchase an item, use the command `!purchase <Item name>`.\n"
            "For more information, use `!store`.\n\n"
            "**Available items:**\n"
            f"{items_list}"
        )
        await ctx.send(message)
        return

    user_id = ctx.author.id
    current_credits = get_user_credits(user_id, ctx.author.roles, role_credits, non_stacking_roles)[0]

    if item_name not in store_items:
        await ctx.send(f"The item '{item_name}' is not available in the store.")
        return

    # Check if the user has already purchased the item
    purchased_items = get_user_purchases(user_id)
    if item_name in purchased_items:
        await ctx.send(f"You have already purchased '{item_name}' and cannot buy it again.")
        return

    item_price = store_items[item_name]

    if current_credits >= item_price:
        # Deduct the item price from user's credits
        new_credits = current_credits - item_price
        update_user_credits(user_id, new_credits)
        add_user_purchase(user_id, item_name)
        await ctx.send(
            f"You have successfully purchased '{item_name}' for {item_price} credits. New balance: {new_credits} credits.")
    else:
        await ctx.send(
            f"You do not have enough credits to purchase '{item_name}'. You need {item_price - current_credits} more credits.")

# Command to show purchased items of a user
@bot.command()
@is_allowed_channel()
async def useritems(ctx, user: discord.Member):
    user_id = user.id
    purchased_items = get_user_purchases(user_id)

    if purchased_items:
        items_list = "\n".join(purchased_items)
        await ctx.send(f"{user.mention} has purchased the following items:\n{items_list}")
    else:
        await ctx.send(f"{user.mention} has not purchased any items yet.")


# Function to remove a purchase
def remove_user_purchase(user_id, item_name):
    with sqlite3.connect('credits.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_purchases WHERE user_id = ? AND item_name = ?', (user_id, item_name))
        conn.commit()


# Command to handle refunding items
@bot.command()
@is_allowed_channel()
@commands.has_any_role('Technical Commander', 'Republic Droids', 'Commander')
async def refund(ctx, user: discord.Member, *, item_name: str):
    user_id = user.id
    purchased_items = get_user_purchases(user_id)

    if item_name not in purchased_items:
        await ctx.send(f"{user.mention} has not purchased the item '{item_name}'.")
        return

    item_price = store_items.get(item_name, 0)

    # Remove the item from the user's purchase list
    remove_user_purchase(user_id, item_name)

    # Refund the item's price to the user
    current_credits = get_user_credits(user_id, user.roles, role_credits, non_stacking_roles)[0]
    new_credits = current_credits + item_price
    update_user_credits(user_id, new_credits)

    await ctx.send(
        f"The item '{item_name}' has been refunded to {user.mention}. {item_price} credits have been returned. New balance: {new_credits} credits.")





@bot.command()
@is_allowed_channel()
async def whoami(ctx, subcommand: str = None):
    user = ctx.author
    server_ids = [850840453800919100, 1138926753931346090, 911409562970628167]
    user_roles = get_user_roles_from_servers(user.id, server_ids)

    user_roles = [discord.utils.get(ctx.guild.roles, name=role_name) for role_name in user_roles if
                  discord.utils.get(ctx.guild.roles, name=role_name)]

    print(f"User roles from servers: {[role.name for role in user_roles if role]}")

    non_stacking_roles_list = [
        "Clone Pilot", "Clone Trooper", "Flight Officer", "Lance Corporal", "Corporal", "Flight Captain", "Sergeant",
        "ARC Sergeant", "RC Sergeant", "Sergeant Major", "Flight Commander", "2nd Lieutenant",
        "Flight Lieutenant" "Lieutenant", "ARC Lieutenant", "RC Lieutenant", "Quartermaster", "Captain", "ARC Captain",
        "RC Captain", "Colonel", "Major", "Technical Commander", "Commander", "Marshal Commander"
    ]

    if subcommand == "medals":
        # Define role categories
        army_medals = [
            "Medal of Valor", "41st Service Medal", "Cadet Master", "Mythical Instructor", "Legendary Instructor",
            "Hero of The 41st", "Absolutely Demolished", "Legendary Ranger", "Battle Hardened", "Bane of Clankers",
            "Order of Dedication", "Vaunted Veteran Medal", "Seppie Scourge", "Plot Armor", "Superior Genetics",
            "Flawless Leadership", "Supporting Act", "May the Score be with you", "Deadly and Discrete",
            "The Best of the Best", "Clanker Crusher", "Terror in the Sky", "True Trooper", "Siegebreaker", "Top Gun",
            "41st Representation Medal", "Lone Survivor", "Exemplar",
            "Professional Soldier", "One Man Army", "The Good Batch", "Bred for War", "Outstanding Dedication",
            "Fireteam on Fire", "First Try", "Experience Outranks Everything"
        ]

        level_medals = [
            "Mythical ARF Medal", "Legendary ARF Medal", "Mythical Engineer Medal", "Elite ARF Medal",
            "Legendary Engineer Medal", "Veteran ARF Medal", "Elite Engineer Medal", "Mythical Commando Medal",
            "Mythical ARC Medal", "Mythical Aerial Medal", "Mythical Officer Medal", "Mythical Specialist Medal",
            "Mythical Heavy Medal", "Mythical Assault Medal", "Veteran Engineer Medal", "Legendary Commando Medal",
            "Legendary ARC Medal", "Legendary Aerial Medal", "Legendary Officer Medal", "Legendary Specialist Medal",
            "Legendary Heavy Medal", "Legendary Assault Medal", "Elite Commando Medal", "Elite ARC Medal",
            "Elite Aerial Medal", "Elite Officer Medal", "Elite Specialist Medal", "Elite Heavy Medal",
            "Elite Assault Medal",
            "Veteran Commando Medal", "Veteran ARC Medal", "Veteran Aerial Medal", "Veteran Officer Medal",
            "Veteran Specialist Medal", "Veteran Heavy Medal", "Veteran Assault Medal"
        ]

        army_qualifications = [
            "Scout Trooper", "Aerial Trooper", "Engineer", "Ace Pilot", "ARF Trooper", "Interceptor Pilot",
            "Bomber Pilot", "Veteran Trooper", "Strike Cadre", "Juggernaut Cadre", "Shadow Cadre", "ARC Qualification",
            "Republic Commando", "Frontliner", "Submachine Gunner", "Rifleman", "CQC Trooper", "Suppressor",
            "Grenadier", "Heavy Rifleman", "Hunter", "Aggressor", "Sniper", "Slug Shooter", "Sharpshooter",
            "Operative", "Urban Warrior", "Gunslinger", "HERO Pilot - First Class", "HERO Pilot - Second Class",
            "Galactic Marine", "Medic Cadre", "Shadow Pilot", "Sapper", "Sky Trooper"
        ]

        navy_qualifications = [
            "Interceptor Qualification", "Bomber Qualification", "Ace Pilot", "HERO - Dogfighter", "HERO - Objective",
            "HERO - Aerial Denial", "HERO - Mobility", "HERO - Support"
        ]

        sof_medals = [
            "SOF Service Medal", "Special Forces Veteran", "Special Forces Legend", "Special Forces Myth",
            "Unexpected Assistance", "Devout Protector", "Strength in Unity", "Brotherhood of Steel",
            "Brothers in Arms",
            "Proven Advisor", "Impossible Odds", "41st Superiority", "Double The Effort", "Regime Toppler",
            "Survivalist", "Unbreakable", "Republic Juggernaut", "Death From Above", "Furry Frenzy", "Back to Basics",
            "Operation:SuppressiveShrout", "Seasoned Saboteur", "Support Scuttler", "Masterful Saboteur", "In And Out",
            "Superior Tactics", "Safety's Off", "Tinnie Scrapper", "Commando Culler", "Guerrilla Tactician",
            "Unwavering",
            "Guardian Angel"
        ]

        regiment_medals = [
            "Fixer Upper", "Behind Enemy Lines", "Above and Beyond", "Devout Protectors", "Altered Genetics",
            "Dragway Genetics", "Perfect Attendance", "Honor Roll", "All Terrain Terror", "The Team to Beat",
            "Leading to Victory", "To Sacrifice and Serve", "For the Republic", "Dedication is Key", "Squad Oriented",
            "All but Special Forces", "Top Trainer", "Leading the Charge", "Participation Trophy", "A Cut Above",
            "Base Class Champion", "Trials are our Speciality", "Team Player", "Old but Gold", "He's going for Speed",
            "He's Going the Distance", "Basic Equipment Expert", "Instructor on Fire", "Praise the Maker",
            "FEEL THE WRATH OF THE 41ST"
        ]

        # Get medals and qualifications from specific servers
        army_server = bot.get_guild(850840453800919100)
        army_roles, level_roles, army_qual_roles, navy_qual_roles = [], [], [], []
        if army_server:
            army_member = army_server.get_member(user.id)
            if army_member:
                army_roles = [role.name for role in army_member.roles if role.name in army_medals]
                level_roles = [role.name for role in army_member.roles if role.name in level_medals]
                army_qual_roles = [role.name for role in army_member.roles if role.name in army_qualifications]
                navy_qual_roles = [role.name for role in army_member.roles if role.name in navy_qualifications]

        sof_server = bot.get_guild(911409562970628167)
        sof_roles = []
        if sof_server:
            sof_member = sof_server.get_member(user.id)
            if sof_member:
                sof_roles = [role.name for role in sof_member.roles if role.name in sof_medals]

        regiment_server = bot.get_guild(1138926753931346090)
        regiment_roles = []
        if regiment_server:
            regiment_member = regiment_server.get_member(user.id)
            if regiment_member:
                regiment_roles = [role.name for role in regiment_member.roles if role.name in regiment_medals]

        # Prepare the embed
        embed = discord.Embed(title="Your Medals", color=discord.Color.red())

        if army_roles:
            embed.add_field(name="Army Medals", value="\n".join(army_roles), inline=False)
        if level_roles:
            embed.add_field(name="Level Medals", value="\n".join(level_roles), inline=False)
        if army_qual_roles:
            embed.add_field(name="Army Qualifications", value="\n".join(army_qual_roles), inline=False)
        if navy_qual_roles:
            embed.add_field(name="Navy Qualifications", value="\n".join(navy_qual_roles), inline=False)
        if sof_roles:
            embed.add_field(name="SOF Medals", value="\n".join(sof_roles), inline=False)
        if regiment_roles:
            embed.add_field(name="Regiment Medals", value="\n".join(regiment_roles), inline=False)

        await ctx.send(embed=embed)

    elif subcommand == "purchases":
        purchases_list = get_user_purchases(user.id)
        if purchases_list:
            purchases_str = "\n".join(purchases_list)
            embed = discord.Embed(
                title="Your Purchases",
                description=purchases_str,
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="Your Purchases",
                description="You have no purchases.",
                color=discord.Color.green()
            )
        await ctx.send(embed=embed)

    elif subcommand == "stats":
        current_credits, max_credits, removed_credits = get_user_credits(user.id, user_roles, role_credits,
                                                                         non_stacking_roles)
        join_date = user.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        highest_non_stacking_role = max(
            (role for role in user.roles if role.name in non_stacking_roles_list),
            key=lambda r: non_stacking_roles_list.index(r.name),
            default=None
        )
        army_rank = highest_non_stacking_role.name if highest_non_stacking_role else "No rank"

        embed = discord.Embed(
            title="Your Stats",
            color=discord.Color.purple()
        )
        embed.add_field(name="Username", value=user.display_name, inline=False)
        embed.add_field(name="Join Date", value=join_date, inline=False)
        embed.add_field(name="Army Rank", value=army_rank, inline=False)
        embed.add_field(name="Max Credits", value=max_credits, inline=False)
        embed.add_field(name="Current Credits", value=current_credits, inline=False)
        embed.add_field(name="Removed Credits", value=removed_credits, inline=False)

        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Whoami Command",
            description=f"Use one of the following subcommands:\n"
                        f"!whoami medals - to see your medals\n"
                        f"!whoami purchases - to see your purchases\n"
                        f"!whoami stats - to see your stats",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)



@bot.command(name='debug')
@is_Technical_Commander()
async def debug(ctx):
    """
    Tests all commands except !kill, !resetStats, !cleardb, !registerEveryone, !removeNonCts, and !registerRemove.
    """
    test_commands = [
        "!hello",
        "!credits",
        "!whoami",
        "!whoami medals",
        "!whoami purchases",
        "!whoami stats",
        "!report Test problem report",
        "!version",
        "!help",
        "!ggn_store",
        "!store category",
        "!register",
        "!addrole TestRole 100",
        "!removerole TestRole",
        "!exportdb",
        "!add @user 100",
        "!remove @user 50",
        "!setUserCredits @user",
        "!save_db",
        "!id @user",
        "!check_credits @user"
    ]

    results = []

    await ctx.send("Starting debug process...")

    for command in test_commands:
        await ctx.send(f"Testing command: {command}")
        print(f"Debug: Testing command: {command}")  # Debugging message

        try:
            # Extract the command and its arguments
            parts = command.split()
            cmd_name = parts[0][1:]  # Remove the '!' prefix
            cmd_args = parts[1:]

            # Simulate mentions for commands that require user mentions
            if '@user' in cmd_args:
                cmd_args = [arg.replace('@user', str(ctx.author.id)) for arg in cmd_args]

            # Find the command object
            cmd = bot.get_command(cmd_name)
            if cmd:
                # Invoke the command
                await ctx.invoke(cmd, *cmd_args)
                await ctx.send(f"Successfully tested command: {command}")
                print(f"Debug: Successfully tested command: {command}")  # Debugging message
                results.append((command, "✅"))
            else:
                await ctx.send(f"Command not found: {command}")
                print(f"Debug: Command not found: {command}")  # Debugging message
                results.append((command, "❌"))

        except Exception as e:
            await ctx.send(f"Error testing command {command}: {e}")
            print(f"Debug: Error testing command {command}: {e}")  # Debugging message
            results.append((command, "❌"))

    # Generate the result message
    result_message = "\n".join([f"{command}: {result}" for command, result in results])
    await ctx.send(f"Debugging completed.\n\nResults:\n{result_message}")
    print("Debug: Debugging completed.")  # Debugging message

bot.run(bot_token)