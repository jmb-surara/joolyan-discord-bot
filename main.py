import discord
import re
import os
from flask import Flask
from threading import Thread

# Flask app to keep bot alive (for Replit or similar)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# Discord client setup with required intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Regex patterns and base transformations
PLATFORMS = {
    r"(https?://(?:www\.)?instagram\.com/p/\S+)": "https://kkinstagram.com/p/",
    r"(https?://(?:www\.)?instagram\.com/reel/\S+)": "https://kkinstagram.com/reel/",
    r"(https?://(?:www\.)?instagram\.com/tv/\S+)": "https://kkinstagram.com/tv/",
    r"(https?://(?:www\.)?instagram\.com/stories/\S+)": "https://kkinstagram.com/stories/",
    r"(https?://(?:www\.)?twitter\.com/\S+)": "https://vxtwitter.com/",
    r"(https?://(?:www\.)?tiktok\.com/\S+)": "https://vxtiktok.com/",
    r"(https?://(?:www\.)?reddit\.com/\S+)": "https://vxreddit.com/",
}

# Short TikTok patterns (vt. / vm.)
SHORT_TIKTOK_REGEX = r"https?://(vt|vm)\.tiktok\.com/\S+"

# Convert supported links to embeddable versions
async def transform_links_and_get_comment(message):
    words = message.content.split()
    modified_links = []
    comment_words = []

    for word in words:
        is_link = False

        # Handle short TikTok links
        if re.match(SHORT_TIKTOK_REGEX, word):
            try:
                new_link = word.replace("tiktok.com", "vxtiktok.com", 1)
                modified_links.append(new_link)
                is_link = True
            except Exception as e:
                print(f"⚠️ Error transforming short TikTok link {word}: {e}")

        # Handle full URLs for other platforms
        for pattern, new_base in PLATFORMS.items():
            if re.match(pattern, word):
                try:
                    path = word.split(".com/")[1]
                    modified_links.append(new_base + path)
                    is_link = True
                    break
                except Exception as e:
                    print(f"⚠️ Error transforming long link {word}: {e}")

        # If it's not a link, it's likely a comment
        if not is_link:
            comment_words.append(word)

    comment = " ".join(comment_words).strip()
    return modified_links, comment

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    modified_links, comment = await transform_links_and_get_comment(message)

    if modified_links:
        user_mention = message.author.mention
        output = f"🔗 Embeddable links requested by {user_mention}:"

        if comment:
            output += f"\n💬 **Comment:** {comment}"

        output += "\n" + "\n".join(modified_links)

        try:
            await message.channel.send(output)
            await message.delete()
        except discord.Forbidden:
            print("⚠️ Bot lacks permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Error sending or deleting message: {e}")

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if TOKEN:
        client.run(TOKEN)
    else:
        print("❌ DISCORD_BOT_TOKEN not set in environment variables.")
