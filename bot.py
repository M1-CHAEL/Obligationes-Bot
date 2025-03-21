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
# Ontology: Define our nouns with richer properties.
# Each noun is mapped to a dictionary with keys "category" and "subtype".
### (This needs to be expanded on and confirmed with to scholasticism) ###
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

# Data: sample nouns, quantifiers, and verbs.
### (This also needs to be expanded on as additional truth values are added) ####
nouns = list(ontology.keys())
quantifiers = ["All", "No", "Some"]
verbs = ["are", "are not"]

# Global game state per channel.
game_sessions = {}

# -------------------------------
# Helper functions
# -------------------------------
def make_statement():
    quant = random.choice(quantifiers)
    verb = random.choice(verbs)
    noun1 = random.choice(nouns)
    noun2 = random.choice(nouns)
    # Ensure the two nouns are different.
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
### (This needs to be expanded to include first order logic principals of scholasticism) ###
def determine_truth_value(statement_data):
    noun1 = statement_data["noun1"]
    noun2 = statement_data["noun2"]
    quant = statement_data["quant"]
    verb = statement_data["verb"]
    
    # Retrieve properties from the ontology.
    props1 = ontology[noun1]
    props2 = ontology[noun2]
    cat1, sub1 = props1["category"], props1["subtype"]
    cat2, sub2 = props2["category"], props2["subtype"]
    
    if quant == "All":
        if verb == "are":
            # "All X are Y" is true if X is a subset of Y.
            # Here, we assume that holds only if both category and subtype match.
            return (cat1 == cat2) and (sub1 == sub2)
        else:
            # "All X are not Y" is true if X and Y are completely disjoint,
            # i.e. they have different categories.
            return cat1 != cat2
    elif quant == "No":
        # "No X are Y" is equivalent to "All X are not Y".
        return cat1 != cat2
    elif quant == "Some":
        if verb == "are":
            # "Some X are Y" is true if there is some intersection.
            # We'll consider this true if X and Y share at least the same category.
            return cat1 == cat2
        else:
            # "Some X are not Y": true if either they are in different categories or,
            # if same category, their subtypes differ (i.e. not all X are Y).
            if cat1 != cat2:
                return True
            else:
                return sub1 != sub2
    return False

# -------------------------------
# Discord Bot Game Logic
# -------------------------------
@bot.command()
async def start(ctx):
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
    await ctx.send(f"{ctx.author.mention}, the positor says: '{statement_data['text']}'\nDo you !affirm or !deny this statement? (Intended answer: {intended_str})")

async def process_response(ctx, answer_bool):
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
    await ctx.send(f"Next statement: '{new_statement['text']}'\nDo you !affirm or !deny? (Intended answer: {intended_str})")

@bot.command()
async def affirm(ctx):
    await process_response(ctx, True)

@bot.command()
async def deny(ctx):
    await process_response(ctx, False)

@bot.command()
async def test_truth(ctx):
    samples = [make_statement() for _ in range(5)]
    output = "Truth Test Samples:\n"
    for s in samples:
        truth = determine_truth_value(s)
        output += f"Statement: '{s['text']}' => Intended: {'True (affirm)' if truth else 'False (deny)'}\n"
    await ctx.send(output)

# Run the bot (replace YOUR_BOT_TOKEN with your actual token)
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
