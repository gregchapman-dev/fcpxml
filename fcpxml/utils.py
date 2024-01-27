# ------------------------------------------------------------------------------
# Purpose:       fcpxml is a utilities package for Final Cut Pro XML files (.fcpxml files)
#                Utils is a set of simple utility functions for use by various fcpxml
#                utilities.
#
# Authors:       Greg Chapman <gregc@mac.com>
#
# Copyright:     (c) 2024 Greg Chapman
# License:       MIT, see LICENSE
# ------------------------------------------------------------------------------
import datetime
import re
from fractions import Fraction

class Utils:
    @staticmethod
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

        # we truncate startTime down, and (whatever it's called) endTime up
        startStr: str = str(datetime.timedelta(seconds=int(startTime)))
        endStr: str = str(datetime.timedelta(seconds=int(endTime + 1.0)))

        return startStr + ' - ' + endStr

    @staticmethod
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

    @staticmethod
    def isYear(string: str) -> bool:
        patt: str = r'^\d{4}(-\d{4})?$'  # 4 digits ('1999') or two years with hyphen ('1999-2001')
        if re.match(patt, string):
            return True
        return False

    MONTHS_SET: set[str] = set([
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ])

    @staticmethod
    def isMonth(string: str) -> bool:
        return string in Utils.MONTHS_SET
