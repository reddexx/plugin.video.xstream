# -*- coding: utf-8 -*-
# Python 3

import sys
import os
import json
import re
import xbmc
import xbmcaddon
import xbmcgui
import time

from xbmcaddon import Addon
from xbmc import LOGDEBUG, LOGERROR
from resources.lib.config import cConfig
from resources.lib import tools
from xbmc import LOGINFO as LOGNOTICE, LOGERROR, LOGWARNING, log, executebuiltin, getCondVisibility, getInfoLabel
from resources.lib.handler.requestHandler import cRequestHandler
from urllib.parse import urlparse

LOGMESSAGE = cConfig().getLocalizedString(30166)
AddonName = xbmcaddon.Addon().getAddonInfo('name')
# xStream = xbmcaddon.Addon().getAddonInfo('id')
from xbmcvfs import translatePath
# Pfad der update.sha
NIGHTLY_UPDATE = os.path.join(translatePath(Addon().getAddonInfo('profile')), "update_sha")
# xStream Installationspfad
ADDON_PATH = translatePath(os.path.join('special://home/addons/', '%s'))

# Update Info beim Kodi Start
def infoDialog(message, heading=AddonName, icon='', time=5000, sound=False):
    if icon == '': icon = xbmcaddon.Addon().getAddonInfo('icon')
    elif icon == 'INFO': icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING': icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR': icon = xbmcgui.NOTIFICATION_ERROR
    xbmcgui.Dialog().notification(heading, message, icon, time, sound=sound)

# Aktiviere xStream Addon
def enableAddon(ADDONID):
    struktur = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","id":1,"params": {"addonid":"%s", "properties": ["enabled"]}}' % ADDONID))
    if 'error' in struktur or struktur["result"]["addon"]["enabled"] != True:
        count = 0
        while True:
            if count == 5: break
            count += 1
            xbmc.executebuiltin('EnableAddon(%s)' % (ADDONID))
            xbmc.executebuiltin('SendClick(11)')
            xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":1,"params":{"addonid":"%s", "enabled":true}}' % ADDONID)
            xbmc.sleep(500)
            try:
                struktur = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","id":1,"params": {"addonid":"%s", "properties": ["enabled"]}}' % ADDONID))
                if struktur["result"]["addon"]["enabled"] == True: break
            except:
                pass

# Überprüfe Abhängigkeiten
def checkDependence(ADDONID):
    isdebug = True
    if isdebug: xbmc.log(__name__ + ' - %s - checkDependence ' % ADDONID, xbmc.LOGDEBUG)
    try:
        addon_xml = os.path.join(ADDON_PATH % ADDONID, 'addon.xml')
        with open(addon_xml, 'rb') as f:
            xml = f.read()
        pattern = '(import.*?addon[^/]+)'
        allDependence = re.findall(pattern, str(xml))
        for i in allDependence:
            try:
                if 'optional' in i or 'xbmc.python' in i: continue
                pattern = 'import.*?"([^"]+)'
                IDdoADDON = re.search(pattern, i).group(1)
                if os.path.exists(ADDON_PATH % IDdoADDON) == True and xbmcaddon.Addon().getSetting('enforceUpdate') != 'true':
                    enableAddon(IDdoADDON)
                else:
                    xbmc.executebuiltin('InstallAddon(%s)' % (IDdoADDON))
                    xbmc.executebuiltin('SendClick(11)')
                    enableAddon(IDdoADDON)
            except:
                pass
    except Exception as e:
        xbmc.log(__name__ + ' %s - Exception ' % e, LOGERROR)


# Starte xStream Update wenn auf Github verfügbar
if os.path.isfile(NIGHTLY_UPDATE) == False or Addon().getSetting('githubUpdateXstream') == 'true'  or Addon().getSetting('enforceUpdate') == 'true':
    from resources.lib import updateManager
    status1 = updateManager.xStreamUpdate(True)
    if Addon().getSetting('update.notification') == 'full': # Benachrichtung xStream vollständig
        infoDialog(cConfig().getLocalizedString(30112), sound=False, icon='INFO', time=10000)   # Suche Updates
        if status1 == True: infoDialog(cConfig().getLocalizedString(30113), sound=False, icon='INFO', time=6000)
        if status1 == False: infoDialog(cConfig().getLocalizedString(30114), sound=True, icon='ERROR')
        if status1 == None: infoDialog(cConfig().getLocalizedString(30115), sound=False, icon='INFO', time=6000)
        if xbmcaddon.Addon().getSetting('enforceUpdate') == 'true': xbmcaddon.Addon().setSetting('enforceUpdate', 'false')
    else:
        if status1 == True: infoDialog(cConfig().getLocalizedString(30113), sound=False, icon='INFO', time=6000)
        if status1 == False: infoDialog(cConfig().getLocalizedString(30114), sound=True, icon='ERROR')
        if xbmcaddon.Addon().getSetting('enforceUpdate') == 'true': xbmcaddon.Addon().setSetting('enforceUpdate', 'false')
