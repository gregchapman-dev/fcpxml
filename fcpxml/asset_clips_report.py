# ------------------------------------------------------------------------------
# Purpose:       fcpxml is a utilities package for Final Cut Pro XML files (.fcpxml files)
#                AssetClipsReport is a utility that creates a text report containing
#                all the asset-clips, their time-ranges and their notes.
#
# Authors:       Greg Chapman <gregc@mac.com>
#
# Copyright:     (c) 2024 Greg Chapman
# License:       MIT, see LICENSE
# ------------------------------------------------------------------------------
import typing as t
from pathlib import Path
from xml.etree.ElementTree import Element

from fcpxml import XMLParser
from fcpxml import Utils

class AssetClipsReport:
    def __init__(self, xml: str | Path | Element):
        self.parser = XMLParser(xml)

    def writeReport(self, reportPath: str | Path) -> bool:
        def assetClipCallback(assetObj, assetClipEl: Element) -> bool:
            # just name for now, could make a name->fileName/filePath mapping
            # from './resources/asset/media-rep' elements, so we can put at
            # least part of the file path in the name.
            assetName: str = assetClipEl.get('name', '')
            # maybe later: assetDuration: str = assetClipEl.get('duration', '')

            # assetClipDict contains:
            #   key = str(timeRange)
            #   value = tuple(list(keywords), note)
            assetClipDict: dict[str, tuple[list[str], str]] = {}
            assetObj[assetName] = assetClipDict
            # loop over the clips in this
            for kwEl in assetClipEl.findall('keyword'):
                startTime: str = kwEl.get('start', '')
                duration: str = kwEl.get('duration', '')
                timeRange: str = Utils.getTimeRange(startTime, duration)
                keywordValue: str = kwEl.get('value', '')  # ', '-delimited list of keywords
                keywordList: list[str] = []
                if keywordValue:
                    keywordList = keywordValue.split(', ')
                note: str = kwEl.get('note', '')
                assetClipDict[timeRange] = (keywordList, note)

            return True  # please keep feeding me Elements

        if not self.parser.isValid:
            return False

        # assetsObj is a dict with:
        #   key = assetName
        #   value = assetClipDict
        # assetClipDict is a dict with:
        #   key = timeRange
        #   value = keywordsAndNote
        # keywordsAndNote is a tuple of:
        #   keywords: list[str]
        #   note: str
        assetsObj: dict[str, dict[str, tuple[list[str], str]]] = {}
        callbacks: dict[str, tuple[t.Callable[[t.Any, Element], bool], t.Any]] = {
            './library/event/asset-clip': (assetClipCallback, assetsObj)
        }
        self.parser.parse(callbacks)

        # now take assetsObj and write it out as a text file
        # clip1-name
        #   timeRange1: year, month note1
        #   timeRange2, note2
        #   ...
        # clip2-name
        #   timeRange1, note1
        #   timeRange2, note2
        #   ...
        # ...
        with open(reportPath, 'wt', encoding='utf-8') as f:
            for assetName, assetClipDict in assetsObj.items():
                print(f'{assetName}:', file=f)
                for timeRange, keywordsAndNote in assetClipDict.items():
                    keywords: list[str] = keywordsAndNote[0]
                    note: str = keywordsAndNote[1]

                    # timeRange first
                    print(f'\t{timeRange}: ', end='', file=f)

                    # year and month next (if present in keywords)
                    year: str = ''
                    month: str = ''
                    for keyword in keywords:
                        if year and month:
                            # stop looking if you found both
                            break

                        if not year and Utils.isYear(keyword):
                            year = keyword
                            continue

                        if not month and Utils.isMonth(keyword):
                            month = keyword
                            continue

                    if month:
                        print(month, end='', file=f)
                    if month and year:
                        print(' ', end='', file=f)
                    if year:
                        print(year, end='', file=f)
                    if year or month:
                        print(': ', end='', file=f)

                    # note next
                    print(f'{note}', file=f)  # EOL, finally

        return True
