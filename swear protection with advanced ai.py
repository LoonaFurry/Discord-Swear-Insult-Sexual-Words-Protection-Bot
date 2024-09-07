import os
import discord
from discord.ext import commands
from groq import Groq
import asyncio

# Configuration - Use environment variables for security
DISCORD_BOT_TOKEN =('your-discord-token')
GROQ_API_KEY =('your-api-key')


# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

# Define lists of bad words including sexual content in English, Turkish, and German
BAD_WORDS = set([
    # Turkish bad words
    "engelli", "ucube", "pislik", "aşalık", "şerefsiz", "ibne", "sümsük",
    "piç", "amçık", "amk", "mk", "orosbu", "siktir",
    # Turkish specific phrases
    "siktir seni", "sikeyim", "amına koyayım", "koca göt", "sürtük",
    # Turkish sexual content terms
    "sürtük", "sürtükler", "seks", "penis", "vajina", "kıç", "am", "fuck",
    # English bad words
    "fuck", "shit", "bitch", "asshole", "cunt", "motherfucker", "nigger",
    "pussy", "dick",
    # Sexual content terms
    "cum", "dildo", "fap", "fuck", "masturbate", "orgasm", "penis", "porn", "sex", "vagina",
    # German bad words
    "arschloch", "scheiße", "miststück", "huren", "fotze", "ficker", "penner", "spast", "schwuchtel",
    "abgefuckt", "kacke", "drecksau", "scheißer", "arsch", "schlampe", "idiot", "bastard", "hurensohn",
    # German sexual content terms
    "sex", "penis", "vagina", "masturbation", "sperma", "orgasmus", "dildo", "ficken", "blasen", "spritzen"
])

# Discord Bot Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

# Function to detect bad words
def contains_bad_words(text):
    """Check if the text contains any bad words from the list.
    
    Args:
        text: The text to analyze.

    Returns:
        True if bad words are detected, False otherwise.
    """
    text = text.lower()
    print(f"Analyzing text: {text}")  # Debug log
    for bad_word in BAD_WORDS:
        if bad_word in text:
            print(f"Detected bad word: {bad_word}")  # Debug log
            return True
    return False

# Swear and Insult Detection Function using Groq API
def detect_explicit_content(text):
    """Detects explicit and sexual content in text using the LLaMA-3.1-70B-Versatile model via Groq API.
    
    Args:
        text: The text to analyze.

    Returns:
        True if explicit or sexual content is detected, False otherwise.
    """
    try:
        # Prepare the prompt for the model
        prompt = (
            "You are a helpful and harmless AI assistant. "
            "Determine if the following text contains any explicit or sexual content. "
            "Respond with 'yes' or 'no' only.\n\n"
            f"Text: {text}"
        )

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        # Create a chat completion using the LLaMA-3.1-70B-Versatile model
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-70b-versatile",
        )

        # Print the response to understand its structure
        print("Chat Completion Response:", chat_completion)

        # Check the response content
        if hasattr(chat_completion, 'choices') and len(chat_completion.choices) > 0:
            # Access the content correctly
            response_message = chat_completion.choices[0].message.content.strip().lower()
            return response_message == "yes"
        else:
            print("No choices found in response.")
            return False

    except AttributeError as e:
        print(f"AttributeError in response processing: {e}")
        return False
    except KeyError as e:
        print(f"KeyError in response processing: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Bot Events
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        # Check the message for explicit and sexual content
        if contains_bad_words(message.content) or detect_explicit_content(message.content):
            await message.delete()
            warning_message = await message.channel.send(
                f'{message.author.mention}, your message was removed as it may contain explicit or sexual content.'
            )
            # Wait for 10 seconds and then delete the warning message
            await asyncio.sleep(10)
            await warning_message.delete()
    except Exception as e:
        print(f"Error processing message: {e}")
        # Send a generic error message without specific details
        await message.channel.send(
            'An error occurred while processing your message. Please try again later.'
        )

# Run the Bot
bot.run(DISCORD_BOT_TOKEN)