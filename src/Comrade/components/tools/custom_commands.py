import discord
from discord.ext import commands
import async_timeout
import asyncio
from discord.ext.commands.view import StringView

from cosmo import *

from utils.checks import isNotThreat, isOP


class CustomCommands(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.check(isNotThreat())
    async def macro(self, ctx, *, cmds):
        '''
        Macro runner for Comrade.

        Split command queries by comma.
        SPECIAL COMMANDS:
        use "wait" to delay execution of a function by a set time
        use "say" to send a message with some content

        ex. $c macro help, wait 5, version, dmuser itchono hello sir
        '''
        async with async_timeout.timeout(MACRO_TIMEOUT):
            for i in cmds.split(","):
                i = i.strip(" ")
                try:
                    if i.split(" ")[0].lower() == "wait":
                        await asyncio.sleep(float(i.split(" ")[1]))

                    elif i.split(" ")[0].lower() == "say":
                        await ctx.send(" ".join(i.split(" ")[1:]))
                    else:
                        i = BOT_PREFIX + i
                        view = StringView(i)
                        ctx2 = commands.Context(
                            prefix=BOT_PREFIX, view=view, bot=self.bot, message=ctx.message)
                        view.skip_string(BOT_PREFIX)

                        invoker = view.get_word()
                        ctx2.invoked_with = invoker
                        ctx2.command = self.bot.all_commands.get(invoker)

                        await self.bot.invoke(ctx2)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    await ctx.send(f"Command execution timed out after {MACRO_TIMEOUT} seconds.")
                    break
                except BaseException:
                    await ctx.send(f"Input {i} could not be processed.")
                    break

    @commands.command()
    @commands.guild_only()
    @commands.check(isNotThreat())
    async def showscripts(self, ctx):
        '''
        Lists all Cosmo scripts in the server
        '''
        e = discord.Embed(
            title=f"Scripts for {ctx.guild.name}",
            colour=discord.Colour.from_rgb(
                *
                DBcfgitem(
                    ctx.guild.id,
                    "theme-colour")))

        scrs = DBfind(CMD_COL, {"server": ctx.guild.id})

        e.add_field(name="Cosmo Scripts", value=", ".join(
            [i["name"] for i in scrs if i["type"] == "cosmo"]), inline=True)
        e.add_field(name="Macros", value=", ".join(
            [i["name"] for i in scrs if i["type"] == "macro"]), inline=True)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP())
    async def removescript(self, ctx, name):
        '''
        Deletes a Cosmo script
        '''
        DBremove_one(CMD_COL, {"server": ctx.guild.id, "name": name})
        await reactOK(ctx)

    @commands.command()
    @commands.guild_only()
    @commands.check(isNotThreat())
    async def showscript(self, ctx, name):
        '''
        Shows a Cosmos script
        '''
        if c := DBfind_one(CMD_COL, {"server": ctx.guild.id, "name": name}):

            (cmd, cmdType) = c["cmd"], c["type"]
            if cmdType == "cosmo":
                await ctx.send(f"```{cmd}```")
            else:
                # macro
                await ctx.send(f"`{cmd}`")

        else:
            await reactX(ctx)
            await ctx.send(f"No script with name {name} was found.", delete_after=10)

    @commands.command()
    @commands.guild_only()
    @commands.check(isNotThreat())
    async def run(self, ctx, *, args):
        '''
        Runs a macro, or a stored Cosmo script, with a given name, and optional arguments [SPLIT BY COMMA].

        ex. $c run script1 param1, param2

        Built on Victor's Cosmo language and Comrade's macro system
        '''
        args = args.split(" ")
        name = args.pop(0)
        args = "".join([i.strip(" ") for i in args]).split(",")  # strip spaces

        if c := DBfind_one(CMD_COL, {"server": ctx.guild.id, "name": name}):

            (cmd, cmdType) = c["cmd"], c["type"]

            if cmdType == "cosmo":

                splt_line_lst = token_list(cmd)

                try:
                    if splt_line_lst[0][-1] == "]" and splt_line_lst[0][0] == "[":

                        params = [
                            i.strip(" ") for i in splt_line_lst[0].strip("[").strip("]").split(",")]
                        # inject args

                        if len(args) == len(params):
                            splt_line_lst[0] = str(
                                [f'{params[i]}={args[i]}' for i in range(len(args))]).replace("'", "")
                        else:
                            await ctx.send(f"Not enough arguments for this script. Needs to be of form `{BOT_PREFIX}run {name} {splt_line_lst[0].strip('[').strip(']')}`")
                            return

                except BaseException:
                    pass

                # get env from first line
                env = get_env(splt_line_lst)
                # parse program
                ast = parse(splt_line_lst)
                # interp ast with given env

                try:
                    cmds = await asyncio.wait_for(interp(ast, env, extCall=True), timeout=INTERP_TIMEOUT)
                    await self.macro(ctx, cmds=",".join(cmds))

                except asyncio.TimeoutError:
                    await ctx.send(f"Program interpretation failed. Check to see if you have any infinite loops running.")

            else:
                await self.macro(ctx, cmds=cmd)  # Raw macro
        else:
            await reactX(ctx)
            await ctx.send(f"No script with name {name} was found.", delete_after=10)

    @commands.command()
    @commands.guild_only()
    async def newscript(self, ctx, command_name, *, command):
        '''
        Creates a command using a Cosmo script or Comrade Macro

        INPUT FORMAT: $c newscript <command name> ```<CODE GOES HERE>```
        OR $c newscript <command name> <MACRO goes here>

        '''
        if command[:3] == "```" and command[-3:] == "```":
            DBupdate(CMD_COL,
                     {"server": ctx.guild.id,
                      "name": command_name},
                     {"server": ctx.guild.id,
                      "name": command_name,
                      "cmd": command.strip("```"),
                      "type": "cosmo"})
        else:
            DBupdate(CMD_COL, {"server": ctx.guild.id, "name": command_name}, {
                     "server": ctx.guild.id, "name": command_name, "cmd": command, "type": "macro"})
        await reactOK(ctx)