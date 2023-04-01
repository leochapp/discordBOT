from music import *
from db import *
import os

load_dotenv(find_dotenv())

#Import des informations de connexions
token = os.environ['TOKEN']


# Connexion du BOT :
intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents, description="Bot cool fait entre pote avec amour et tendresse")
intents.members = True
intents.message_content = True
help_command = commands.DefaultHelpCommand(no_category = 'Commands')

@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user} ! ")

    tabs = get_server_info()
    tab_server_info = tabs[0]
    tab_users_info = tabs[1]

    compteur = 0

    first_fetch = True

    while True:
        # récupérer tous les noms de serveurs
        servers = client.guilds
        server_info = [(server.id,server.name) for server in servers]
        if len(tab_server_info) != len(server_info):
            for server in server_info:

                if server[1] not in tab_server_info:
                    add_server(server)

        # récupérer tous les membres de tous les serveurs

        all_members = []


        if len(all_members) != len(tab_users_info) or first_fetch==True:
            for server in servers:
                async for member in server.fetch_members():
                    user = (member.id,server.id)
                    if user not in tab_users_info:
                        add_user(member)
                    all_members.append((member.id, server.id))
            first_fetch = False

        # attendre une minute avant de récupérer à nouveau les noms et les membres des serveurs

        if compteur<10:
            compteur+=1
        else:
            tab_server_info = update_server_info()

        tab_users_info = update_users_info()

        await asyncio.sleep(60)


# Ajout des commandes du bot musique :

async def setup():
    await client.wait_until_ready()
    await client.add_cog(MusicBOT(client))

async def main():
    await asyncio.gather(
        client.start(token),
        setup(),
    )

asyncio.run(main())
