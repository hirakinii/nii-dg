#!/usr/bin/env python3
# coding: utf-8

import pytest  # noqa: F401

from nii_dg.error import EntityError, PropsError
from nii_dg.ro_crate import ROCrate
from nii_dg.schema.amed import DMP, DMPMetadata
from nii_dg.schema.base import (DataDownload, HostingInstitution, Person,
                                RepositoryObject, RootDataEntity)


def test_init() -> None:
    ent = DMPMetadata({})
    assert ent["@id"] == "#AMED-DMP"
    assert ent["@type"] == "DMPMetadata"
    assert ent.schema_name == "amed"
    assert ent.entity_name == "DMPMetadata"


def test_as_jsonld() -> None:
    ent = DMPMetadata({})
    org = HostingInstitution("https://ror.org/04ksd4g47")

    ent["about"] = RootDataEntity({})
    ent["funder"] = org
    ent["funding"] = "Acceleration Transformative Research for Medical Innovation"
    ent["chiefResearcher"] = Person("https://orcid.org/0000-0001-2345-6789")
    ent["creator"] = [Person("https://orcid.org/0000-0001-2345-6789")]
    ent["hostingInstitution"] = org
    ent["dataManager"] = Person("https://orcid.org/0000-0001-2345-6789")
    ent["repository"] = RepositoryObject("https://doi.org/xxxxxxxx")
    ent["distribution"] = DataDownload("https://zenodo.org/record/example")
    ent["hasPart"] = [DMP(1), DMP(2)]

    jsonld = {'@type': 'DMPMetadata', '@id': '#AMED-DMP', 'about': {'@id': './'}, 'name': 'AMED-DMP', 'funding': 'Acceleration Transformative Research for Medical Innovation', 'chiefResearcher': {'@id': 'https://orcid.org/0000-0001-2345-6789'}, 'creator': [{'@id': 'https://orcid.org/0000-0001-2345-6789'}], 'hostingInstitution': {
        '@id': 'https://ror.org/04ksd4g47'}, 'dataManager': {'@id': 'https://orcid.org/0000-0001-2345-6789'}, 'repository': {'@id': 'https://doi.org/xxxxxxxx'}, 'distribution': {'@id': 'https://zenodo.org/record/example'}, 'hasPart': [{'@id': '#dmp:1'}, {'@id': '#dmp:2'}], "funder": {'@id': 'https://ror.org/04ksd4g47'}}

    ent_in_json = ent.as_jsonld()
    del ent_in_json["@context"]

    assert ent_in_json == jsonld


def test_check_props() -> None:
    ent = DMPMetadata(props={"unknown_property": "unknown"})

    # error: with unexpected property
    with pytest.raises(EntityError):
        ent.check_props()

    # error: lack of required properties
    del ent["unknown_property"]
    with pytest.raises(EntityError):
        ent.check_props()

    # error: type error
    org = HostingInstitution("https://ror.org/04ksd4g47")

    ent["about"] = RootDataEntity()
    ent["funder"] = org
    ent["funding"] = "Acceleration Transformative Research for Medical Innovation"
    ent["chiefResearcher"] = "Donald Duck"
    ent["creator"] = [Person("https://orcid.org/0000-0001-2345-6789")]
    ent["hostingInstitution"] = org
    ent["dataManager"] = Person("https://orcid.org/0000-0001-2345-6789")
    ent["hasPart"] = [DMP(1), DMP(2)]
    with pytest.raises(EntityError):
        ent.check_props()

    # no error occurs with correct property value
    ent["chiefResearcher"] = Person("https://orcid.org/0000-0001-2345-6789")
    ent.check_props()


def test_validate() -> None:
    crate = ROCrate()
    org = HostingInstitution("https://ror.org/04ksd4g47")
    root = RootDataEntity()
    ent = DMPMetadata(props={"funder": org, "hasPart": [], "about": root})
    crate.add(org, ent)

    # error: funder not included in the funder list of RootDataEntity
    # error: value of about is not the RootDataEntity of the crate
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["about"] = crate.root
    crate.root["funder"] = [org]
    # no error
    ent.validate(crate)

    dmp = DMP("sample")
    crate.add(dmp)
    # error: not all DMP entity in the crate is included in hasPart
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["hasPart"] = [dmp]
    # error: creator, hostingInstitution, dataManager are required
    with pytest.raises(EntityError):
        ent.validate(crate)

    ent["hostingInstitution"] = org
    person = Person("https://example.com/person")
    ent["creator"] = [person]
    ent["dataManager"] = person
    # no error
    ent.validate(crate)
