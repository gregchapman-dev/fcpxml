# ------------------------------------------------------------------------------
# Purpose:       fcpxml is a utilities package for Final Cut Pro XML files (.fcpxml files)
#                XMLParser is the XML parser engine (built on xml.etree.ElementTree)
#
# Authors:       Greg Chapman <gregc@mac.com>
#
# Copyright:     (c) 2024 Greg Chapman
# License:       MIT, see LICENSE
# ------------------------------------------------------------------------------

import sys
import typing as t
from pathlib import Path
from xml.etree.ElementTree import Element, fromstring, ParseError, ElementTree

class XMLParser:
    def __init__(self, xml: str | Path | Element):
        self.element: Element | None = None

        if isinstance(xml, Element):
            self.element = xml
            return

        xmlStr: str | None = None
        if isinstance(xml, str):
            # could be a file path, or could be the xml data itself
            try:
                xml = Path(xml)
            except Exception:  # pylint: disable=broad-exception-caught
                xmlStr = xml

        if isinstance(xml, Path):
            # xml is a Path (originally, or we turned it into one).
            # Read it into xmlStr.
            try:
                with open(xml, 'rt', encoding='utf-8') as f:
                    xmlStr = f.read()
            except UnicodeDecodeError:
                try:
                    with open(xml, 'rt', encoding='utf-16') as f:
                        xmlStr = f.read()
                except UnicodeError:
                    with open(xml, 'rt', encoding='latin-1') as f:
                        xmlStr = f.read()

            if xmlStr is None:
                print(f'ERROR: failed to read from XML file: {xml}.', file=sys.stderr)
                return

        if xmlStr is not None:
            try:
                element: Element | ElementTree = fromstring(xmlStr)
                if isinstance(element, ElementTree):
                    element = element.getroot()
                self.element = element

                # do some validation (version, etc)
                return

            except ParseError as parseErr:
                print(f'ERROR: Parsing the XML failed with "{parseErr}".', file=sys.stderr)
                return

        print(f'ERROR: XMLParser received incorrect arg type: {type(xml)}', file=sys.stderr)

    @property
    def isValid(self) -> bool:
        return self.element is not None

    # parse with callbacks:
    # Each callbacks dict item is:
    # key = any string findall can take (element name, XPath, etc),
    # value = tuple(callable, refcon)
    # The callable will receive two arguments (refcon, element) and is required to return
    # True (please continue parsing) or False (you can stop, I have everything
    # I need).
    def parse(self, callbacks: dict[str, tuple[t.Callable[[t.Any], bool], t.Any]]) -> bool:
        # returns True if successful, False if failure occurred (early termination due
        # to callable returning False is NOT a failure; True will be returned here.)
        if not self.isValid:
            print('ERROR: No XML to parse, XMLParser initialization failed', file=sys.stderr)
            return False

        # scan the XML creating a set of all the elements that will require a callback
        elementsToCallback: dict[Element, tuple[t.Callable[[t.Any], bool], t.Any]] = {}
        for key, value in callbacks.items():
            elements: list[Element] = self.element.findall(key)
            for el in elements:
                elementsToCallback[el] = value

        # walk through every element in document order, calling back if appropriate
        callback: t.Callable[[t.Any], bool]
        refcon: t.Any
        for el in self.element.iter('*'):
            if el in elementsToCallback:
                callback, refcon = elementsToCallback[el]
                callback(refcon, el)
