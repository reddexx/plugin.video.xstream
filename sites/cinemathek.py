# -*- coding: utf-8 -*-

#   2022.09.25 DWH
# -------------TODO--------------------
# Genre
# Suche
# Episoden
# Hoster


from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser, cUtil
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui


SITE_IDENTIFIER = 'cinemathek'
SITE_NAME = 'Cinemathek'
SITE_ICON = 'cinemathek.png'
URL_MAIN = 'https://cinemathek.net'
URL_FILME = URL_MAIN + '/movies/'
URL_SERIEN = URL_MAIN + '/tvshows/'
URL_SEARCH = URL_MAIN + '/?s=%s'
URL_GENRE = URL_MAIN + '/genre/'

def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_FILME)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_SERIEN)
    cGui().addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN)
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().addFolder(cGuiElement('IMDB', SITE_IDENTIFIER, 'showIMDB'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()
  


def showGenre():    # irgendwas hab ich mal wieder falsch und seh den Wald vor lauter Bäumen nicht
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(sUrl) 
    sHtmlContent = oRequest.request()
    pattern = '">Genre</a>.*?'  # container start
    pattern += 'href="([^"]+).*?>([^<]+).*?' # link
    pattern += '</ul>'  # end 
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)    

    for sUrl, sName in aResult:
        if sUrl.startswith('/'):
            sUrl = URL_GENRE + sUrl
        params.setParam('sUrl', sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')

    oRequest = cRequestHandler(sUrl, ignoreErrors=sGui is not False) 
    sHtmlContent = oRequest.request()
    pattern = '<article[^>]*class="item[^"]*"[^>]*>.*?'  # container start
    pattern += '<img src="([^"]+).*?'  # sThumbnail
    pattern += 'href="([^"]+).*?'  # url  
    pattern += 'class="title"> <h4>([^<]+).*?'  # name 
    pattern += '<div class="texto">([^<]+).*?'  # desc

    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sThumbnail, sUrl, sName, sDesc in aResult:
        if sSearchText and not cParser.search(sSearchText, sName):
            continue  
        isTvshow, aResult = cParser.parse(sHtmlContent, '<article[^>]*class="item tvshows') # Muss nur im Serien Content auffindbar sein
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons' if isTvshow else 'showHosters')
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')    
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setDescription(sDesc)
        params.setParam('sThumbnail', sThumbnail)
        params.setParam('sUrl', sUrl)
        params.setParam('sName', sName)
        oGui.addFolder(oGuiElement, params, isTvshow, total)

    if not sGui and not sSearchText:
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, '<link[^>]*rel="next"[^>]*href="([^"]+)"') # Nächste Seite
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)

        oGui.setView('tvshows' if isTvshow else 'movies')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    isMatch, aResult = cParser.parse(sHtmlContent, 'Season ([\d]+)') # Sucht den Staffel Eintrag und d fügt die Anzahl hinzu
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, 'class="wp-content">(.*?)</p>') # Staffel Beschreibung
    total = len(aResult)
    for sSeason, in aResult:
        oGuiElement = cGuiElement('Staffel ' + sSeason, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season')
        oGuiElement.setSeason(sSeason)
        oGuiElement.setThumbnail(params.getValue('sThumbnail'))
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('Season', sSeason)
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    sSeason = params.getValue('Season')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'Season %s.*?</div></div>' % sSeason
    isMatch, sHtmlContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = 'class="mark-([^"]+)">.*?href="([^"]+)'
        isMatch, aResult = cParser.parse(sHtmlContainer, pattern)
    if not isMatch:
        cGui().showInfo('Keine Episoden gefunden')
        return


    total = len(aResult)
    for sEpisode, sUrl in aResult:
        oGuiElement = cGuiElement('Folge ' + sEpisode, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setSeason(sSeason)
        oGuiElement.setEpisode(sEpisode)
        oGuiElement.setMediaType('episode')
        oGuiElement.setThumbnail(params.getValue('sThumbnail'))
        if isDesc:
            oGuiElement.setDescription(sDesc)
        params.setParam('sUrl', sUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<iframe class="metaframe rptss" src="([^"]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        for sUrl in aResult:
            hoster = {'link': sUrl, 'name': cParser.urlparse(sUrl)}
            hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)