# Starte Resolver Update wenn auf Github verfügbar    
if os.path.isfile(NIGHTLY_UPDATE) == False or Addon().getSetting('githubUpdateResolver') == 'true'  or Addon().getSetting('enforceUpdate') == 'true': 
    from resources.lib import updateManager
    status2 = updateManager.resolverUpdate(True)
    if Addon().getSetting('update.notification') == 'full': # Benachrichtung Resolver vollständig
        infoDialog(cConfig().getLocalizedString(30112), sound=False, icon='INFO', time=10000)   # Suche Updates
        if status2 == True: infoDialog('Resolver ' + xbmcaddon.Addon().getSetting('resolver.branch') + cConfig().getLocalizedString(30116), sound=False, icon='INFO', time=6000)
        if status2 == False: infoDialog(cConfig().getLocalizedString(30117), sound=True, icon='ERROR')
        if status2 == None: infoDialog(cConfig().getLocalizedString(30118), sound=False, icon='INFO', time=6000)
        if xbmcaddon.Addon().getSetting('enforceUpdate') == 'true': xbmcaddon.Addon().setSetting('enforceUpdate', 'false')
    else:
        if status2 == True: infoDialog('Resolver ' + xbmcaddon.Addon().getSetting('resolver.branch') + cConfig().getLocalizedString(30116), sound=False, icon='INFO', time=6000)
        if status2 == False: infoDialog(cConfig().getLocalizedString(30117), sound=True, icon='ERROR')
        if xbmcaddon.Addon().getSetting('enforceUpdate') == 'true': xbmcaddon.Addon().setSetting('enforceUpdate', 'false')

# "setting.xml" wenn notwendig Indexseiten aktualisieren
try:
    if xbmcaddon.Addon().getSetting('newSetting') == 'true':
        from resources.lib.handler.pluginHandler import cPluginHandler
        cPluginHandler().getAvailablePlugins()
except Exception:
    pass

# Startet Überprüfung der Abhängigkeiten

checkDependence('plugin.video.xstream')

