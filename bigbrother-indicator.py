#!/usr/bin/env python
#_*_coding:utf8_*_

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GObject
import signal
#import os
import time
from threading import Thread
#import sys
#import pip
from gi.repository import Notify
#import datetime
from datetime import datetime

now = datetime.now()
IdPerson = '3793'
dbhost='192.168.27.82'
dbuser='sa'
dbpassword='123'
dbname="ACS"

APPINDICATOR_ID = 'bigbrother-indicator'
indicator = appindicator.Indicator.new(APPINDICATOR_ID, '/usr/share/unity/icons/panel-shadow.png', appindicator.IndicatorCategory.OTHER)


#def install(package):
#    pip.main(['install', package])

try:
    import pymssql
except ImportError:
    install('pymssql')

conn = pymssql.connect(host=dbhost, user=dbuser, password=dbpassword, database=dbname)
cursor = conn.cursor()
cursor.execute("SELECT [Name] FROM [ACS].[dbo].[PERSONS] WHERE [IdPerson]='"+IdPerson+"';")
for i in cursor.fetchall():
    Name = i[0]

def main():
#    indicator = appindicator.Indicator.new(APPINDICATOR_ID, 'whatever', appindicator.IndicatorCategory.SYSTEM_SERVICES)
#    indicator = appindicator.Indicator.new(APPINDICATOR_ID, gtk.STOCK_INFO, appindicator.IndicatorCategory.OTHER)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    indicator.set_label("0 "+u"hour", APPINDICATOR_ID)
    update = Thread(target=show_hours)
    update.setDaemon(True)
    update.start()
    GObject.threads_init()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    gtk.main()

def build_menu():
    menu = gtk.Menu()
    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu

def show_hours():
    secondsin = 0.0
    secondsout = 0.0
    totalhours = 0.0
    totalminutes = 0.0
    while True:
        time.sleep(3)
#        worktime = str(round(totalhours,2))+u" часа"
        worktime = str((totalhours).is_integer())+':'+str(totalminutes)+u" часа"

        curdate = now.strftime('%Y-%m-%d')

        mytime = '2017-01-01 00:00:00'
        t2 = datetime.now() - datetime.strptime(str(mytime), '%Y-%m-%d %H:%M:%S')
        t3 = t2.total_seconds()

#         apply the interface update using  GObject.idle_add()
        GObject.idle_add(
            indicator.set_label,
            worktime, APPINDICATOR_ID,
            priority=GObject.PRIORITY_DEFAULT
            )

        cursor.execute("SELECT count(*) FROM [ACS].[dbo].[ROOMREG] WHERE [IdPerson]='"+IdPerson+"' AND ([IdRoom]='1' OR [IdRoom]='2') AND ([Command]='50' OR [Command]='51') AND CONVERT(VARCHAR(25), CurDate, 126) LIKE '" + curdate + "%';")
        for i in cursor.fetchall():
            recordscount = i[0]
        cursor.execute("SELECT DATEDIFF(SECOND,'2017-01-01 00:00:00',[CurDate]) FROM [ACS].[dbo].[ROOMREG] WHERE [IdPerson]='"+IdPerson+"' AND ([IdRoom]='1' OR [IdRoom]='2') AND [Command]='50' AND CONVERT(VARCHAR(25), CurDate, 126) LIKE '" + curdate + "%';")
        for i in cursor.fetchall():
            secondsin = secondsin + i[0]
        cursor.execute("SELECT DATEDIFF(SECOND,'2017-01-01 00:00:00',[CurDate]) FROM [ACS].[dbo].[ROOMREG] WHERE [IdPerson]='"+IdPerson+"' AND ([IdRoom]='1' OR [IdRoom]='2') AND [Command]='51' AND CONVERT(VARCHAR(25), CurDate, 126) LIKE '" + curdate + "%';")
        for i in cursor.fetchall():
            secondsout = secondsout + i[0]

        t4 = secondsout
        if recordscount % 2 != 0 :
            secondsout = secondsout + t3
       


        totalhours = ((secondsout-secondsin)/60)/60
        totalminutes = ((totalhours).is_integer()*60)-((secondsout-secondsin)/60)
        message = u'Today is ' + curdate + '\nHello ' + Name + u'\nYour work time for today is ' + worktime
        Notify.init("Big brother")
        if (totalhours).is_integer():
            Notify.Notification.new('Big brother', message,'/home/USERNAME/icon.png').show()
            Notify.uninit()

        secondsout = 0.0
        secondsin = 0.0

def quit(source):
    gtk.main_quit()

if __name__ == "__main__":
    main()
