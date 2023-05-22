import json
import discord
import asyncio
import random
class roulette:
    def __init__(self):
        self.config = self._config
        self.reward_roles = self.config['reward_roles']
        self.admins = self.config['admins']
        self.token = self.config['token']
        self.event = {"event": None, "users": {}}

    @property
    def _config(self):
        with open("config.json") as f: return json.load(f)
    
    def run_bot(self):
        bot = discord.Bot(intents=discord.Intents.all())
        
        @bot.event
        async def on_ready():
            print("Bot online")
        
        @bot.slash_command(description="verify globally")
        async def event(ctx, channel: discord.TextChannel):
            if self.event['event']: return await ctx.respond(f"event already running in {self.event['event']['url']}")
            if not ctx.author.id in self.admins: return await ctx.respond("You're not authorized to do this.", ephemeral=True)
        
            self.event['event'] = {}
            self.event['event']['channel'] = channel
            message = await channel.send("React to this message to participate in the event.")
            self.event['event']['url'] = message.jump_url
            self.event['event']['enabled'] = True
            await message.add_reaction("⭐")
            await ctx.respond(f"Started new event inside of {message.jump_url}")
        
        
        @bot.slash_command(description="Displays you the current even message.")
        async def current_event(ctx):
            if self.event["event"] is None: await ctx.respond("No current event", ephemeral=True)
            else: await ctx.respond(f"{self.event['event']['url']}", ephemeral=True)
        
        @bot.slash_command(description="Start the current event.")
        async def start(ctx):
            if not ctx.author.id in self.admins: return await ctx.respond("You're not authorized to do this.", ephemeral=True)
            if self.event["event"] is None: return await ctx.respond("No current event", ephemeral=True)
            self.event["event"]["enabled"] = False
            users = self.event["users"].copy()
            channel = self.event['event']['channel']
            self.event["users"] = {}
            self.event["event"] = {}
            await ctx.respond(f"Started the event in channel {channel.mention}", ephemeral=True)
            for i in range(sum(user["total_joins"] for user in users.values())):
                if len(users) == 1: break
                current_user = random.choice(list(users.keys()))
                users[current_user]['total_joins'] -= 1
                await channel.send(f"User <@{current_user}> got choosen which now has {users[current_user]['total_joins']} hp left")
                if users[current_user]['total_joins'] == 0:
                     del users[current_user]
                
                await asyncio.sleep(5)
            await channel.send(f"We have a winner: <@{random.choice(list(users.keys()))}>")
                    
                
                
        @bot.event
        async def on_reaction_add(reaction, user):
            if self.event["event"] is None: return
            if user.id in self.event["users"]: return
            
            if not "enabled" in self.event['event']: return
            if not self.event['event']['enabled'] and reaction.message.channel.id != self.event['event']['channel'].id and self.event['event']['url'] != reaction.message.jump_url: return
            if user == bot.user: return
            if reaction.emoji == "⭐": 
                user_roles = [role.id for role in user.roles]
                reward_count = 1 + sum(1 for role in self.reward_roles if role in user_roles)
                self.event["users"][user.id] = {"total_joins": reward_count}
                msg = await reaction.message.channel.send(f"{user.mention} joined the event using {reward_count} joins")
                await asyncio.sleep(3)
                await msg.delete()
            
        
        bot.run(self.token)
        
roulette().run_bot()