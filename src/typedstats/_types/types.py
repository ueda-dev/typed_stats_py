from __future__ import annotations
from typing import Any, Dict, List, Generic, TypeVar, TypedDict, Callable, Tuple, Type
from pandas import DataFrame
from .._types.exceptions import ProtocolViolationException
from .._decorators import allowed_overrun
import pandas as pd

_S = TypeVar('_S', bound='type')
_T = TypeVar('_T', bound='type')

class Field(Generic[_T]):
    def __init__(self, data: List[Any], dtype:_T) -> None:
        self.data = data
        self.type = dtype

    def __len__(self):
        return len(self.data)

class PrimeThis:
    """
    フィールドを参照するためのクラス
    ReadOnly
    """
    def __init__(self) -> None:
        self._fields:Dict[str, Field] = {}

    def __getitem__(self, name: str) -> Any:
        return self._fields[name].data
    
    def __getattr__(self, name: str) -> Any:
        return self._fields[name].data
    
    def to_df(self):
        values = {
            key: [
                x() if callable(x) else x for x in value.data
                ] for key, value in self._fields.items()
            }
        
        return pd.DataFrame(values)
    
class This(Generic[_T]):
    def __init__(self, primethis:PrimeThis, index:int, asType: _T = Any) -> None:
        self._primethis = primethis
        self._index = index
        self._asType = asType

    def asTypeof(self, dtype: _S) -> This[_S]:
        return This(self._primethis, self._index, dtype)

    @allowed_overrun
    def __getitem__(self, name: str) -> _T:
        item = self._primethis._fields[name].data[self._index]
        value = None
        if callable(item):
            value = item()
        else:
            value = item

        if callable(self._asType):
            try:
                return self._asType(value)
            except:
                return value
            
        else:
            return value
    
    @allowed_overrun
    def __getattr__(self, name: str) -> _T:
        value = self._primethis._fields[name].data[self._index]
        if callable(value):
            return value()
        else:
            return value

class PrimeOrigin(DataFrame):
    @classmethod
    def from_df(cls, df: DataFrame) -> 'PrimeOrigin':
        return cls(df)

    def __setitem__(self, key, value) -> None:
        raise ProtocolViolationException("Origin object is read-only")
    
    def __setattr__(self, name: str, value) -> None:
        raise ProtocolViolationException("Origin object is read-only")

class Origin(Generic[_T]):
    def __init__(self, primeorigin: PrimeOrigin, index: int, asType: _T = Any) -> None:
        self._primeorigin = primeorigin
        self._index = index
        self._asType = asType

    def asTypeof(self, dtype: _S) -> Origin[_S]:
        return Origin(self._primeorigin, self._index, dtype)
    
    @allowed_overrun
    def __getitem__(self, name: str) -> _T:
        return self._primeorigin[name][self._index]

    @allowed_overrun
    def __getattr__(self, name: str) -> _T:
        return self._primeorigin[name][self._index]

class FieldInitializeOption(TypedDict):
    name: str
    dtype: _T
    initializer: Callable[[This, Origin], _T]

class OriginLoadingOption(TypedDict):
    loader_function: Callable[..., DataFrame]
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]