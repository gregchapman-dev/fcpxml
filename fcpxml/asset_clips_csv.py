# ------------------------------------------------------------------------------
# Purpose:       fcpxml is a utilities package for Final Cut Pro XML files (.fcpxml files)
#                AssetClipsCSV is a utility that creates a (CSV) spreadsheet containing
#                all the asset-clips (defined by keywording and making notes about various
#                time-ranges of assets in a library).
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

class AssetClipsCSV:
    def __init__(self, xml: str | Path | Element):
        self.parser = XMLParser(xml)

    def writeCSV(self, csvPath: str | Path) -> bool:
        def assetClipCallback(csvObj, assetClipEl: Element) -> bool:
            # just name for now, could make a name->fileName/filePath mapping
            # from './resources/asset/media-rep' elements, so we can put at
            # least part of the file path in the name.
            assetName: str = assetClipEl.get('name', '')
            # maybe later: assetDuration: str = assetClipEl.get('duration', '')

            # assetClipDict contains:
            #   key = str(timeRange)
            #   value = tuple(list(keywords), note)
            assetClipDict: dict[str, tuple[list[str], str]] = {}
            csvObj[assetName] = assetClipDict
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

        # csvObj is a dict with:
        #   key = assetName
        #   value = assetClipDict
        # assetClipDict is a dict with:
        #   key = timeRange
        #   value = keywordsAndNote
        # keywordsAndNote is a tuple of:
        #   keywords: list[str]
        #   note: str
        csvObj: dict[str, dict[str, tuple[list[str], str]]] = {}
        callbacks: dict[str, tuple[t.Callable[[t.Any, Element], bool], t.Any]] = {
            './library/event/asset-clip': (assetClipCallback, csvObj)
        }
        self.parser.parse(callbacks)

        # now take csvObj and write it out as a CSV file
        # name, timeRange, note, keyword1, keyword2, ...
        with open(csvPath, 'wt', encoding='utf-8') as f:
            print('Movie Name,Time Range,Note,Keywords...', file=f)
            for assetName, assetClipDict in csvObj.items():
                for timeRange, keywordsAndNote in assetClipDict.items():
                    print(
                        f'{Utils.escapedCSVEntry(assetName)}'
                        ','
                        f'{Utils.escapedCSVEntry(timeRange)}',
                        end='',
                        file=f
                    )
                    keywords: list[str] = keywordsAndNote[0]
                    note: str = keywordsAndNote[1]
                    if keywords or note:
                        if note:
                            print(f',{Utils.escapedCSVEntry(note)}', end='', file=f)
                        else:
                            print(',', end='', file=f)
                        for keyword in keywords:
                            print(f',{Utils.escapedCSVEntry(keyword)}', end='', file=f)
                    print('', file=f)  # EOL, finally

        return True
