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
import sys
from pathlib import Path
from xml.etree.ElementTree import Element

from fcpxml import XMLParser

class AssetClipsCSV:
    def __init__(self, xml: str | Path | Element):
        self.csv: str = ''
        self.parser = XMLParser(xml)

    def writeCSV(self, csvPath: str | Path) -> bool:
        def assetClipCallback(csvObj, assetClipEl: Element) -> bool:
            def getTimeRange(startTime: str, duration: str) -> str:
                # we can make it much more human readable
                return startTime + '-' + duration

            # just name for now, could make a name->fileName/filePath mapping from './resources/asset/media-rep' elements
            assetName: str = assetClipEl.get('name', '')
            assetDuration: str = assetClipEl.get('duration') # we'll get the timescale from this
            # assetClipDict contains:
            #   key = str(timeRange)
            #   value = tuple(list(keywords), note)
            assetClipDict: dict[str, tuple[list[str], str]] = {}
            csvObj[assetName] = assetClipDict
            # loop over the clips in this
            for kwEl in assetClipEl.findall('keyword'):
                startTime: str = kwEl.get('start', '')
                duration: str = kwEl.get('duration', '')
                timeRange: str = getTimeRange(startTime, duration)
                keywordValue: str = kwEl.get('value', '')  # ', '-delimited list of keywords
                keywordList: list[str] = []
                if keywordValue:
                    keywordList = keywordValue.split(', ')
                note: str = kwEl.get('note', '')
                assetClipDict[timeRange] = (keywordList, note)

            print('hey')

        if not self.parser.isValid:
            return False

        csvObj: dict = {}
        callbacks: dict[str, tuple[t.Callable[[t.Any, Element], bool], t.Any]] = {
            './library/event/asset-clip': (assetClipCallback, csvObj)
        }
        self.parser.parse(callbacks)

        return True


