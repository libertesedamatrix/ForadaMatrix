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
    import feedparser, html2text, json, datetime
    from loguru import logger
except ImportError as err:
    print(f"Falhou ao importar módulos requeridos: {err}")

import logging
import os
import sys
from threading import Thread
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps #parte do send_action
import telegram.bot#parte onde precisa para o sistema de inundação(flood)
from telegram.ext import messagequeue as mq
from telegram import ParseMode #parte de textos padronizados, Negrito(bold * *), Itálico(Italic _ _), Mono(Mono ``)
from telegram.ext.dispatcher import run_async #Performance Optimizations
#from mwt import MWT
from emoji import emojize

# Habilitar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


#decorators
#Este decorador parametrizado permite sinalizar diferentes ações dependendo do tipo de resposta do seu bot. Desta forma, os usuários terão um feedback similar do seu bot, como seria de um ser humano real.


#Restringir o acesso a um manipulador (decorador)
LISTA_DE_ADMINS = [673021454, 702068435]

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        #username_id = update.effective_user #bot.get_chat
        if user_id not in LISTA_DE_ADMINS:
            #update.message.reply_text('Acesso não autorizado negado para {} ID: {}.'.format(username_id ,user_id))
            update.message.reply_text('Acesso não autorizado negado para ID: {}.'.format(user_id))
            print("Acesso não autorizado negado para {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator


def findat(msg):
    # from a list of texts, it finds the one with the '@' sign
    for i in msg:
        if '&' in i:
            return i

# Defina alguns manipuladores de comando. Estes geralmente levam os dois argumentos bot e
# atualização Os manipuladores de erro também recebem o objeto TelegramError levantado com erro.
@restricted
def start(update, context):
    update.message.reply_text('Olá, Bot Iniciado no Grupo/Chat com sucesso.')

def help(update, context):
    update.message.reply_text('Help!')

#novos comandos

#
#@send_action(ChatAction.TYPING)
#def callback_divulgar(context):
#    pass
#    context.bot.send_message(chat_id='-1001192265900', text='_LISTA DE CANAIS RECOMENDADOS_\n_CLIQUE NO NOME ESPECÍFICO PARA SER REDIRECIONADO_\n \n[Matrix The End](https://www.youtube.com/channel/UCrrlO-rjaqvXXK2U_p0C8tg)\n \n[REDE HUMBERTO VOLTS]\n[Humberto Volts](https://www.youtube.com/channel/UCM9hlzGLtByT7awBPBdOBpA)\n[Como Vencer Todas!](https://www.youtube.com/channel/UC3UFn2vXKfZBzH_VDgDBnPg)\n[Notícias e Política!](https://www.youtube.com/channel/UCMQLbIUB_akIl4_7NvNr7RA)\n \n[REDE THIAGO LIMA]\n[DESPERTE. - Thiago Lima-](https://www.youtube.com/channel/UCwQdXKdraEfNZv9b4IWFn5g)\n[Thiago Lima](https://www.youtube.com/channel/UCul7RtuTpGhIW1m3sXfzuEw)\n \n[REDE RÔMULO MARASCHIN]\n[Rômulo Maraschin](https://www.youtube.com/channel/UCSyUhW3u3JazIT3VtE4nCEw)\n[Firmeza da Verdade](https://www.youtube.com/channel/UCr0NQAx7C64fOrNxVdc8gYA)\n \n[REDE CIENCIA DE VERDADE/AFONSO]\n[Ciencia de Verdade](https://www.youtube.com/channel/UCDoPuIvx88nh69fS5VJCNWg)\n[Ciencia de Verdade/Patreon](https://www.patreon.com/cienciadeverdade)\n \n[Além da Nuvem/ADN](https://www.youtube.com/channel/UCJ-TrcQTTN3fcGBjT-I8MJw)\n \n[REDE DAVID/ENCARANDO]\n[Encarando o Sobrenatural Oficial](https://www.youtube.com/channel/UCyhRfD3HkB-0VbFA1prxjxw)\n[Encarando o Sobrenatural](https://www.youtube.com/channel/UCxR9jCW0ZFSWL9_BQJwlaaQ)\n \n[REDE BRUNO ALVES/TERRA PLANA]\n[MISTÉRIOS DO MUNDO](https://www.youtube.com/channel/UCkVPPZdJn6gTL5H7Fk78NGg)\n[Bruno Alves Mistérios](https://www.youtube.com/channel/UC2y-0ktlJMua_T01CcOx7rQ)\n \n[REDE MAGNÉTICAMENTE/ESTUDOS BÍBLICOS]\n[MagneticaMente](https://www.youtube.com/channel/UCRq5D2B8Pu2OTiwAcmZ6I9w)\n[Flat Land](https://www.youtube.com/channel/UClAcCO4eWYj00MBUIaSYhSw) [Antiofídico777](https://www.youtube.com/channel/UCvYt8Qk0UTkvJ-yNXBbinAw)\n \n[Terra Plana USA](https://www.youtube.com/channel/UC6Wgo5A5GRKMJe4yyR7_0Kw)\n \n[REDE GUARDEI A FÉ]\n[Guardei a Fé](https://www.youtube.com/channel/UCHWjmG-Ce93VNcNZMMUyGQQ)\n[GF News!](https://www.youtube.com/channel/UCY0f7GEJVh2H3d5t0AHEW6A)\n \n[Verdade Absoluta André Bastos](https://www.youtube.com/channel/UCGfC41o4e2PlerPmrrWVTTw)\n \n[REDE MARCOS PAULO GOES]\n[Marcos Paulo Goes](https://www.youtube.com/channel/UClTvLvg3b8S4BKAi6g91tyw)\n[Marcos Paulo Goes](https://www.youtube.com/channel/UCSYknUZG9VREGJfvtTIrohA)\n \n[Danizudo/Ocultismo-Músicas](https://www.youtube.com/channel/UCKaULi5ypurpvXaUPXbN4dQ)\n \n[DunaiJunior/Ocultismo-Músicas](https://www.youtube.com/channel/UC-9j5lIBJ0gRGYXy08-Vx6w)\n \nDOAÇÕES [EM BREVE]\n`PAYPAL`[INDISPONÍVEL]\n`PICPAY`[INDISPONÍVEL]\n \n`PATROCINIO`[INDISPONÌVEL/EM BREVE/*]\n`Versão: bit/0.1`\n \n**Confira nossos cursos de idiomas gratuitos nas recomendações do CursosGrátisqueFuncionam(@CGqFBOT)**', parse_mode=ParseMode.MARKDOWN)
#    context.bot.send_message(chat_id='-1001192265900', text='[REDE PRISCA CÔCO]\n[Prisca Côco](https://www.youtube.com/channel/UCaYS9ja-CaIFHB4PC7DCuIA)\n[Prisca Conta](https://www.youtube.com/channel/UCE2-3hzK6PespWfN-9mRiew)\n \n[#MANOTOKIO2020](https://www.youtube.com/channel/UCIkQMUV-X2HJpUEYH95yrxg)\n \n[Jemima Gomes - FORA DO SISTEMA](https://www.youtube.com/user/jemimagondim)\n \n[Neemias Gomes - FORA DO SISTEMA!](https://www.youtube.com/channel/UCzZdVXmqtwTtAWtxk6NCUqw)\n \n[VERDADE REVELADA](https://www.youtube.com/user/verdaderevelada1)\n \n[Ultimos Acontecimentos HOJE](https://www.youtube.com/channel/UCRr-cQB5CeIhdnhwocrUR5w)\n \n', parse_mode=ParseMode.MARKDOWN)
#    context.bot.send_message(chat_id='-1001192265900', text='_Cursos Grátis - 10 minutos de Estudos por dia_ \n _Clique nos respectivos cursos[em azul] no qual deseja participar_\n \n[Curso de Hebraico Grátis](https://www.duolingo.com/o/vdqbdg)\n **Primeiro Idioma Criado e o Principal**\n`Precisa do Inglês básico`\n \n[Curso de Grego Grátis](https://www.duolingo.com/o/kdfxhx)\n**Idioma no qual a Biblia também foi escrita**\n`Precisa do Inglês básico`\n \n[Curso de Inglês Grátis](https://www.duolingo.com/o/vfsqut)\n \n[Curso de Espanhol Grátis](https://www.duolingo.com/o/xkukdb)\n \nSe preferir já vem com conta feita.\ncontate o administrador dos grupos na plataforma de estudos.\n \nBrevemente novos cursos.\n**Confira os canais recomendados nas recomendações do ForadaMatrix(@ForadaMatrixBOT)**', parse_mode=ParseMode.MARKDOWN)
#    update.message.reply_text('**BIBLIOTECAS**\n \n [BibliotecaJPL](t.me/bibliotecajpl)\n`quase 3000 livros em PDFs disponibilizados`\n \n[Biblioteca - Humberto Volts](t.me/bibliotecahumbertovolts)\n`Bibliotecas de audios sobre informações e conhecimentos do Humberto Volts/Grupo/Membros` ', parse_mode=ParseMode.MARKDOWN)
#
@restricted
def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Faltam argumentos!')
            return

        # Add job to queue
        job = context.job_queue.run_once(callback_divulgar, due, context=chat_id)
        #and callback_canaisyt2  callback_cursos
        context.chat_data['job'] = job

        update.message.reply_text('Temporizador definido com sucesso!')

    except (IndexError, ValueError):
        update.message.reply_text('Use: /tempodivulgar <segundos>.')

@restricted
def unset(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('Você não tem mensagem(ns) ativa(s) no temporizador.')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Temporizador removido com sucesso!')    
#

#check if bot is online
@restricted
#@escrevendo
def callback_checkbotison(update, context):
    pass
    update.message.reply_text('`Estou online.`', use_aliases=True, parse_mode=ParseMode.MARKDOWN)
#check chat_id
def showchat_id(self, bot, update):
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text='chat id: {}'.format(chat_id))

def callback_bibliotecas(update, context):
    pass
    update.message.reply_text('#Bibliotecas\n_BIBLIOTECAS_\n_Clique nos nomes para ser Redirecionado_\n \n[Biblioteca em Nuvem](t.me/bibliotecajpl)\n`quase 3000 livros em PDFs disponibilizados`\n \n[Biblioteca - Humberto Volts](t.me/bibliotecahumbertovolts)\n`Bibliotecas de audios sobre informações e conhecimentos do Humberto Volts/Grupo(s)/Membros`\n \n [EMPREENDIMENTOS COLETIVOS - A CURA É A UNIÃO!](https://t.me/joinchat/MEGw_Uk8WqekcCZBfsGlFQ)\n`GRUPO DE CURA ESPIRITUAL ATRAVÉS DA ENERGIA MACRO DO UNIVERSO - ESSA ENERGIA ESTÁ PRESENTE EM TODOS NÓS E É O PONTO DE CONEXÃO COM O CRIADOR` ', parse_mode=ParseMode.MARKDOWN)

#callback cursos
@send_action
def callback_cursos(update, context):
    pass
    update.message.reply_text('_Cursos Grátis - 10 minutos de Estudos por dia_ \n _Clique nos respectivos cursos[em azul] no qual deseja participar_ \n \n [Curso de Hebraico Grátis](https://www.duolingo.com/o/vdqbdg) \n **Primeiro Idioma Criado e o Principal** \n `Precisa do Inglês básico` \n \n [Curso de Grego Grátis](https://www.duolingo.com/o/kdfxhx) \n **Idioma no qual a Biblia também foi escrita** \n `Precisa do Inglês básico` \n \n [Curso de Inglês Grátis](https://www.duolingo.com/o/vfsqut) \n \n [Curso de Espanhol Grátis](https://www.duolingo.com/o/xkukdb) \n \n Se preferir já vem com conta feita. \n contate o administrador dos grupos na plataforma de estudos. \n \n Brevemente novos cursos. \n **Confira os canais recomendados nas recomendações do ForadaMatrix(@ForadaMatrixBOT)**', parse_mode=ParseMode.MARKDOWN)


def regraslink(update, context):
    pass
    update.message.reply_text("👉 https://t.me/grupohumbertovolts/126998 👈🏿\n     ☝🏿                                                                           👆", use_aliases=True)

#def echo(update, context):
#    """Eco a mensagem do usuário."""
#    update.message.reply_text(update.message.text)


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
                    # Go to the top of subscription_manager.opml file.
                    data_file.seek(0)
                    # Dump the new json structure to the file.
                    json.dump(items, data_file, indent=2)
                    data_file.truncate()
            data_file.close()
    except IOError:
        logger.debug("date_title(): Falhou ao abrir arquivos requeridos.")


def feed_to_md(state, name, feed_data):
    """A Function for converting rss feeds into markdown text.
    state: Either `set` or `None`: To execute date_title()
    name: Name of RSS feed object: eg: hacker_news
    feed_data: Data of the feed: URL and post_date from subscription_manager.opml"""
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
        logger.debug(f"Rodando date_title para subscription_manager.opml em {datetime.datetime.now()}")
        date_title("subscription_manager.opml", name, title)
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


def check_feeds(update, context):
    """Checks the provided feeds from subscription_manager.opml for a new post."""
    chat_id = update.message.chat_id
    job = context.job
    logger.debug("Checando Feeds...")
    feeds = file_reader("subscription_manager.opml.opml", "r")
    for name, feed_data in feeds.items():
        results = feed_to_md(None, name, feed_data)
        # Checking if title is the same as title in subscription_manager.opml file.
        # If the same, pass; do nothing.
        if ((feed_data["date_title"]) == (results[0]["title"])):
            pass
        elif ((feed_data["date_title"]) != (results[0]["title"])):
            results = feed_to_md("set", name, feed_data)
            logger.debug(f"Rodando feed_to_md at {datetime.datetime.now()}")
            rss_msg = f"""[{results[0]["title"]}]({results[0]["url"]})"""
            context.bot.send_message(chat_id="update.message.chat_id", text=rss_msg, parse_mode="Markdown")
    logger.debug("Dormindo por 30 mins...")


#def callback_enochbook(update, context):
#    text = update.message.text
#    text = text.lower()
#    if text == "enoque":
#        context.bot.send_document(chat_id=-'1001192265900', document=open('books/O_Livro_de_Enoque_Apocrifo.pdf','rb'))
#        update.message.reply_text('Documento: O Livro de Enoque Apócrifo | Enviado com Sucesso!') 


#def add_group(update, context):
def entrougrupo(update, context):
    for member in update.message.new_chat_members:
        #update.message.reply_text("\nShalom {firstname} {lastname} ({username}).  *BOT?: *`{isonobot}`\nSeja muito bem vindo(a) ao canal @grupohumbertovolts.\nQue a Tranquilidade do Criador esteja com você!.\n *Entrou por link do convite?: *`[em breve]`".format(firstname=member.first_name, lastname=member.last_name, username=member.username, isonobot=member.is_bot), parse_mode=ParseMode.MARKDOWN)
        update.message.reply_text("\nShalom {fullname} ({username}).\nSeja muito bem vindo(a) ao canal/grupo @grupohumbertovolts.\nQue a Tranquilidade do Criador esteja com você!.\n*Entrou por link do convite?:*`[em breve]` | *BOT?:* `{isonobot}`".format(fullname=member.full_name, username=member.username, isonobot=member.is_bot), parse_mode=ParseMode.MARKDOWN, use_aliases=True, disable_web_page_preview=True)

def saiugrupo(update, context):
    for member in update.message.left_chat_member:
        update.message.reply_text("{fullname} ({username}) saiu do grupo.".format(fullname=member.full_name, username=member.username))


def stop_and_restart():
    """Pare com cuidado o atualizador e substitua o processo atual por um novo"""
    u.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)

