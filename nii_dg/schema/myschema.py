"""myschema.py
A test set of validation rules for MySchema.
"""

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from nii_dg.check_functions import check_entity_values, is_relative_path, is_url
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