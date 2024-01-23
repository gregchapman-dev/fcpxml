import typing as t
from xml.etree.ElementTree import Element  # , fromstring, ParseError, ElementTree
from fcpxml import XMLParser

def callMe(refcon: t.Any, el: Element) -> bool:
    return True

xml = XMLParser('/Users/gregc/Documents/Code/fcpxml/Info.fcpxml')
print(f'xml.isValid = {xml.isValid}')
callbacks: dict[str, tuple[t.Callable[[t.Any, Element], bool], t.Any]] = {
    './library/event/asset-clip': (callMe, None)
}
xml.parse(callbacks)
print('done')
