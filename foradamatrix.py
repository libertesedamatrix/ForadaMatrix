#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Este programa é dedicado ao domínio público sob a licença CC0.
#
# ESTE EXEMPLO FOI ATUALIZADO PARA TRABALHAR COM A VERSÃO BETA 12 DO PYTHON-TELEGRAM-BOT.
# Se você ainda estiver usando a versão 11.1.0, por favor, veja os exemplos em
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
Bot simples para responder mensagens do telegram.

Primeiro, algumas funções do manipulador são definidas. Então, essas funções são passadas para
Despachante e registrados em seus respectivos lugares.
Então, o bot é iniciado e é executado até pressionar Ctrl-C na linha de comando.

Uso:
Exemplo básico de Echobot, repete mensagens.
Pressione Ctrl-C na linha de comando ou envie um sinal para o processo para parar o
robô.
"""
try:
    import logging
    import os
    import sys
    from threading import Thread
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
    from functools import wraps #parte do send_action
    from telegram.ext import messagequeue as mq
    from telegram import ParseMode #parte de textos padronizados, Negrito(bold * *), Itálico(Italic _ _), Mono(Mono ``)
    from telegram.ext.dispatcher import run_async #Performance Optimizations
    from emoji import emojize
    import feedparser, html2text, json, datetime
    from loguru import logger
except ImportError as err:
    print(f"Falha ao importar os módulos necessários: {err}")

# Habilitar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


#Restringir o acesso a um manipulador (decorador)
LISTA_DE_ADMINS = [USERIDAQUI]

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        #username_id = update.effective_user #bot.get_chat
        if user_id not in LISTA_DE_ADMINS:
            #update.message.reply_text('Acesso não autorizado negado para {} ID: {}.'.format(username_id ,user_id))
            #update.message.reply_text('Acesso não autorizado negado para ID: {}.'.format(user_id)) //desativado por enquando, por conta de flood dos membros.
            print("Acesso não autorizado negado para {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped



def date_title(file_name, object_name, date_title):
    """Set the date/title of latest post from a source.
    file_name: File name to open.
    Object_name: Name of the object: feed name or twitter screen name.
    date_title: Date/title of the object being posted."""
    try:
        with open(file_name, "r+") as data_file:
            # Load json structure into memory.
            items = json.load(data_file)
            for name, data in items.items():
                if ((name) == (object_name)):
                    # Replace value of date/title with date_title
                    data["date_title"] = date_title
                    # Go to the top of feeds.json file.
                    data_file.seek(0)
                    # Dump the new json structure to the file.
                    json.dump(items, data_file, indent=2)
                    data_file.truncate()
            data_file.close()
    except IOError:
        logger.debug("date_title(): Falha ao abrir o arquivo solicitado.")

def feed_to_md(state, name, feed_data):
    """A Function for converting rss feeds into markdown text.
    state: Either `set` or `None`: To execute date_title()
    name: Name of RSS feed object: eg: hacker_news
    feed_data: Data of the feed: URL and post_date from feeds.json"""
    # Parse rss feed.
    d = feedparser.parse(feed_data["url"])
    # Target the first post.
    first_post = d["entries"][0]
    title = first_post["title"]
    summary = first_post["summary"]
    post_date = first_post["published"]
    link = first_post["link"]
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = True
    summary = h.handle(summary)
    if ((state) == ("set")):
        logger.debug(f"Rodando date_title para feeds.json em {datetime.datetime.now()}")
        date_title("feeds.json", name, title)
    results = []
    result = {"title": title, "summary": summary,
                "url": link, "post_date": post_date}
    results.append(result)
    # A list containing the dict object result.
    return results

def file_reader(path, mode):
    """Loads json data from path specified.
    path: Path to target_file.
    mode: Mode for file to be opened in."""
    try:
        with open(path, mode) as target_file:
            data = json.load(target_file)
            target_file.close()
            return data
    except IOError:
        logger.debug(f"Falhou ao abrir {path}")

def check_feeds(bot, job):
    """Checks the provided feeds from feeds.json for a new post."""
    logger.debug("Cecando Feeds...")
    feeds = file_reader("feeds.json", "r")
    for name, feed_data in feeds.items():
        results = feed_to_md(None, name, feed_data)
        # Checking if title is the same as title in feeds.json file.
        # If the same, pass; do nothing.
        if ((feed_data["date_title"]) == (results[0]["title"])):
            pass
        elif ((feed_data["date_title"]) != (results[0]["title"])):
            results = feed_to_md("set", name, feed_data)
            logger.debug(f"Rodando feed_to_md em {datetime.datetime.now()}")
            rss_msg = f"""[{results[0]["title"]}]({results[0]["url"]})"""
            bot.send_message(chat_id="Insert User ID Here.", text=rss_msg, parse_mode="Markdown")
    logger.debug("Dormindo por 30 mins...")


# Defina alguns manipuladores de comando. Estes geralmente levam os dois argumentos bot e
# atualização Os manipuladores de erro também recebem o objeto TelegramError levantado com erro.
@restricted
def start(update, context):
    update.message.reply_text('Olá, Bot Iniciado no Grupo/Chat com sucesso.')

def help(update, context):
    update.message.reply_text('*Comandos*\n\n`/tempodivulgar`\n')


def callback_bibliotecas(update, context):
    pass
    update.message.reply_text('#Bibliotecas\n_BIBLIOTECAS_\n_Clique nos nomes para ser Redirecionado_\n \n[Biblioteca em Nuvem](t.me/bibliotecajpl)\n`quase 3000 livros em PDFs disponibilizados`\n \n[Biblioteca - Humberto Volts](t.me/bibliotecahumbertovolts)\n`Bibliotecas de audios sobre informações e conhecimentos do Humberto Volts/Grupo(s)/Membros`\n \n [EMPREENDIMENTOS COLETIVOS - A CURA É A UNIÃO!](https://t.me/joinchat/MEGw_Uk8WqekcCZBfsGlFQ)\n`GRUPO DE CURA ESPIRITUAL ATRAVÉS DA ENERGIA MACRO DO UNIVERSO - ESSA ENERGIA ESTÁ PRESENTE EM TODOS NÓS E É O PONTO DE CONEXÃO COM O CRIADOR` ', parse_mode=ParseMode.MARKDOWN)


def regraslink(update, context):
    pass
    update.message.reply_text("👉 https://t.me/grupohumbertovolts/126998 👈🏿\n     ☝🏿                                                                           👆", use_aliases=True)


#def add_group(update, context):
def entrougrupo(update, context):
    for member in update.message.new_chat_members:
        #update.message.reply_text("\nShalom {firstname} {lastname} ({username}).  *BOT?: *`{isonobot}`\nSeja muito bem vindo(a) ao canal @grupohumbertovolts.\nQue a Tranquilidade do Criador esteja com você!.\n *Entrou por link do convite?: *`[em breve]`".format(firstname=member.first_name, lastname=member.last_name, username=member.username, isonobot=member.is_bot), parse_mode=ParseMode.MARKDOWN)
        update.message.reply_text("\nShalom {fullname} ({username}).\nSeja muito bem vindo(a) ao canal/grupo @grupohumbertovolts.\nQue a Tranquilidade do Criador esteja com você!.\n*Entrou por link do convite?:*`[em breve]` | *BOT?:* `{isonobot}`".format(fullname=member.full_name, username=member.username, isonobot=member.is_bot), parse_mode=ParseMode.MARKDOWN, use_aliases=True, disable_web_page_preview=True)

def saiugrupo(update, context):
    for member in update.message.left_chat_member:
        update.message.reply_text("{fullname} ({username}) saiu do grupo.".format(fullname=member.full_name, username=member.username))


def error(update, context):
    logger.debug(error)
    logger.warning('Update "%s" caused error "%s"', update, context.error)




def main():
    u = Updater("SeuTokenAqui", use_context=True)
    j = u.job_queue

    # Obtem o despachante para registrar manipuladores
    dp = u.dispatcher

    # em comandos diferentes - responde no Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("checar", callback_checkbotison))
    dp.add_handler(CommandHandler("bibliotecas", callback_bibliotecas))
    dp.add_handler(CommandHandler("regras", regraslink))
    entrou_grupo_handle = MessageHandler(Filters.status_update.new_chat_members, entrougrupo)
    dp.add_handler(entrou_grupo_handle)
    saiu_grupo_handle = MessageHandler(Filters.status_update.left_chat_member, saiugrupo)
    dp.add_handler(saiu_grupo_handle)
    j.run_repeating(check_feeds, interval=300, first=0)


    # registra todos os erros
    dp.add_error_handler(error)
    # Inicia o Bot
    u.start_polling()
    u.idle()


if __name__ == '__main__':
    main()
