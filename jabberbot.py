#!/usr/bin/env python2.7
# vim:fileencoding=koi8-r:nomodified:ts=4:expandtab

# requirex xmpppy

# The original program:
# http://xmpppy.sourceforge.net/examples/bot.py

import sys
import xmpp
import random

room="ninux.org@chat.jabber.ninux.org" 
room="prova@chat.jabber.ninux.org" 
roomu = ""

probability = 1 #percent
eatmessages = 40
quotestxt = 'quotes.txt'
global botusername
botusername = "trollbot0"

quotes = set()
f = open(quotestxt)
for line in f:
    if len(line.strip()) > 0:
        quotes.add(line.strip())
f.close()


commands={}
i18n={'it':{},'en':{}}
########################### user handlers start ##################################
i18n['en']['HELP']="This is example jabber bot.\nAvailable commands: %s"
def helpHandler(user,command,args,mess):
    lst=commands.keys()
    lst.sort()
    return "HELP",', '.join(lst)

i18n['en']['EMPTY']="%s"
i18n['en']['TROLLBOT']='%s'
def trollbotHandler(user,command,args,mess):
    print "[TROLLBOT]: triggered!"
    addHandler(user,"add","%s %s" % (command, args), mess)
    mychoice = random.choice(list(quotes))
    mychoicesplit = [ w.strip() for w in mychoice.split(" ") ]
    if len(mychoicesplit) == 1 and mychoicesplit[0].lower().startswith("trollbot"):
        return
    try:
        if mess.getType() == "chat":
            uname = str(user).split('@')[0]
        else:
            uname = str(user).split('/')[1].split('@')[0]
        def tro(word):
            if word.startswith("trollbot"):
                return uname
            else:
                return word
        mychoicefiltered = [tro(w) for w in mychoicesplit]
    except IndexError:
        mychoicefiltered = mychoicesplit[1:]


    return "TROLLBOT", " ".join(mychoicefiltered)

def trollbot0Handler(user,command,args,mess):
    return trollbotHandler(user,command,args,mess)

i18n['en']['ADD']='%s'
def addHandler(user,command,args,mess):
    argsplit = [ s.strip() for s in args.split(' ') if len(s.strip()) > 0 ]
    if len(argsplit) == 0 or (len(argsplit) == 1 and (argsplit[0].lower().startswith("trollbot") or argsplit[0] == "None")):
        return "ADD", "not added"
    comargs = " ".join(argsplit)
    if comargs in quotes:
        return "ADD", "not added"
    f = open(quotestxt, 'a')
    try:
        f.write(comargs + u"\n")
    except UnicodeEncodeError:
        pass
    f.close()
    quotes.add(comargs)
    return "ADD", "added: %s" % comargs

i18n['en']['HU']='%s'
def huHandler(user,command,args,mess):
    res = "%s huuuuuuuuuuuuuuuu!!!" % args
    addHandler(user, "add", res, mess)
    return "HU", res

i18n['en']['INVITE']='%s'
def inviteHandler(user,command,args,mess):
    if mess.getType() == "groupchat":
        return 
    global eatmessages
    eatmessages = 40
    global botusername
    if args.find("@") == -1:
            roomj="%s@chat.jabber.ninux.org/%s" % (args, botusername)
    else:
            roomj="%s/%s" % (args, botusername)
    conn.send(xmpp.Presence(to=roomj))
    return "INVITE", "invitation accepted"

i18n['en']['SCIO']='%s'
def scioHandler(user,command,args,mess):
    if mess.getType() != "groupchat":
        return
    user = mess.getFrom()
    global botusername
    try:
        roomr = str(user).split('/')[0]
    except IndexError:
        return
    roomj="%s/%s" % (roomr, botusername)
    conn.send(xmpp.Presence(to=roomj, typ='unavailable'))
    return "SCIO", "via!"

i18n['en']['GOTO']='%s'
def gotoHandler(user,command,args,mess):
    return scioHandler(user,command,args,mess)

