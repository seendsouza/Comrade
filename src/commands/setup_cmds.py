from utils.utilities import *
from utils.mongo_interface import *

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    def setupuser(self, user: discord.Member):
        '''
        Configures a new user for use
        '''
        d = {"user": user.id}
        d["name"] = user.name
        d["nickname"] = user.nick if user.nick else user.name
        d["threat level"] = 0
        d["banned words"] = []
        d["kick votes"] = []
        d["mute votes"] = []
        d["server"] = user.guild.id
        d["muted"] = False
        d["OP"] = False
        d["stop pings"] = False
        d["stop images"] = False
        d["daily weight"] = DEFAULT_DAILY_COUNT if not user.bot else 0
        d["bot"] = user.bot
        d["last online"] = "Now" if str(user.status) == "online" else "Never"
        d["highest guess streak"] = 0

        return d

    @commands.command()
    async def createChannel(self, ctx: commands.Context, channelname: str):
        '''
        Creates a channel, and gives the user who created it full permissions over it.
        '''
        


    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def reloadusers(self, ctx: commands.Context):
        '''
        POTENTIALLY DESTRUCTIVE. repopulates the UserData collection on Atlas with default values.
        '''
        for user in ctx.guild.members:
            # each user is stored, themselves each as a dictionary
            updateUser(self.setupuser(user))
        await reactOK(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def updatealluserfields(self, ctx: commands.Context, fieldname,
                                  value):
        '''
        updates all fields of users to some given value.
        '''
        await ctx.channel.trigger_typing()

        for user in ctx.guild.members:
            # each user is stored, themselves each as a dictionary

            d = getUser(user.id, ctx.guild.id)

            try:
                d[fieldname] = int(value)
            except:
                d[fieldname] = value

            updateUser(d)

        await reactOK(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def user(self, ctx: commands.Context, tgt, cfgitem, value=None):
        '''
        Configures a user, mentioned by ping, id, or nickname. Leave value as none to delete field.
        '''
        u = getUser((await extractUser(ctx, tgt)).id, ctx.guild.id)

        if not value:
            try:
                del u[cfgitem]
                updateUser(u)
                await delSend(ctx, "User config value deleted.")
            except:
                await delSend(ctx, "Value was not found.")

        else:
            try:
                u[cfgitem] = eval(value)
            except:
                u[cfgitem] = value
            updateUser(u)

            await reactOK(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def cfg(self, ctx: commands.Context, cfgitem, value=None):
        '''
        Modifies a value in Comrade's configuration. Leave value blank to delete the field.
        '''
        c = getCFG(ctx.guild.id)

        if not value:
            try:
                del c[cfgitem]
                updateCFG(c)
                await delSend(ctx, "Config value deleted.")
            except:
                await delSend(ctx, "Value was not found.")

        else:
            try:
                c[cfgitem] = eval(value)
            except:
                c[cfgitem] = value
            updateCFG(c)

            await reactOK(ctx)

    @commands.command()
    @commands.guild_only()
    async def cfgstatus(self, ctx: commands.Context):
        '''
        Sends an embed providing a dump of all Comrade configuration data for this server.
        '''
        c = getCFG(ctx.guild.id)

        s = ""

        for k in c:
            if k != "_id":
                s += str(k) + ": " + str(c[k]) + "\n"

        e = discord.Embed(title="Comrade Configuration for {}".format(
            ctx.guild.name),
                          description=s,
                          colour=discord.Colour.from_rgb(*THEME_COLOUR))
        e.set_thumbnail(url=ctx.guild.icon_url)

        await ctx.send(embed=e)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def resetcfg(self, ctx: commands.Context):
        '''
        POTENTIALLY DESTRUCTIVE. Resets the configuration file for a server back to a default state. 
        '''
        d = {"_id": ctx.guild.id}
        d["last daily"] = "2020-05-04"  # default "time = 0" for comrade
        d["joke mode"] = True
        d["kick requirement"] = 6
        d["mute requirement"] = 4
        d["lethality override"] = 0
        d["zahando threshold"] = 3
        d["banned words"] = []
        d["announcements channel"] = -1
        d["meme channel"] = -1
        d["bot channel"] = -1
        d["log channel"] = -1
        d["emote directory"] = -1
        updateCFG(d)

        await reactOK(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def injectEmotes(self, ctx: commands.Context):
        '''
        Inserts each image located inside the a folder called emotes and uploads it to the custom emotes channel in the server.
        '''
        for n in os.listdir("emotes"):
            with open("emotes/{}".format(n), "rb") as f:
                msg = await ctx.send(file=discord.File(f))
                url = msg.attachments[0].url
                c = await getChannel(ctx.guild, "emote directory")
                await c.send(n[:n.index(".")] + "\n" + url)
