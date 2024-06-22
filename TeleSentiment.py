from telethon import TelegramClient, errors
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import GetHistoryRequest
import re
import json

# Your API credentials
api_id = ''
api_hash = ''
phone = ''
username = ''
group_username = 'GhostsofPs_Chat' 

# File paths for the sentiment word lists
positive_words_file = 'positive.txt'
negative_words_file = 'negative.txt'
booster_inc_words_file = 'booster_inc.txt'
booster_decr_words_file = 'booster_decr.txt'
negation_words_file = 'negation.txt'

# Initialize Telegram client
client = TelegramClient(username, api_id, api_hash)

async def authenticate():
    # Connect to Telegram
    await client.connect()
    
    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))
    
    # Print the authenticated user
    me = await client.get_me()
    print(me)

def read_words(file_path):
    try:
        with open(file_path, 'r') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return set()

# Read the sentiment word lists
positive_words = read_words(positive_words_file)
negative_words = read_words(negative_words_file)
booster_inc_words = read_words(booster_inc_words_file)
booster_decr_words = read_words(booster_decr_words_file)
negation_words = read_words(negation_words_file)

async def fetch_messages():
    await authenticate()

    try:
        # Get the group entity using the group username
        group_entity = await client.get_entity(group_username)
    except errors.UsernameNotOccupiedError:
        print(f"The username {group_username} does not exist.")
        return
    except errors.UsernameInvalidError:
        print(f"The username {group_username} is invalid.")
        return

    # Fetch messages from the Telegram group
    try:
        messages = await client.get_messages(group_entity, limit=200)
    except errors.ChatIdInvalidError:
        print(f"Invalid group ID: {group_entity.id}. Please check the group ID and try again.")
        return
    except errors.ChatWriteForbiddenError:
        print(f"Bot does not have access to the group: {group_entity.id}. Ensure the bot has been invited and has necessary permissions.")
        return
    except ValueError as e:
        print(f"Error: {e}. Please check the group ID and ensure the bot has access to the group.")
        return
    
    # Initialize score counters
    positive_total = 0
    negative_total = 0
    zero_total = 0
    
    # Analyze each message
    for message in messages:
        if message.message is None:
            continue  # Skip if message content is None

        words = re.findall(r'\w+', message.message.lower())
        score = 0
        
        for i, word in enumerate(words):
            if word in positive_words:
                word_score = 1
                # Check for boosters and negation
                if i > 0:
                    prev_word = words[i - 1]
                    if prev_word in booster_inc_words:
                        word_score *= 2
                    elif prev_word in booster_decr_words:
                        word_score *= 0.5
                    elif prev_word in negation_words:
                        word_score *= -1
                score += word_score
            elif word in negative_words:
                word_score = -1
                # Check for boosters and negation
                if i > 0:
                    prev_word = words[i - 1]
                    if prev_word in booster_inc_words:
                        word_score *= 2
                    elif prev_word in booster_decr_words:
                        word_score *= 0.5
                    elif prev_word in negation_words:
                        word_score *= -1
                score += word_score
        
        # Determine sentiment for the message
        if score > 0:
            positive_total += 1
        elif score < 0:
            negative_total += 1
        else:
            zero_total += 1
    
    # Print summary
    total_messages = positive_total + negative_total + zero_total
    print("\nSummary:")
    print(f"Total messages analyzed: {total_messages}")
    print(f"Positive messages: {positive_total} ({(positive_total/total_messages)*100:.2f}%)")
    print(f"Negative messages: {negative_total} ({(negative_total/total_messages)*100:.2f}%)")
    print(f"Neutral messages: {zero_total} ({(zero_total/total_messages)*100:.2f}%)")

# Run the Telegram client
with client:
    client.loop.run_until_complete(fetch_messages())