import discord
from discord.ext import commands
import time
from Joueur import Joueur, Couleur

participants = []
vote_active = [False]
debug = True
MAX_USERS = 10

class AngelBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.get_channel(1136482449694658602)

    @commands.command()
    async def register(self, ctx):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT * FROM users WHERE id = ?", (ctx.author.id,))
        result = await cursor.fetchone()
        
        if result is not None:
            await ctx.send(f"Tu es déja connecté {ctx.author.name}")
            await ctx.message.add_reaction("❌")
            return
        
        await cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (ctx.author.id, ctx.author.name, 10, False, True))
        await ctx.message.add_reaction("✅")
        await self.bot.db.commit()

    @commands.command()
    async def show_points(self, ctx):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT * FROM users")
        result = await cursor.fetchone()

        if result is not None:
            await self.channel.send(f"{ctx.author.name} a {result[2]} points")
        else:
            await self.channel.send(f"{ctx.author.name} tu n'es pas inscrit !")

    @commands.command()
    async def list_users(self, ctx):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT * FROM users")
        result = await cursor.fetchall()

        if result == []:
            await ctx.send("No users in database")

        embed = discord.Embed(description=f"".join(f'<@{i[0]}>' for i in result))
        await ctx.send(embed=embed)

    @commands.command()
    async def add_match(self, ctx, blue : str, red : str):
        if vote_active[0] == True:
            await ctx.send(f"Un vote est déja actif")
            time.sleep(2)
            await ctx.channel.purge(limit=2)
            return
        
        if isinstance(blue, str) and isinstance(red, str):
            vote_active[0] = True
            message = await ctx.send(f"Gamba Time !! Time to vote. Qui va gagner ? {blue} ou {red} ?")
            await message.add_reaction("🔵")
            await message.add_reaction("🔴")
        else:
            await ctx.send(f"Le nom des équipes sont invalides")

    @commands.command()
    async def winner(self, ctx, winner : str):
        cursor = await self.bot.db.cursor()
        if vote_active[0] == False:
            await ctx.send(f"Aucun vote actif")
            return
        
        if isinstance(winner, str):
            print(winner)
            if winner == "blue":
                for participant in participants:
                    if participant.couleur == Couleur.BLEU:
                        await cursor.execute("SELECT * FROM users WHERE id = ?", (participant.id,))
                        result = await cursor.fetchone()
                        print(result)
                        await cursor.execute("UPDATE users SET points = ?, inscrit = ? WHERE id = ?", (result[2] + 2, False, participant.id))

            elif winner == "red":
                for participant in participants:
                    if participant.couleur == Couleur.ROUGE:
                        await cursor.execute("SELECT * FROM users WHERE id = ?", (participant.id,))
                        result = await cursor.fetchone()
                        print(result)
                        await cursor.execute("UPDATE users SET points = ?, inscrit = ? WHERE id = ?", (result[2] + 2, False, participant.id))

            else:
                await ctx.send(f"Le nom de l'équipe est invalide")
        else:
            await ctx.send(f"Le nom de l'équipe est invalide")

        participants.clear()
        await cursor.execute("UPDATE users SET inscrit = ?", (False,))
        vote_active[0] = False

        await ctx.channel.purge(limit=4)
        await ctx.send(f"Bien joué à ceux qui se font la pallete Ez")

        await self.bot.db.commit()


    @commands.command()
    async def leaderboards(self, ctx):
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT * FROM users ORDER BY points DESC")
        result = await cursor.fetchall()
        
        texte = ""

        if len(result) < MAX_USERS:
            for idx, participant in enumerate(result):
                texte += f"{idx + 1}. {participant[1]} : {participant[2]} points\n"

        else:
            for idx, participant in enumerate(result[:MAX_USERS]):
                texte += f"{idx + 1}. {participant[1]} : {participant[2]} points\n"

        print(texte)
        await ctx.channel.purge(limit=1)
        await ctx.send(texte)


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        cursor = await self.bot.db.cursor()

        if user == self.bot.user:
            return
        
        if vote_active == False:
            await self.channel.send(f"Aucun vote actif")
            return
        
        await cursor.execute("SELECT * FROM users WHERE id = ?", (user.id,))
        result = await cursor.fetchone()

        if result is not None:
            if result[2] > 0:
                if reaction.emoji == "🔵":
                    if result[3] == False:
                        participants.append(Joueur(result[0], Couleur.BLEU))
                        await cursor.execute("UPDATE users SET points = ?, inscrit = ? WHERE id = ?", (result[2] - 1, True, user.id))
                        await self.channel.send(f"{result[1]} a voté pour l'équipe bleu")
                    else:
                        await self.channel.send(f"{result[1]} tu as déja voté")
                elif reaction.emoji == "🔴":
                    if result[3] == False:
                        participants.append(Joueur(result[0], Couleur.ROUGE))
                        await cursor.execute("UPDATE users SET points = ?, inscrit = ? WHERE id = ?", (result[2] - 1, True, user.id))
                        await self.channel.send(f"{result[1]} a voté pour l'équipe rouge")
                    else:
                        await self.channel.send(f"{result[1]} tu as déja voté")
            else:
                await self.channel.send(f"{result[1]} tu n'as pas assez de points")
        else:
            await self.channel.send(f"{user.name} tu n'es pas inscrit !")
        await self.bot.db.commit()


    # Commandes Debug/Vérif
    @commands.command(active=debug)
    async def show_player_db(self, ctx):
        print(ctx.author.id)

        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT * FROM users WHERE id = ?", (ctx.author.id,))
        result = await cursor.fetchone()
        print(result)

    @commands.command(active=debug)
    async def set_points(self, ctx, points, player):
        cursor = await self.bot.db.cursor()
        await cursor.execute("UPDATE users SET points = ? WHERE username = ?", (points, player))
        await self.bot.db.commit()

async def setup(bot):
    await bot.add_cog(AngelBot(bot))