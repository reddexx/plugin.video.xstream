# -*- coding: utf-8 -*-
# Python 3

# Fertig muss aber noch debuggt werden !    DWH 2022.10.13

import xbmcaddon
from resources.lib import common


class cConfig:
    def __init__(self):
        self.__addon = xbmcaddon.Addon(common.addonID)
        self.__aLanguage = self.__addon.getLocalizedString

    def showSettingsWindow(self):
        self.__addon.openSettings()

    def getSetting(self, sName, default=''):
        result = self.__addon.getSetting(sName)
        if result:
            return result
        else:
            return default

    def setSetting(self, id, value):
        if id and value:
            self.__addon.setSetting(id, value)

    def getLocalizedString(self, sCode):
        return self.__aLanguage(sCode)
