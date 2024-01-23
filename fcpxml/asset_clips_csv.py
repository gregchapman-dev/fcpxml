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
import datetime
import typing as t
from pathlib import Path
from fractions import Fraction
from xml.etree.ElementTree import Element

from fcpxml import XMLParser

class AssetClipsCSV:
    def __init__(self, xml: str | Path | Element):
        self.parser = XMLParser(xml)

    def writeCSV(self, csvPath: str | Path) -> bool:
        def assetClipCallback(csvObj, assetClipEl: Element) -> bool:
            def getTimeRange(timeStamp: str, duration: str) -> str:
                # timeStamp and duration both must be of the form:
                # Ns (for an integer number of seconds) or N/Ms (for a fractional number of seconds)
                if timeStamp[-1] != 's' and duration[-1] != 's':
                    return timeStamp + '-' + duration
                timeStamp = timeStamp[:-1]
                duration = duration[:-1]

                tsNumStr: str = ''
                tsDenStr: str = '1'
                durNumStr: str = ''
                durDenStr: str = '1'

                if '/' in timeStamp:
                    tsNumStr, tsDenStr = timeStamp.split('/', 1)
                else:
                    tsNumStr = timeStamp

                if '/' in duration:
                    durNumStr, durDenStr = duration.split('/', 1)
                else:
                    durNumStr = duration

                startTime: Fraction = Fraction(int(tsNumStr), int(tsDenStr))
                dur: Fraction = Fraction(int(durNumStr), int(durDenStr))
                endTime: Fraction = startTime + dur

                startStr: str = str(datetime.timedelta(seconds=round(startTime)))
                endStr: str = str(datetime.timedelta(seconds=round(endTime)))

                return startStr + ' - ' + endStr

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
                timeRange: str = getTimeRange(startTime, duration)
                keywordValue: str = kwEl.get('value', '')  # ', '-delimited list of keywords
                keywordList: list[str] = []
                if keywordValue:
                    keywordList = keywordValue.split(', ')
                note: str = kwEl.get('note', '')
                assetClipDict[timeRange] = (keywordList, note)

            return True  # please keep feeding me Elements

        def escapedCSVEntry(entry: str) -> str:
            output: str = entry
            if ',' in entry:
                # first escape any double-quotes (so we can use double quotes around entry)
                output = ''
                for ch in entry:
                    if ch == '"':
                        output += ch + ch
                    else:
                        output += ch

                # next, put double-quotes around entry to escape any commas.
                output = '"' + output + '"'
            return output


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
                        f'{escapedCSVEntry(assetName)},{escapedCSVEntry(timeRange)}',
                        end='',
                        file=f
                    )
                    keywords: list[str] = keywordsAndNote[0]
                    note: str = keywordsAndNote[1]
                    if keywords or note:
                        if note:
                            print(f',{escapedCSVEntry(note)}', end='', file=f)
                        else:
                            print(',', end='', file=f)
                        for keyword in keywords:
                            print(f',{escapedCSVEntry(keyword)}', end='', file=f)
                    print('', file=f)  # EOL, finally

        return True
