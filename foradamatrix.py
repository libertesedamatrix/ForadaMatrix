#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import logging
    import os
    import sys
    import config
    from threading import Thread
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
    from functools import wraps #parte do send_action
    from telegram.ext import messagequeue as mq
    from telegram import ParseMode #parte de textos padronizados, Negrito(bold * *), Itálico(Italic _ _), Mono(Mono ``)
    from telegram.ext.dispatcher import run_async #Performance Optimizations
    from emoji import emojize
    import json
    import requests
    #from config #carregar config.py   
except ImportError as err:
    print("Falha ao importar os módulos necessários: {err}")

# Habilitar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#use isso em cada callback que for usar chat_id para não precisar colocar o id do chat
#chat_id= update.message.chat_id

#Restringir o acesso a um manipulador (decorador)
LISTA_DE_ADMINS = [config.USERID]

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

@restricted
def start(update, context):
    update.message.reply_text('Olá, Bot Iniciado no Grupo/Chat com sucesso.')

def help(update, context):
    update.message.reply_text('Ainda não disponível')

#novas callbacks
def title(update, context):
    #declare variables to store required values
    c_id = update.message.chat_id
    m_txt = update.message.text.replace('/title','').lstrip().rstrip()
    
    if(m_txt == ''):
        context.bot.send_message(chat_id=c_id,text='Título de filme inválido')
    else:
        # print("Received movie name: ",m_txt)
        context.bot.send_message(chat_id=c_id,text=callapi_title(m_txt))

def pesquisarfilme(update, context):
    #declare variables to store required values
    c_id = update.message.chat_id
    m_txt = update.message.text.replace('/pesquisarfilme','').lstrip().rstrip()

    if(m_txt == ''):
        context.bot.send_message(chat_id=c_id,text='Pesquisa de Filmes no IMDB\nLinha de pesquisa válida somente em Inglês\n Tente Novamente com argumentos corretos')
    else:
        context.bot.send_message(chat_id=c_id,text=callapi_search(m_txt))

def callapi_title(txt):
    api_base_url = 'http://www.omdbapi.com/?'
    api_key = (config.OMDBAPI)
    api_url = api_base_url+'apikey='+api_key+'&t='+txt.replace(' ','+')
    response = requests.get(api_url)
    if(response.status_code == 200):
        resp_txt = json.loads(response.content.decode('utf-8'))
        # print("Recieved response: \n",resp_txt)
        if(resp_txt['Response'] == 'True'):
            framed_response = "Title: " + resp_txt['Title'] + "\n" + "Year: " + resp_txt['Year'] + "\n" + "Release Date: " + resp_txt['Released'] + "\n" + "Plot Summary: " + resp_txt['Plot'] + "\n"         
        else:
            framed_response = "Título do filme não encontrado"
    else:
        framed_response = "Algo deu errado! Por favor, tente novamente"
    return(framed_response)

def callapi_search(txt):
    api_base_url = 'http://www.omdbapi.com/?'
    api_key = (config.OMDBAPI)
    api_url = api_base_url+'apikey='+api_key+'&s='+txt.replace(' ','+')
    framed_response = 'Filmes com o nome "'+ txt +'" neles: \n'
    response = requests.get(api_url)
    if(response.status_code == 200):
        resp_txt = json.loads(response.content.decode('utf-8'))
        # print("Recieved response: \n",resp_txt,"\n")
        # print('Search result:',resp_txt['Search'])
        if(resp_txt['Response']== 'True'):
            for t in resp_txt['Search']:
                framed_response += t['Title'] + '\n'
        else:
                framed_response = "Nenhum resultado encontrado"
    else:
        framed_response = "Algo deu errado! Por favor, tente novamente"
    return(framed_response)
# 

#def add_group(update, context):
def entrougrupo(update, context):
    for member in update.message.new_chat_members:
        #update.message.reply_text("\nShalom {firstname} {lastname} ({username}).  *BOT?: *`{isonobot}`\nSeja muito bem vindo(a) ao canal @grupohumbertovolts.\nQue a Tranquilidade do Criador esteja com você!.\n *Entrou por link do convite?: *`[em breve]`".format(firstname=member.first_name, lastname=member.last_name, username=member.username, isonobot=member.is_bot), parse_mode=ParseMode.MARKDOWN)
        update.message.reply_text("\nShalom {fullname} ({username}).\nSeja muito bem vindo(a) ao canal/grupo [-| {group_name} |-].\nQue a Tranquilidade do Criador esteja com você!.\n*Entrou por link do convite?:*`[em breve]` | *BOT?:* `{isonobot}`".format(fullname=member.full_name, username=member.username, group_name=update.message.chat.title, isonobot=member.is_bot), parse_mode=ParseMode.MARKDOWN, use_aliases=True, disable_web_page_preview=True)
        if member.get_profile_photos == True:
            update.message.reply_text("Recomendável tirar a foto do perfil")

        if member.full_name == None or member.first_name == None:
            if member.username != None:
                member.full_name = member.username

def saiugrupo(update, context):
    for member in update.message.left_chat_member:
        update.message.reply_text("{fullname} ({username}) saiu do grupo.".format(fullname=member.full_name, username=member.username))   

def callback_checkbotison(update, context):
    pass
    update.message.reply_text('`Estou online.`', use_aliases=True, parse_mode=ParseMode.MARKDOWN)

def error(update, context):
    logger.debug(error)
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    u = Updater(config.TOKEN, use_context=True)
    j = u.job_queue
    # Obtem o despachante para registrar manipuladores
    dp = u.dispatcher

    # em comandos diferentes - responde no Telegram
    dp.add_handler(CommandHandler("iniciar", start))
    dp.add_handler(CommandHandler("ajuda", help))
    dp.add_handler(CommandHandler("checar", callback_checkbotison))
    title_handler = CommandHandler('title',title)
    dp.add_handler(title_handler)

    search_handler = CommandHandler('pesquisarfilme',pesquisarfilme)
    dp.add_handler(search_handler)

    entrou_grupo_handle = MessageHandler(Filters.status_update.new_chat_members, entrougrupo)
    dp.add_handler(entrou_grupo_handle)
    saiu_grupo_handle = MessageHandler(Filters.status_update.left_chat_member, saiugrupo)
    dp.add_handler(saiu_grupo_handle)

    # registra todos os erros
    dp.add_error_handler(error)
    # Inicia o Bot
    u.start_polling()
    u.idle()

if __name__ == '__main__':
    main()
