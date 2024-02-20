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
    class TextWrapper:
        def __init__(
            self,
            filewt,
            wrapAt: int = 80,
            wrapIndent: int = 4,
            tab: int = 4,
            dryRun: bool = False
        ):
            # filewt is a text file, open for writing:
            #   with open(reportPath, 'wt', encoding='utf-8') as filewt:
            #       wrapper = TextWrapper(filewt, wrapAt=100, wrapIndent=25)
            self.filewt = filewt
            self.wrapAt = wrapAt
            self.wrapIndent = wrapIndent
            self.tab = tab
            self.dryRun = dryRun
            self._currLinePos = 0

        def write(self, text: str):
            # how much can we fit (break at whitespace, but don't trim any whitespace except
            # the one that caused the break)
            lines: list[str] = self._split(text)

            numLines: int = len(lines)
            if numLines == 0:
                return

            for i, line in enumerate(lines):
                if not self.dryRun:
                    if i == numLines - 1:
                        print(line, end='', file=self.filewt)
                        continue
                    print(line, file=self.filewt)

            if lines[-1][-1] == '\n':
                self._currLinePos = 0
            else:
                lastLineLength: int = len(lines[-1])
                self._currLinePos += lastLineLength

        def writeLine(self, text: str):
            if text:
                self.write(text)

            if not self.dryRun:
                print(file=self.filewt)
                self._currLinePos = 0

        def _split(self, text: str) -> list[str]:
            import textwrap
            initialIndent: str = ' ' * self._currLinePos
            output: list[str] = textwrap.wrap(
                text,
                width=self.wrapAt,
                initial_indent=initialIndent,
                subsequent_indent=' ' * self.wrapIndent,
                tabsize=self.tab,
                break_long_words=False,
            )

            # We tricked textwrap.wrap with initial_indent.  We need to strip that off,
            # since that text is already in the file.
            if output:
                output[0] = output[0][self._currLinePos:]
            else:
                # must have been all white-space; we want to keep that
                output.append(text)

            return output


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

    MONTHS_ABBREV: dict[str, str] = {
        'January': 'Jan',
        'February': 'Feb',
        'March': 'Mar',
        'April': 'Apr',
        'May': 'May',
        'June': 'Jun',
        'July': 'Jul',
        'August': 'Aug',
        'September': 'Sep',
        'October': 'Oct',
        'November': 'Nov',
        'December': 'Dec',
    }

    @staticmethod
    def isMonth(string: str) -> bool:
        return string in Utils.MONTHS_SET

    @staticmethod
    def abbreviate(text: str) -> str:
        if text in Utils.MONTHS_SET:  # in set is faster than in dict
            return Utils.MONTHS_ABBREV[text]
        return text

