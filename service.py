# -*- coding: utf-8 -*-
# Python 3
# Fertig muss aber noch debuggt werden !    DWH 2022.10.12

import sys
import os
import json
import re
import xbmc
import xbmcaddon
import xbmcgui
from xbmc import LOGDEBUG, LOGERROR
from resources.lib.config import cConfig

AddonName = xbmcaddon.Addon().getAddonInfo('name')
# xStream = xbmcaddon.Addon().getAddonInfo('id')

from xbmcvfs import translatePath
# Pfad der update.sha
NIGHTLY_UPDATE = os.path.join(translatePath(xbmcaddon.Addon().getAddonInfo('profile')), "update_sha")
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
        #if isdebug: log_utils.log(__name__ + '%s - allDependence ' % str(allDependence), log_utils.LOGDEBUG)
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
        xbmc.log(__name__ + '  %s - Exception ' % e, LOGERROR)


if os.path.isfile(NIGHTLY_UPDATE) == False or xbmcaddon.Addon().getSetting('githubUpdateXstream') == 'true' or xbmcaddon.Addon().getSetting('githubUpdateResolver') == 'true' or xbmcaddon.Addon().getSetting('enforceUpdate') == 'true':
    
# Status Dialog der Auto Updates    
    from resources.lib import updateManager
    status1 = updateManager.xStreamUpdate(True)
    status2 = updateManager.resolverUpdate(True)
    infoDialog(cConfig().getLocalizedString(30112), sound=False, icon='INFO', time=10000)
    if status1 == True: infoDialog(cConfig().getLocalizedString(30113), sound=False, icon='INFO', time=6000)
    if status1 == False: infoDialog(cConfig().getLocalizedString(30114), sound=True, icon='ERROR')
    if status1 == None: infoDialog(cConfig().getLocalizedString(30115), sound=False, icon='INFO', time=6000)
    if status2 == True: infoDialog('Resolver ' + xbmcaddon.Addon().getSetting('resolver.branch') + cConfig().getLocalizedString(30116), sound=False, icon='INFO', time=6000)
    if status2 == False: infoDialog(cConfig().getLocalizedString(30117), sound=True, icon='ERROR')
    if status2 == None: infoDialog(cConfig().getLocalizedString(30118), sound=False, icon='INFO', time=6000)
    if xbmcaddon.Addon().getSetting('enforceUpdate') == 'true': xbmcaddon.Addon().setSetting('enforceUpdate', 'false')

# "setting.xml" wenn notwendig Indexseiten aktualisieren
try:
    if xbmcaddon.Addon().getSetting('newSetting') == 'true':
        from resources.lib.handler.pluginHandler import cPluginHandler
        cPluginHandler().getAvailablePlugins()
except Exception:
    pass

checkDependence('plugin.video.xstream')
