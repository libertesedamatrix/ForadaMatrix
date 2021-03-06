#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import config
from threading import Thread
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import functools
from functools import wraps #parte do send_action
from telegram.ext import messagequeue as mq
from telegram import ParseMode #parte de textos padronizados, Negrito(bold * *), Itálico(Italic _ _), Mono(Mono ``)
from telegram.ext.dispatcher import run_async #Performance Optimizations
from emoji import emojize
import json
import requests
from pprint import pprint as pp
import time
#from telegram import Bot
#from yandex_translate import YandexTranslate


# Habilitar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#use isso em cada callback que for usar chat_id para não precisar colocar o id do chat
#chat_id= update.message.chat_id

"""
translate = YandexTranslate(config.yandex_key)
translate = YandexTranslate('Your API key here.')

bot = Bot(
    token=config.TOKEN,
    base_url=config.TG_API_URL
)
"""

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

API_URL = (config.API_URL)
API_URL_LOC = config.API_URL_LOC

@restricted
def start(update, context):
    update.message.reply_text('Olá, Bot Iniciado no Grupo/Chat com sucesso.')

def help(update, context):
    update.message.reply_text('Ainda não disponível')

#novas callbacks


#tradutor
def check(update, context):
    input = update.message.text
    input = translate.translate(input, 'en-pt')
    update.message.reply_text(input['text'][0])
#regras
def regras(update, context):
    update.message.reply_text(text=config.MensagemRegras, use_aliases=True, parse_mode=ParseMode.MARKDOWN)

#pesquisar climas
def query_api(city):
    try:
        print(API_URL.format(city, API_KEY))
        data = requests.get(API_URL.format(city, API_KEY)).json()
    except Exception as exc:
        print(exc)
        data = None
    return data


def weather_check(update, context, args):
    try:
        user_says = " ".join(args)
        resp = query_api(user_says)
        pp(resp)
        chat_id = update.message.chat_id
        temp = int(round((resp['main']['temp'])))
        pressure = resp['main']['pressure']
        country = resp['sys']['country']
        desc = resp['weather'][0]['description']
        resp = ("Temperatura atual em %s, %s é %s C. \nPressão Atmosférica %s hPa\n%s" % (user_says, country, temp, pressure, desc.capitalize()))
        context.bot.send_message(chat_id=chat_id, text=resp)
    except KeyError:
        resp = ("Cidade não encontrada. Nós não temos dados climáticos para %s. Por Favor tente novamente usando uma cidade diferente. " % user_says)
        context.bot.send_message(chat_id=chat_id, text=resp)

def getLocation(update, context, user_data):
    msg = update.message
    user_data['msg'] = msg
    user_data['id'] = update.update_id
    update.message.reply_text('Checando clima por coordenadas geográficas lat: {}, lng: {}'.format(
        msg.location.latitude, msg.location.longitude))
    try:
        print(API_URL_LOC.format(msg.location.latitude, msg.location.longitude, API_KEY))
        resp = requests.get(API_URL_LOC.format(msg.location.latitude, msg.location.longitude, API_KEY)).json()
        pp(resp)
        chat_id = update.message.chat_id
        temp = int(round((resp['main']['temp'])))
        name = resp['name']
        pressure = resp['main']['pressure']
        country = resp['sys']['country']
        desc = resp['weather'][0]['description']
        resp = ("Temperatura atual em %s, %s é %s C. \nPressão atmosférica %s hPa\n%s" % (
        name, country, temp, pressure, desc.capitalize()))
        context.bot.send_message(chat_id=chat_id, text=resp)
    except Exception as exc:
        print(exc)
        resp = None

#pesquisar filmes
def title(update, context):
    #declare variables to store required values
    c_id = update.message.chat_id
    m_txt = update.message.text.replace('/titulo','').lstrip().rstrip()
    
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
        context.bot.send_message(chat_id=c_id,text='Pesquisa de Filmes no IMDB\nLinha de pesquisa válida somente em Inglês\nTente Novamente com argumentos corretos')
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
            framed_response = "Título: " + resp_txt['Title'] + "\n" + "Ano: " + resp_txt['Year'] + "\n" + "Data de Lançamento: " + resp_txt['Released'] + "\n" + "Resumo do Filme(Plot): " + resp_txt['Plot'] + "\n"         
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

def ratings(update, context):
    movie_name = update.message.text
    print(movie_name)
    movie_rating = getRating(movie_name)
    message_text = f"Classificação para {movie_name} é {movie_rating}"
    context.bot.send_message(chat_id=update.message.chat_id, text = message_text)


def getRating(movieTitle):
    url = 'http://www.omdbapi.com'
    data = {'apikey':config.OMDBAPI,'t':movieTitle}
    response = requests.get(url,data)
    return str(response.json().get("imdbRating"))

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
    title_handler = CommandHandler('titulo',title)
    dp.add_handler(title_handler)

    dp.add_handler(CommandHandler('clima',weather_check, pass_args=True))
    dp.add_handler(MessageHandler(Filters.location,
                                  getLocation,
                                  pass_user_data=True))

    search_handler = CommandHandler('pesquisarfilme',pesquisarfilme)
    dp.add_handler(search_handler)

    #ratings_handler = MessageHandler(Filters.text, ratings)
    ratings_handler = CommandHandler('imdbclassificar', ratings)
    dp.add_handler(ratings_handler)

    #dp.add_handler(MessageHandler(Filters.text, callback=check))

    dp.add_handler(CommandHandler('regras',regras))
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

while True:
    print('Looping the bot')
    time.sleep(2) # 2 second delay