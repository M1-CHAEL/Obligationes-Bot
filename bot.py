import discord
from discord.ext import commands
import random
import os

# -------------------------------
# Discord Bot Setup
# -------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------------
# Ontology: Define nouns and their properties
# Each noun maps to a dictionary with "category" and "subtype".
# TODO: Expand this and align with scholastic principles.
# -------------------------------
ontology = {
    "dogs": {"category": "animal", "subtype": "mammal"},
    "cats": {"category": "animal", "subtype": "mammal"},
    "birds": {"category": "animal", "subtype": "avian"},
    "trees": {"category": "plant", "subtype": "tree"},
    "rivers": {"category": "natural", "subtype": "water"},
    "mountains": {"category": "natural", "subtype": "landform"},
    "books": {"category": "manmade", "subtype": "literature"},
    "ideas": {"category": "abstract", "subtype": "concept"}
}

# -------------------------------
# Vocabulary Data
# TODO: Expand this as additional logic layers are implemented.
# -------------------------------
nouns = list(ontology.keys())
quantifiers = ["All", "No", "Some"]
verbs = ["are", "are not"]

# -------------------------------
# Game Sessions (per Discord channel)
# -------------------------------
game_sessions = {}

# -------------------------------
# Helper Functions
# -------------------------------

def make_statement():
    """
    Create a randomized logical statement from the defined vocabulary.
    """
    quant = random.choice(quantifiers)
    verb = random.choice(verbs)
    noun1 = random.choice(nouns)
    noun2 = random.choice(nouns)

    while noun2 == noun1:
        noun2 = random.choice(nouns)

    text = f"{quant} {noun1} {verb} {noun2}."
    return {
        "text": text,
        "noun1": noun1,
        "noun2": noun2,
        "quant": quant,
        "verb": verb
    }

def determine_truth_value(statement_data):
    """
    Basic (placeholder) logical evaluation based on ontology properties.
    TODO:
      - Expand to include first-order logic principles.
      - Replace with formal logic engine (e.g., Z3).
    """
    noun1 = statement_data["noun1"]
    noun2 = statement_data["noun2"]
    quant = statement_data["quant"]
    verb = statement_data["verb"]

    props1 = ontology[noun1]
    props2 = ontology[noun2]
    cat1, sub1 = props1["category"], props1["subtype"]
    cat2, sub2 = props2["category"], props2["subtype"]

    if quant == "All":
        if verb == "are":
            # True if noun1 is a subset of noun2 (same category + subtype)
            return (cat1 == cat2) and (sub1 == sub2)
        else:
            # True if categories are completely disjoint
            return cat1 != cat2

    elif quant == "No":
        # Equivalent to "All X are not Y"
        return cat1 != cat2

    elif quant == "Some":
        if verb == "are":
            # True if they share the same category
            return cat1 == cat2
        else:
            # True if different categories or different subtypes within same category
            return cat1 != cat2 or sub1 != sub2

    return False

# -------------------------------
# Discord Bot Game Logic
# -------------------------------

@bot.command()
async def start(ctx):
    """
    Starts a new game session for the channel.
    """
    if ctx.channel.id in game_sessions:
        await ctx.send("A game is already in progress in this channel!")
        return

    statement_data = make_statement()
    intended = determine_truth_value(statement_data)
    statement_data["intended"] = intended

    game_sessions[ctx.channel.id] = {
        "statement": statement_data,
        "score": 0
    }

    intended_str = "affirm" if intended else "deny"
    await ctx.send(
        f"{ctx.author.mention}, the positor says: '{statement_data['text']}'\n"
        f"Do you !affirm or !deny this statement? (Intended answer: {intended_str})"
    )

async def process_response(ctx, answer_bool):
    """
    Process the user's answer (!affirm or !deny).
    """
    if ctx.channel.id not in game_sessions:
        await ctx.send("No active game in this channel.")
        return

    session = game_sessions[ctx.channel.id]
    statement_data = session["statement"]

    if answer_bool == statement_data["intended"]:
        session["score"] += 1
        await ctx.send(f"{ctx.author.mention}, your response is correct. Current score: {session['score']}.")
    else:
        await ctx.send(f"{ctx.author.mention}, your response is incorrect. You lose!")
        del game_sessions[ctx.channel.id]
        return

    new_statement = make_statement()
    new_statement["intended"] = determine_truth_value(new_statement)
    session["statement"] = new_statement
    intended_str = "affirm" if new_statement["intended"] else "deny"

    await ctx.send(
        f"Next statement: '{new_statement['text']}'\n"
        f"Do you !affirm or !deny? (Intended answer: {intended_str})"
    )

@bot.command()
async def affirm(ctx):
    """
    User affirms the given statement.
    """
    await process_response(ctx, True)

@bot.command()
async def deny(ctx):
    """
    User denies the given statement.
    """
    await process_response(ctx, False)

# -------------------------------
# Run the bot (uses environment variable for token)
# -------------------------------
bot.run(os.getenv("DISCORD_BOT_TOKEN"))

