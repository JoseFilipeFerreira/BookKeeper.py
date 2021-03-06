import discord
import asyncio
import json
from discord.ext import commands
import os
from os import path
import subprocess
import random
import markovify

bot = commands.Bot(command_prefix = '-')

bot.remove_command('help')

text_model = None

QUOTES_PATH = './quotes/'

def main():
    global text_model
    with open("geral.txt", "r") as f:
        text = f.read()
        text_model = markovify.NewlineText(text)

    with open(QUOTES_PATH + 'best.json', 'r', encoding="utf8") as file:
        bot.best_quotes = json.load(file)['array']

    bot.run(open('auth').readline().rstrip())

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='-generate'))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_message(message):
	await bot.process_commands(message)


@bot.command(pass_context=True)
async def saver(ctx, name):
#dowload all messages from a discord server
    appInfo = await bot.application_info()
    if ctx.message.author != appInfo.owner:
        bot.say("Invalid User!")
        return
    await bot.delete_message(ctx.message)
    
    saved  = []
    channels = ctx.message.server.channels
    for channel in channels:
        print(channel.name)
        nSaved = 0
        size = 100
        lastMessage = None
        while size == 100:
            messages = bot.logs_from(
                channel,
                before = lastMessage,
                limit = 100)
            size = 0
            async for x in messages:
                size += 1
                if x.content != "":
                    saved.append(x.content)
                lastMessage = x
            nSaved += size
            print(nSaved)

    with open("{}.txt".format(name), "a") as f:
        for q in saved:
            f.write(q + '\n')

@bot.command(pass_context=True)
async def generate(ctx):
    global text_model
    msg = text_model.make_sentence(tries = 100)
    await bot.say(msg.replace("@", "(a)"))

@bot.command(pass_context=True)
async def best(ctx):
    await bot.say(random.choice(bot.best_quotes))

@bot.command(pass_context=True)
async def add(ctx, *quote):
    quote = ' '.join(word for word in quote)
    appInfo = await bot.application_info()
    owner = appInfo.owner
    #TODO optimize one day
    if ctx.message.author != owner:
        await bot.say('Invalid user')
    elif len(quote) < 1:
        await bot.say('Invalid quote')
    else:
        with open(QUOTES_PATH + 'best.json', 'w', encoding='utf8') as file:
            d = {'array': bot.best_quotes}
            json.dump(d, file, indent=4)
        bot.best_quotes.append(quote)
        await bot.say('quote "'+ quote +'" added to file')

main()