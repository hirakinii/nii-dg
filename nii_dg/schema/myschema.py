"""myschema.py
A test set of validation rules for MySchema.
"""

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from nii_dg.check_functions import (
    check_entity_values, is_absolute_path,
    is_content_size, 
    is_encoding_format, is_iso8601, is_relative_path,
    is_sha256, is_url
)
from nii_dg.entity import DataEntity, EntityDef
from nii_dg.error import EntityError
from nii_dg.utils import load_schema_file

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve(
).parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)

PROHIBITED_WORDS: List[str] = ["danger", "ban", "foo", "bar", "hoge"]


PERMITTED_OUTPUT_FILE_FMTS: List[str] = ["npy", "h5", "npz", "csv", "txt"]


def is_permitted_format(value: str) -> bool:
    """chech whether the given value has one of the permitted file formats.
    """
    try:
        ext = os.path.splitext(value)[-1]
        return ext in PERMITTED_OUTPUT_FILE_FMTS
    except Exception as _:
        return False


def is_message(value: str) -> bool:
    """check whether the given value has the message format.

    Parameters
    ----------
    value : str
        message.
    
    Returns
    -------
    bool
        True if the value has the message format.
    """
    return re.match(r'^[A-Z][a-zA-Z0-9\.\{\}\^\-\ \#\"\'\!\\\|\%\&\(\)\[\]\*\:\+\;]*?\.$', value) is not None


def contain_prohibited_words(value: str) -> bool:
    """test function to check whether the given message contains prohibited words.

    Parameters
    ----------
    value : str
        message.
    
    Returns
    -------
    bool
        False if the value has any prohibited word.
    """
    for s in PROHIBITED_WORDS:
        if s in value:
            return True
    return False


class MySchema(DataEntity):
    """MySchema
    """

    def __init__(
        self,
        id_: str,
        props: Dict[str, Any] = {},
        schema_name: str = SCHEMA_NAME,
        entity_def: EntityDef = SCHEMA_DEF["MySchema"],
    ):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(
            self,
            {
                "url": is_url,
                "message": is_message,
            },
        )
        if not self.id.endswith("/"):
            error.add("@id", "The id MUST end with `/`.")
        if not is_relative_path(self.id):
            error.add("@id", "The id MUST be a relative path.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        message = self.get("message")
        if message is not None:
            if contain_prohibited_words(message):
                error.add("message", "message has some prohibited words.")

        if error.has_error():
            raise error


class MyOutputSchema(DataEntity):
    def __init__(
        self,
        id_: str,
        props: Dict[str, Any] = {},
        schema_name: str = SCHEMA_NAME,
        entity_def: EntityDef = SCHEMA_DEF["File"],
    ):
        super().__init__(id_, props, schema_name, entity_def)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(
            self,
            {
                "contentSize": is_content_size,
                "encodingFormat": is_encoding_format,
                "sha256": is_sha256,
                "url": is_url,
                "sdDatePublished": is_iso8601,
            },
        )
        if is_absolute_path(self.id):
            error.add("@id", "The id MUST be a URL or a relative path.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if is_url(self.id):
            if "sdDataPublished" not in self:
                error.add(
                    "sdDataPublished",
                    "The property `sdDataPublished` is required when the id is a URL.",
                )

        if not is_permitted_format(self.id):
            if not is_url(self.id):
                error.add(
                    "@id",
                    "The property `@id` does not has any permitted file format."
                )

        if error.has_error():
            raise error
