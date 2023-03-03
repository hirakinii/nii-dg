#!/usr/bin/env python3
# coding: utf-8

import pytest

from nii_dg.error import EntityError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.base import (DataDownload, HostingInstitution, License,
                                RepositoryObject)
from nii_dg.schema.cao import DMP, DMPMetadata, File, Person


def test_init() -> None:
    ent = DMP("#dmp:1")
    assert ent["@id"] == "#dmp:1"
    assert ent["@type"] == "DMP"
    assert ent.schema_name == "cao"
    assert ent.entity_name == "DMP"


def test_as_jsonld() -> None:
    ent = DMP("#dmp:1")
    person = Person("https://orcid.org/0000-0001-2345-6789")

    ent["dataNumber"] = 1
    ent["name"] = "calculated data"
    ent["description"] = "Result data calculated by Newton's method"
    ent["creator"] = [person]
    ent["keyword"] = "Informatics"
    ent["accessRights"] = "open access"
    ent["availabilityStarts"] = "2023-04-01"
    ent["isAccessibleForFree"] = True
    ent["license"] = License("https://www.apache.org/licenses/LICENSE-2.0")
    ent["usageInfo"] = "Contact data manager before usage of this data set."
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["contentSize"] = "100GB"
    ent["hostingInstitution"] = HostingInstitution("https://ror.org/04ksd4g47")
    ent["dataManager"] = person

    jsonld = {'@type': 'DMP', '@id': '#dmp:1', 'name': 'calculated data', 'description': "Result data calculated by Newton's method", 'dataNumber': 1, 'keyword': 'Informatics', 'accessRights': 'open access', 'availabilityStarts': '2023-04-01', 'isAccessibleForFree': True, 'license': {'@id': 'https://www.apache.org/licenses/LICENSE-2.0'},
              'usageInfo': 'Contact data manager before usage of this data set.', 'repository': {'@id': 'https://doi.org/xxxxxxxx'}, 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'contentSize': '100GB', 'hostingInstitution': {'@id': 'https://ror.org/04ksd4g47'}, 'dataManager': {'@id': 'https://orcid.org/0000-0001-2345-6789'}, 'creator': [{'@id': 'https://orcid.org/0000-0001-2345-6789'}]}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = DMP("#dmp:1", {"unknown_property": "unknown"})

    # error: with unexpected property
    # error: lack of required properties
    # error: availabilityStarts value is not future date
    # error: type error
    person = Person("https://orcid.org/0000-0001-2345-6789")

    ent["name"] = "calculated data"
    ent["description"] = "Result data calculated by Newton's method"
    ent["creator"] = [person]
    ent["keyword"] = 1
    ent["accessRights"] = "open access"
    ent["availabilityStarts"] = "2022-12-01"
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["hostingInstitution"] = HostingInstitution("https://ror.org/04ksd4g47")
    ent["dataManager"] = person
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs
    del ent["unknown_property"]
    ent["dataNumber"] = 1
    ent["keyword"] = "Informatics"
    ent["availabilityStarts"] = "9999-04-01"
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    ent = DMP("#dmp:1", {"accessRights": "embargoed access"})
    crate.add(ent)

    # error: no DMPMetadata entity
    # error: availabilityStarts is required
    with pytest.raises(EntityError):
        ent.validate(crate)

    meta = DMPMetadata()
    crate.add(meta)
    ent["availabilityStarts"] = "2000-01-01"
    # error: availabilityStarts MUST be the date of future
    # error: repository is required
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["repository"] = {"@id": "https://example.com/repo"}
    ent["availabilityStarts"] = "2030-01-01"
    crate.add(RepositoryObject("https://example.com/repo"))
    # no error
    ent.validate(crate)

    ent["accessRights"] = "open access"
    # error: availabilityStarts is not required
    # error: distribution is required
    # error: license is required
    # error: isAccessibleForFree is required
    with pytest.raises(EntityError):
        ent.validate(crate)

    del ent["availabilityStarts"]
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["license"] = License("https://example.com/license")
    ent["isAccessibleForFree"] = False
    ent["contentSize"] = "10GB"
    file = File("test", {"contentSize": "11GB", "dmpDataNumber": ent})
    crate.add(file, DataDownload("https://zenodo.org/record/example"), License("https://example.com/license"))
    # error: file size is over.
    # error: isAccessibleForFree MUST be True
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["contentSize"] = "100GB"
    ent["isAccessibleForFree"] = True
    # no error
    ent.validate(crate)
