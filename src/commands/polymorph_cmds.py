from utils.utilities import *
from utils.mongo_interface import *
from polymorph.text_gen import *
from polymorph.model_gen import *
from polymorph.data_compressor import *

import time

'''
POLYMORPH

N-gram based user mimicry tool developed for use with Comrade
'''

class Polymorph(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        self.models = {} # local model store
        self.localcache = {} # message cache

        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        When bot is loaded
        '''
        # load all messages from servers

        print("Loading message caches for all servers:")

        for g in self.bot.guilds:
            self.localcache[g.id] = []
            successcount = 0
            for c in g.channels:
                if cache := getcache(c.id): 
                    self.localcache[g.id] += cache
                    successcount += 1

            if self.localcache[g.id]:
                await log(g, "Message cache loaded with {} messages".format(len(self.localcache[g.id])))
            else:
                await log(g, "No message cache loaded for this server!")

            print(f"\t{g.name}: {successcount} channels loaded")

    @commands.command(aliases = ["gen"])
    @commands.guild_only()
    async def polymorph(self, ctx: commands.Context, number: typing.Optional[int] = 15,*, target: str):
        '''
        Generates text from model of a user and outputs it to a channel.
        If the model has not yet been built, it builds a model based on the last cached channel.
        If you want the model for a certain channel, run [buildmodel] in that channel.
        '''
        if number > 100 or number < 0: await ctx.send("No")
        
        elif user := await extractUser(ctx, target):
            c = self.bot.get_cog("Echo")

            try:
                model = self.models[(user.id, ctx.guild.id)]
                await c.echo(ctx, text(model, number), str(user.id), deleteMsg=False)

            except:
                await ctx.send("Model is not yet built, it will take a bit longer to produce this first iteration of text.")
                await self.buildmodel(ctx, target)
                
                try:
                    model = self.models[(user.id, ctx.guild.id)]
                    await c.echo(ctx, text(model, number), str(user.id), deleteMsg=False)
                except:
                    pass
    
    @commands.command()
    @commands.guild_only()
    async def buildmodel(self, ctx: commands.Context, target: str, n=2, silent=False):
        '''
        Builds the n-gram model for a user based on all cached messages in a server.
        By default, n=2.
        This command can be called manually to change the n number.
        '''
        await ctx.trigger_typing()

        t_start = time.perf_counter()

        if self.localcache[ctx.guild.id]:
            if user := await extractUser(ctx, target):
                
                # check to see if we have too many models cached
                if len(self.models) >= RAM_LIMIT:
                    self.models.pop(list(self.models.keys()).pop())
                    if not silent: await ctx.send("Model cache full. Freeing up cache...")
                    await ctx.trigger_typing()

                msgs = [m["content"] for m in self.localcache[ctx.guild.id] if m["author"] == user.id]
                model = modelfrommsgs(msgs, n=1) # construct 2-gram model

                self.models[(user.id, ctx.guild.id)] = model
                # load model into user cache

                if not silent: await ctx.send("Model for {} built in {:.3f}s.".format(user.display_name, time.perf_counter()-t_start))
        else:
            await reactX(ctx)
            await ctx.send("Model could not be built - no message cache has been loaded for this server. \nUse `{}extractChannel <channel>` to load a channel".format(BOT_PREFIX))
            

    @commands.command()
    @commands.guild_only()
    async def extractChannel(self, ctx: commands.Context, channel : discord.TextChannel = None):
        '''
        Extracts messages in channel and uploads it to MongoDB for use with text generation.
        '''
        if not channel: channel = ctx.channel
        msgs = []

        await ctx.send("Collecting all info for {}. This will take some time.".format(channel.mention))

        msgs = await channel.history(limit=None).flatten()

        ex = [{"author":m.author.id, "content":m.content} for m in msgs]

        self.localcache[ctx.guild.id] += ex

        tx = compressCache(ex, 3)
        fillcache(ctx.channel.id, tx)
        await ctx.send("{} successfully cached and uploaded.".format(channel.mention))
        await log(ctx.guild, "Channel extracted: {}".format(channel.mention))
        await reactOK(ctx)

    @commands.command()
    @commands.guild_only()
    async def modelSize(self, ctx: commands.Context):
        '''
        Returns the size of the current model store.
        '''
        await ctx.send("Current storing {} models locally.".format(len(self.models)))

    @commands.command()
    @commands.guild_only()
    async def channelCacheStatus(self, ctx: commands.Context):
        '''
        Returns information about the currently cached channel
        '''
        if self.localcache[ctx.guild.id]:
            await ctx.send("Message cache loaded with {} messages.".format(len(self.localcache[ctx.guild.id])))
        else:
            await ctx.send("No message cache loaded for this server!")
  
    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def injectcache(self, ctx: commands.Context, filename=None):
        '''
        Injects .dat file into active cache from local file (in /polymorph directory), or clears it.
        '''
        try:
            with open("polymorph/{}.dat".format(filename), "rb") as f:
                self.localcache[g.id] += pickle.load(f)
            await reactOK(ctx)
        except:
            await ctx.send("Error loading local cache.")
