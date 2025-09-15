from __future__ import annotations

from typing import Any, ClassVar
from urllib.parse import urlparse

from attr import define

from ... import Config
from ...utils import PythonIdentifier
from .protocol import PropertyProtocol, Value
from .schemas import Class


@define
class RemoteModelProperty(PropertyProtocol):
    name: str
    required: bool
    default: Value | None
    python_name: PythonIdentifier
    description: str | None
    example: str | None
    class_info: Class
    module_path: str
    _json_type_string: ClassVar[str] = "Dict[str, Any]"

    @classmethod
    def build(
        cls,
        name: str,
        required: bool,
        python_name: PythonIdentifier,
        config: Config,
    ) -> RemoteModelProperty:
        class_info = Class.from_string(string=name, config=config)
        module_path = _get_module_path(name)
        return cls(
            name=name,
            required=required,
            default=None,
            python_name=python_name,
            description=None,
            example=None,
            class_info=class_info,
            module_path=module_path,
        )

    @classmethod
    def convert_value(cls, value: Any) -> Value | None:
        if value is None or isinstance(value, Value):
            return value
        return Value(str(value))

    @property
    def self_import(self) -> str:
        """Constructs a self import statement from this ModelProperty's attributes"""
        return f".{self.module_path}.models.{self.class_info.module_name} import {self.class_info.name}"
    
    def get_lazy_imports(self, *, prefix: str) -> set[str]:
        return {f"from {prefix}{self.self_import}"}

    def get_base_type_string(self, *, quoted: bool = False) -> str:
        return f'"{self.class_info.name}"' if quoted else self.class_info.name


def _get_module_path(path: str) -> str:
    """
    Tranform
    ./creditRegistry.ds.json#/components/schemas/SingleFormat -> 
    ./creditRegistry.ds.json -> 
    creditRegistry.ds.json -> 
    creditRegistry
    """

    ref = urlparse(path)
    return ref.path.split("/")[-1].split(".")[0]
