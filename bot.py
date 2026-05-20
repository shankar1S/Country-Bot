import os

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


load_dotenv()

TOKEN = os.getenv("token")


def get_country_info(country: dict) -> str:
    currencies = ", ".join(country.get("currencies", {}).keys()) or "Not available"
    capitals = ", ".join(country.get("capital", [])) or "Not available"
    languages = ", ".join(country.get("languages", {}).values()) or "Not available"

    return f"""Common Name: {country["name"]["common"]}

Official Name: {country["name"]["official"]}

Currency used: {currencies}

Capital: {capitals}

Languages used: {languages}
"""


async def send_country(update: Update, country: dict) -> None:
    flag_url = country.get("flags", {}).get("png")
    if flag_url:
        await update.message.reply_photo(flag_url)
    await update.message.reply_text(get_country_info(country))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        """Hello   ¡Hola!  Bonjour  Ciao    你好(nǐ hǎo)    Dia     Olá  नमस्ते (namaste)  Здравствуйте (Zdravstvuyte) こんにちは (Kon’nichiwa)    Χαίρετε (Chaírete)

Hey, This is InforNation, I'm a countrybot and I'm here to help you find the country you are looking for.
InforNation will also provide you some basic Information about that particular Nation.

You can search country you want by name, code, region, sub-region, currency, capital city, language.

You can use the following commands:
/name - To search the country by name.
/capital - To search the country by capital.
/language - To search the country by language.
/currency - To search the country by currency.
/countrycode - To search the country by countrycode. Search by cca2, ccn3, cca3 or cioc country code.

Use the /help command for more instructions and information regarding the bot."""
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        """Hey This is InforNation, I'm a countrybot and I'm here to provide you information and interesting facts about any country in the world.
I'm always here to help you.

You can use the following commands:
/help - To access this message containing the basic information and instructions
/name - Search by country name
/capital - Search by capital city
/language - Search by language
/currency - Search by currency
/countrycode - Search by cca2, ccn3, cca3 or cioc country code"""
    )


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search_mode"] = "name"
    await update.message.reply_text("Please enter the name of a country to get information about it.")


async def capital(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search_mode"] = "capital"
    await update.message.reply_text("Please enter the capital of a country to get information about it.")


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search_mode"] = "language"
    await update.message.reply_text("Please enter the language of a country to get information about it.")


async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search_mode"] = "currency"
    await update.message.reply_text("Please enter the currency to get information about the country.")


async def countrycode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["search_mode"] = "alpha"
    await update.message.reply_text("Please enter the country code to get information about the country.")


async def search_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_mode = context.user_data.get("search_mode")
    query = update.message.text.strip()

    if not search_mode:
        await update.message.reply_text("Please choose a search command first, such as /name or /capital.")
        return

    response = requests.get(f"https://restcountries.com/v3.1/{search_mode}/{query}", timeout=15)

    if response.status_code != 200:
        await update.message.reply_text("Error, no such country was found. Please check the spelling once.")
        return

    data = response.json()
    if search_mode == "name":
        exact_matches = [
            country
            for country in data
            if country.get("name", {}).get("common", "").lower() == query.lower()
        ]
        data = exact_matches or data

    for country in data:
        await send_country(update, country)


def main() -> None:
    if not TOKEN:
        raise RuntimeError("Missing bot token. Add token=YOUR_TELEGRAM_BOT_TOKEN to the .env file.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("name", name))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CommandHandler("capital", capital))
    app.add_handler(CommandHandler("countrycode", countrycode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_country))

    app.run_polling()


if __name__ == "__main__":
    main()