@restricted
def restart(update, context):
    update.message.reply_text('Bot reiniciando...')
    Thread(target=stop_and_restart).start()


#def callback_admins(bot, chat_id):
 #return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
 #if user.id in admins(bot, chat.id):

#def livroenoch(update, context):
#    for member in update.message.new_chat_members:
#        text = update.message.text
#        text = text.split(" ")
#    if "enoque" in text:
#        context.bot.send_document(chat_id=-'1001192265900', document=open('books/O_Livro_de_Enoque_Apocrifo.pdf','rb'))


def error(update, context):
    logger.debug(error)
    logger.warning('Update "%s" caused error "%s"', update, context.error)





def main():
    # Crie o atualizador e passe o token do seu bot.
    # Certifique-se de definir use_context = True para usar os novos callbacks baseados em contexto
    # Poste a versão 12, isso não será mais necessário
    #logger.start("file_{time}.log", rotation="300 MB")
    u = Updater("SeuTokenAqui", use_context=True)
    j = u.job_queue

    # Obtem o despachante para registrar manipuladores
    dp = u.dispatcher

    # em comandos diferentes - responde no Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))


    
    #j.run_repeating(callback_canaisyt, interval=10800, first=0)

    #dp.add_handler(MessageHandler(Filters.regex('enoque'), callback_enochbook))
    dp.add_handler(CommandHandler("checar", callback_checkbotison))
    dp.add_handler(CommandHandler("chatid", showchat_id))
    dp.add_handler(CommandHandler("bibliotecas", callback_bibliotecas))
    #dp.add_handler(CommandHandler("cursos", callback_cursos))
    #dp.add_handler(MessageHandler(Filters.text, livroenoch)) #certo
    #dp.add_handler(MessageHandler(Filters.regex('enoque'), enochbook)) #errado
    dp.add_handler(CommandHandler("regras", regraslink))
    entrou_grupo_handle = MessageHandler(Filters.status_update.new_chat_members, entrougrupo)
    dp.add_handler(entrou_grupo_handle)
    saiu_grupo_handle = MessageHandler(Filters.status_update.left_chat_member, saiugrupo)
    dp.add_handler(saiu_grupo_handle)
    dp.add_handler(CommandHandler('reiniciar', restart, filters=Filters.user(username='@AASaints')))

    
    #dp.add_handler(CommandHandler("tempodivulgar", set_timer,
    #                              pass_args=True,
    #                              pass_job_queue=True,
    #                              pass_chat_data=True))
    #dp.add_handler(CommandHandler("parardivulgar", unset, pass_chat_data=True))
    #no noncommand ou seja, mensagem - echo a mensagem no telegrama
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # registra todos os erros
    dp.add_error_handler(error)

    POLLING_INTERVAL = 0.2
    # Inicia o Bot
    u.start_polling()

    # Execute o bot até que você pressione Ctrl-C ou o processo receba SIGINT,
    # SIGTERM ou SIGABRT. Isso deve ser usado a maior parte do tempo, desde
    # start_polling() é non-blocking e irá parar o bot graciosamente.
    u.idle()


if __name__ == '__main__':
    main()
