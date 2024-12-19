from lxml import etree

from cpelib.types.dictionary import CPEDictionary
from cpelib.types.generator import GeneratorInfo

from pathlib import Path
from tqdm import tqdm


class CPEDictionaryLoader:
    def __init__(self, xml_file: str = '~/.cpelib/official-cpe-dictionary_v2.3.xml'):
        """
        Loader for CPE dictionary XML files. Parses the cpe-item elements in chunks.

        Args:
            xml_file (str): Path to the XML file.
        """

        # check if the file exists
        xml_file = Path(xml_file).expanduser()

        if not xml_file.exists():
            raise FileNotFoundError(f"File not found: {xml_file}")

        self.xml_file = xml_file
        self.generator_info = None
        self.dictionary = CPEDictionary()  # Holds items

        self.context = etree.iterparse(self.xml_file, events=('start', 'end'))
        _, self.root = next(self.context)
        _, generator_element = next(self.context)

        # Read the first element after root - the <generator> node
        if generator_element is not None and generator_element.tag.endswith('generator'):
            self.generator_info = GeneratorInfo.from_xml(generator_element, self.root.nsmap)
            generator_element.clear()  # Clear generator from memory
        else:
            raise ValueError("Expected <generator> element as the first child of root.")

        print(self.generator_info)

    @property
    def nsmap(self) -> dict:
        """Returns the namespace map of the XML document."""
        return self.root.nsmap

    def __call__(self, *args, **kwargs):
        # TODO: this probably should have an option to either return the items or the dictionary

        """
        Parses the XML file incrementally and yields chunks of CPE items.

        Yields:
            List[CPEItem]: Chunks of CPE items.
        """

        with tqdm(desc="Processing CPE items", unit="item") as pbar:
            # Process <cpe-item> elements
            for event, element in self.context:
                if event == 'end' and element.tag.endswith('cpe-item'):
                    yield from self.dictionary.add_item(element, self.nsmap)
                    element.clear()  # Clear the current cpe-item node from memory

                    # Free up memory for processed elements
                    while element.getprevious() is not None:
                        del element.getparent()[0]

                    pbar.update(1)