# Überprüfung des Domain Namens. Leite um und hole neue URL und schreibe in die settings.xml. Bei nicht erreichen der Seite deaktiviere Globale Suche bis zum nächsten Start und überprüfe erneut.
def checkDomain(): #ToDo Domains aus dem jeweiligen Siteplugin lesen oder in der config in eine def deklarieren
    # Domains die bis jetzt keinen Domain Wechsel hatten
    domains = [('aniworld', 'aniworld.to'), ('cinemathek', 'cinemathek.net'), ('filmpalast', 'filmpalast.to'), ('flimmerstube', 'flimmerstube.com'), ('streamworld', 'streamworld.in')]
    # Domains mit wechselbarer Domain
    domains += [('kinoger', cConfig().getSetting('plugin_kinoger.domain')), ('kinox', 'www15.kinoz.to'), ('serienstream', cConfig().getSetting('plugin_serienstream.domain'))]
    # Domains die wenig wechseln
    domains += [('kinofox', 'kinofox.su'), ('kino', 'kino.ws'), ('megakino', 'megakino.co'), ('movie2k', 'movie2k.at'), ('movieking', 'movieking.cc')]
    # Domains die häufig wechseln
    domains += [('hdfilme', 'hdfilme.haus'), ('kkiste', 'kkiste.house'), ('kinokiste', 'kinokiste.cloud'), ('movie4k', 'movie4k.rocks'), ('xcine', 'xcine.click')]

   
    log(LOGMESSAGE + ' -> [checkDomain]: Query status code of the provider', LOGNOTICE)
    for item in domains:
        provider, _domain = item # SITE_IDENTIFIER , Domain
        domain = cConfig().getSetting('plugin_'+ provider +'.domain', _domain)
        base_link = 'http://' + domain + '/'  # URL_MAIN
        if domain == 'site-maps.cc':    # Falsche Umleitung ausschliessen
            continue
        try:
            if xbmcaddon.Addon().getSetting('plugin_' + provider) == 'false':                               # Wenn SitePlugin deaktiviert
                cConfig().setSetting('global_search_' + provider, 'false')                                  # setzte Globale Suche auf aus
                cConfig().setSetting('plugin_' + provider + '_checkdomain', 'false')                        # setzte Domain Check auf aus

            if xbmcaddon.Addon().getSetting('plugin_' + provider + '_checkdomain') == 'true':               # aut. Domainüberprüfung an ist überprüfe Status der Sitplugins
                oRequest = cRequestHandler(base_link, caching=False, ignoreErrors=True)
                oRequest.request()
                status_code = int(oRequest.getStatus())
                log(LOGMESSAGE + ' -> [checkDomain]: Status Code ' + str(status_code) + '  ' + provider + ': - ' + base_link, LOGNOTICE)
                if 403 <= status_code <= 503:                                                               # Domain Interner Server Error und nicht erreichbar
                    cConfig().setSetting('global_search_' + provider, 'false')                              # deaktiviere Globale Suche
                    log(LOGMESSAGE + ' -> [checkDomain]: Internal Server Error (DDOS Guard, HTTP Error, Cloudflare or BlazingFast active)', LOGNOTICE)

                if 300 <= status_code <= 400:                                                               # Domain erreichbar mit Umleitung
                    url = oRequest.getRealUrl()
                    #cConfig().setSetting('plugin_'+ provider +'.base_link', url)
                    cConfig().setSetting('plugin_' + provider + '.domain', urlparse(url).hostname)          # setze Domain in die settings.xml
                    cConfig().setSetting('global_search_' + provider, 'true')                               # aktiviere Globale Suche
                    log(LOGMESSAGE + ' -> [checkDomain]: globalSearch for ' + provider + ' is activated.', LOGNOTICE)

                elif status_code == 200:                                                                    # Domain erreichbar
                    #cConfig().setSetting('plugin_' + provider + '.base_link', base_link)
                    cConfig().setSetting('plugin_' + provider + '.domain', urlparse(base_link).hostname)    # setze URL_MAIN in die settings.xml
                    cConfig().setSetting('global_search_' + provider, 'true')                               # aktiviere Globale Suche
                    log(LOGMESSAGE + ' -> [checkDomain]: globalSearch for ' + provider + ' is activated.', LOGNOTICE)

                else:
                    log(LOGMESSAGE + ' -> [checkDomain]: Error ' + provider + ' not available.', LOGNOTICE)
                    cConfig().setSetting('global_search_' + provider, 'false')                              # deaktiviere Globale Suche
                    log(LOGMESSAGE + ' -> [checkDomain]: globalSearch for ' + provider + ' is deactivated.', LOGNOTICE)
        except:
            cConfig().setSetting('global_search_' + provider, 'false')                                      # deaktiviere Globale Suche
            log(LOGMESSAGE + ' -> [checkDomain]: Error ' + provider + ' not available.', LOGNOTICE)
            pass

# Startet Domain Überprüfung und schreibt diese in die settings.xml
checkDomain()

# Todo löscht derzeit beim Start nach dem checkDomain die pluginDB in dem Userdata Ordner da diese durch die fehlende update settings im Pluginhandler nicht aktualisiert wird.
# pluginhandler.py Line 58
PLUGIN_UPDATE = os.path.join(translatePath(Addon().getAddonInfo('profile')), "pluginDB")
if os.path.exists(PLUGIN_UPDATE):
    os.remove(PLUGIN_UPDATE)
    from resources.lib.handler.pluginHandler import cPluginHandler
    cPluginHandler().getAvailablePlugins()

# zeigt nach Update den Changelog als Popup an
def changelog():
    CHANGELOG_PATH = translatePath(os.path.join('special://home/addons/plugin.video.xstream/', 'changelog.txt'))
    version = xbmcaddon.Addon().getAddonInfo('version')
    if xbmcaddon.Addon().getSetting('changelog_version') == version or not os.path.isfile(CHANGELOG_PATH):
        return
    xbmcaddon.Addon().setSetting('changelog_version', version)
    heading = cConfig().getLocalizedString(30275)
    with open(CHANGELOG_PATH, mode="r", encoding="utf-8") as f:
        cl_lines = f.readlines()
    announce = ''
    for line in cl_lines:
        announce += line
    tools.textBox(heading, announce)

# Changelog Popup in den "settings.xml" ein bzw. aus schaltbar

if xbmcaddon.Addon().getSetting('popup.update.notification') == 'true': 
    changelog()


# Html Cache beim KodiStart nach (X) Tage löschen
deltaDay = int(cConfig().getSetting('cacheDeltaDay', 2))
deltaTime = 60*60*24*deltaDay # Tage 
currentTime = int(time.time())
# alle x Tage
if currentTime >= int(cConfig().getSetting('lastdelhtml', 0)) + deltaTime:
    cRequestHandler('').clearCache() # Cache löschen
    cConfig().setSetting('lastdelhtml', str(currentTime))