i18n['en']['REREAD']='%s'
def rereadHandler(user,command,args,mess):
    if mess.getType() == "groupchat":
        return
    i = 0
    newquotes = set()
    f = open(quotestxt)
    for line in f:
        if len(line.strip()) > 0:
            newquotes.add(line.strip())
            i+=1
    f.close()
    global quotes
    quotes = set()
    quotes = newquotes
    return "REREAD", "reread %d lines" % (i,)

########################### user handlers stop ###################################
############################ bot logic start #####################################
i18n['en']["UNKNOWN COMMAND"]='Unknown command "%s". Try "help"'
i18n['en']["UNKNOWN USER"]="I do not know you. Register first."

def messageCB(conn,mess):
    global eatmessages 
    if eatmessages >=0:
        eatmessages = eatmessages - 1
        print "[TROLLBOT]: ate message (%d left)" % eatmessages
        return
    #global roomu
    #conn.send(xmpp.Presence(to=roomu))
    user=mess.getFrom()
    try:
        if str(user).lower().find("trollbot") != -1:
            print "[TROLLBOT]: avoiding auto-trigger"
            return
    except IndexError:
        pass
    user.lang='en'      # dup
    text=mess.getBody()
    if text and text.find(' ')+1: command,args=text.split(' ',1)
    else: command,args=text,''
    cmd=command
    if command: 
        cmd=command.lower()

    #reply=("TROLLBOT",cmd)
    #reply=commands['TROLLBOT'](user,command,args,mess)

    if commands.has_key(cmd): 
        reply=commands[cmd](user,command,args,mess)
    else:
        rint = random.randint(0,100)
        if (text and text.find("troll") != -1) or mess.getType() == "chat" or rint <= probability:
            print "[TROLLBOT]: triggering! (%d / %d [%s])" % (rint, probability, mess.getType())
            reply = trollbotHandler(user,command,args,mess)
            if reply[0] == 'NONE':
                return
        else:
            print "[TROLLBOT]: not triggered... (%d / %d)" % (rint, probability)
            return

    if type(reply)==type(()):
        key,args=reply
        if i18n[user.lang].has_key(key): pat=i18n[user.lang][key]
        elif i18n['en'].has_key(key): pat=i18n['en'][key]
        else: pat="%s"
        if type(pat)==type(''): reply=pat%args
        else: reply=pat(**args)
    else:
        try: reply=i18n[user.lang][reply]
        except KeyError:
            try: reply=i18n['en'][reply]
            except KeyError: pass
    #if reply: conn.send(xmpp.Message(mess.getFrom(),reply))
    if reply: 
        if mess.getType() == "groupchat":
            try:
                user=mess.getFrom()
                roomr = str(user).split('/')[0]
            except IndexError:
                roomr = room
            msg = xmpp.Message(roomr, reply)
            msg.setType('groupchat')
            conn.send(msg)
        else:
            msg = xmpp.Message(mess.getFrom(), reply)
            conn.send(msg)

for i in globals().keys():
    if i[-7:]=='Handler' and i[:-7].lower()==i[:-7]: commands[i[:-7]]=globals()[i]

############################# bot logic stop #####################################

def StepOn(conn):
    try:
        conn.Process(1)
    except KeyboardInterrupt: return 0
    return 1

def GoOn(conn):
    while StepOn(conn): pass

if len(sys.argv)<3:
    print "Usage: bot.py username@server.net password"
else:
    jid=xmpp.JID(sys.argv[1])
    user,server,password=jid.getNode(),jid.getDomain(),sys.argv[2]

    conn=xmpp.Client(server)#,debug=[])
    conres=conn.connect()
    if not conres:
        print "Unable to connect to server %s!"%server
        sys.exit(1)
    if conres<>'tls':
        print "Warning: unable to estabilish secure connection - TLS failed!"
    authres=conn.auth(user,password)
    if not authres:
        print "Unable to authorize on %s - check login/password."%server
        sys.exit(1)
    if authres<>'sasl':
        print "Warning: unable to perform SASL auth os %s. Old authentication method used!"%server
    conn.RegisterHandler('message',messageCB)
    conn.sendInitPresence()
    print "Bot started."
    roomu="%s/%s" % (room, user)
    conn.send(xmpp.Presence(to=roomu))
    botusername = user
    GoOn(conn)

