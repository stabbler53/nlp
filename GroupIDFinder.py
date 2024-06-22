from telethon import TelegramClient, errors

# Your API credentials
api_id = '14516468'
api_hash = 'bc04181a83b197ef3a524cc1087a6bf8'
group_username = 'foodrunneruia'  # Use the group's username

# Initialize Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def get_group_id(username):
    try:
        entity = await client.get_entity(username)
        print(f"Group ID for {username}: {entity.id}")
        return entity.id
    except errors.UsernameNotOccupiedError:
        print(f"The username {username} does not exist.")
    except errors.UsernameInvalidError:
        print(f"The username {username} is invalid.")
    except Exception as e:
        print(f"An error occurred: {e}")

with client:
    client.loop.run_until_complete(get_group_id(group_username))
