import discord
import openai
import requests
from io import BytesIO
from discord.ext import commands
from discord import app_commands
from secret import OPENAI_API_KEY, BOT_TOKEN

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix = "?", intents = intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")
    
    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral = True)

bot = Bot()

#Set up the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Define a function to log the bot out of Discord and close the connection
async def logout():
    await bot.logout()

# Define a function to close the bot's connection to Discord
async def close():
    await bot.close()

# Use DALL-E to generate an answer to a question
def generate_image(prompt):
    response = openai.Image.create(
        model="image-alpha-001",
        prompt=prompt,
        n=1,
        size="256x256",
        response_format="url",
    )
    return response["data"][0]["url"]

# Use GPT-3 to generate an answer to a question
async def generate_answer(question):
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=question,
        max_tokens=1024,
        temperature=0.75,
    )
    return response["choices"][0]["text"]

@bot.hybrid_command(name = "restart", with_app_command = True, description = "Restart the bot")
@commands.is_owner()
async def restart(ctx: commands.Context):
    # Log the bot out of Discord and close the connection
    await logout()
     
    # Start the bot again
    bot.run(BOT_TOKEN)
    await ctx.reply('Bot successfully restarted!')

@bot.hybrid_command(name = "shutdown", with_app_command = True, description = "Shut down the bot")
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    # Close the bot's connection to Discord
    await ctx.reply('Shutting down...')
    await close()

@bot.hybrid_command(name = "imagine", with_app_command = True, description = "Bayangkan bila..")
async def imagine(ctx: commands.Context, *, prompt: str):
    await ctx.defer(ephemeral = True)
    # Generate an image from the given prompt
    image_url = generate_image(prompt)

    # Download the image from the URL
    response = requests.get(image_url)

    # Create a file object from the image data
    file = discord.File(BytesIO(response.content), filename="image.png")

    # Send a message with the image attached
    await ctx.reply(file=file)

@bot.hybrid_command(name="ask", with_app_command = True, description="Kamu naenya?")
async def ask(ctx: commands.Context, *, question: str):
    await ctx.defer(ephemeral = True)
     # Generate an answer to the question using GPT-3
    answer = await generate_answer(question)

    # Respond to the slash command with the answer
    await ctx.reply(content=answer)

bot.run(BOT_TOKEN)