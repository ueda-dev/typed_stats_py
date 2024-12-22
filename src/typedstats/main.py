from ._types import Field, FieldInitializeOption, OriginLoadingOption, Origin, This, PrimeOrigin, PrimeThis
import pandas as pd
import numpy as np
from types import UnionType

def _primeIter(this: PrimeThis, origin: PrimeOrigin):
    iter_count = max([len(origin) ,*[len(field) for field in this._fields.values()]])
    for i in range(iter_count):
        yield (This(this, i), Origin(origin, i))

class TypedDataset:
    def __init__(self, loading_option: OriginLoadingOption, *fields: FieldInitializeOption) -> None:
        if not callable(loading_option['loader_function']):
            raise ValueError('Loader function must be callable')

        args = loading_option.get('args', [])
        kwargs = loading_option.get('kwargs', {})
        unknown = loading_option['loader_function'](*args, **kwargs)
        if not isinstance(unknown, pd.DataFrame):
            raise ValueError('Loader function must return a pandas DataFrame')

        self._origin = PrimeOrigin.from_df(unknown)
        self._this = PrimeThis()

        for field in fields:
            self._initialize_field(field, self._this, self._origin)
    
    @classmethod
    def _initialize_field(cls, option: FieldInitializeOption, primethis: PrimeThis, primeorigin: PrimeOrigin) -> None:
        field = [option['initializer'](this, origin) for this, origin in _primeIter(primethis, primeorigin)]

        #遅延評価を行う場合は型チェックが効かない
        if not any([callable(f) for f in field]):
            if isinstance(option['dtype'], UnionType):
                if not all(isinstance(x, option['dtype'].__args__) for x in field):
                    raise ValueError(f'Field {option["name"]} must be {option["dtype"]}')
                
            else:
                if not all(isinstance(x, option['dtype']) for x in field):
                    raise ValueError(f'Field {option["name"]} must be {option["dtype"]}')
        
        primethis._fields[option['name']] = Field(data=field, dtype=option['dtype'])

    def __str__(self) -> str:
        return str(self.to_df())

    def to_df(self) -> pd.DataFrame:
        return self._this.to_df()
    
    def to_ndarray(self) -> np.ndarray:
        return self.to_df().values
    
    def to_dict(self) -> dict:
        return {name: field.data for name, field in self._this._fields.items()}