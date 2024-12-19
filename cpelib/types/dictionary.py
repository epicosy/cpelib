
from lxml import etree
from typing import Dict
from pydantic import BaseModel, Field

from cpelib.types.item import CPEItem
from cpelib.types.vendor import Vendor


class CPEDictionary(BaseModel):
    items: Dict[str, CPEItem] = Field(default_factory=dict)
    vendors: Dict[str, Vendor] = Field(default_factory=dict)

    def __len__(self):
        return len(self.items)

    def add_item(self, element: etree._Element, nsmap: dict) -> CPEItem:
        """
            Adds a CPEItem parsed from the given XML element.

            Args:
                element (etree._Element): The XML element to parse.
                nsmap (dict): The namespace map for the XML document
        """
        # TODO: find cpe23-item with short version of namespace
        cpe_item = CPEItem(
            name=element.get('name'),
            title=element.find('title', nsmap).text,
            cpe=element.find('{http://scap.nist.gov/schema/cpe-extension/2.3}cpe23-item').get('name'),
            deprecated=element.get('deprecated') == 'true',
            deprecation_date={'deprecation_date': element.get('deprecation_date')},
            references={'references': element.find('references', nsmap)}
        )
        self.items[cpe_item.name] = cpe_item

        vendor = self.vendors.get(cpe_item.cpe.vendor, None)

        if vendor is None:
            vendor = Vendor(name=cpe_item.cpe.vendor)
            self.vendors[vendor.name] = vendor

        if not vendor.has_product(cpe_item.cpe.product):
            product = cpe_item.cpe.get_product()
            vendor.add_product(product)

        yield cpe_item
