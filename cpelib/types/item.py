
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator

from cpelib.types.reference import Reference
from cpelib.types.cpe import CPE
from cpelib.utils.common import XSD_DATETIME_FORMAT
from cpeparser import CpeParser

cpe_parser = CpeParser()


class CPEItem(BaseModel):
    name: str
    title: str
    cpe: CPE
    deprecated: Optional[bool] = False
    deprecation_date: Optional[datetime] = None
    references: Optional[List[Reference]] = None  # List of Reference objects
    # TODO: add the check and deprecation_by attributes (just in case, not in the XML files so far)

    @field_validator("cpe", mode="before")
    def parse_cpe(cls, values):
        """
        Parses the <cpe23-item> node into a CPE string.
        """

        if values is not None:
            cpe_dict = cpe_parser.parser(values)
            return CPE(**cpe_dict)

        return None

    @field_validator("references", mode="before")
    def parse_references(cls, values):
        """
        Parses the <references> node into a References object.
        """
        refs = []

        if values is not None:
            references = values.get("references", None)

            if references is not None:
                for ref in references:
                    reference = Reference(href=ref.get("href"), text=ref.text)
                    #if len(reference.tags) == 0:
                    #    raise ValueError(f"No tags for: {reference.text}")
                    refs.append(reference)

        return refs

    @field_validator("deprecation_date", mode="before")
    def parse_deprecation_date(cls, values):
        """
        Parses the deprecation date string into a datetime object.
        """
        if values:
            deprecation_date = values.get("deprecation_date", None)

            if deprecation_date is not None:
                return datetime.strptime(deprecation_date, XSD_DATETIME_FORMAT)

        return None