# TYPED_STAT_PY
## コンセプト（こんな記述ができるよ）
>[!NOTE]
>データセットの読み込み&前処理を、「型安全に」 「1つの式で」実行できます。ごちゃごちゃした分かりずらいコーディングからはおさらばです。
```{python}
from typed_stats import TypedDataset
import pandas as pd

# Create a TypedDataset
dataset = TypedDataset(
    {
        'loader_function': pd.read_csv,
        'args': ['sample.csv']
    },
    {
        'name': 'hoge',
        'dtype': str | int,
        'initializer': lambda this, origin: origin.asTypeof(str)['hoge']
    },
    {
        'name': 'hoge-upper',
        'dtype': str,
        'initializer': lambda this, origin: this.asTypeof(str)['hoge'].upper()
    },
    {
        'name': 'hoge-delayed',
        'dtype': str,
        'initializer': lambda this, origin: lambda: this['hoge']
    }

df = dataset.to_df()
)
```

## TypedDatasetの使い方
>[!NOTE]
>TypedDatasetに渡されるオブジェクトは全て辞書です。TypedDictで型を定義しているのでインテリセンスが効くと思います。
### 第一引数
- `loader_function`: データセットを読み込む関数です。戻り値がpandas.DataFrameの関数であればOK
- `args`: 先述の関数に渡す位置引数
- `kwargs`: 先述の関数に渡すキーワード引数

### 第二引数以降
- `name`: データの列名。
- `dtype`: 任意のtypeオブジェクトまたはUnionTypeオブジェクト
- `initializer`: 関数オブジェクトです。戻り値が`dtype`で指定した型と一致しない場合、例外を送出します。この関数については複雑な仕様が存在するので後述します。

### initializerについて
上記のサンプルコードの`initializer`の値には、`lambda this, origin: ...`と続く関数オブジェクトが渡されています。 
ここから分かる通り、この関数は二つの引数を受け取ります。 
一つ目の`this`は、それまでに定義した他のフィールドを参照するためのインターフェースです。`this[...]`と記述することで参照可能です。ただし、未定義のフィールドを参照すると`KeyError`が送出されます。`this.asTypeof()`を利用することで型を明示的に変換できます。 
二つ目の`origin`は、第一引数で読み込んだデータフレームを参照するためのインターフェースです。操作方法は`this`と同じであるため割愛します。 
>[!TIP]
>`this`と`origin`で参照できるのは指定した列の「同じ行」にある値です。つまるところ、参照できる値は`List`でも`Series`でもなくスカラー型です。

>[!WARNING]
>テストコード内には`'initializer': lambda this, origin: lambda: this['hoge']`という記述があります。これは未評価の関数オブジェクトを渡すことで遅延評価を実現する仕組みですが、型チェックが効かなくなります。おそらく削除するので利用は非推奨です。



## 注意点
- 現時点では最適化が進んでおらず、パフォーマンスがかなり犠牲になっています。現状では小～中規模の分析向けです。
- 保守はいつまでやるか分からないです。もうスパゲッティコードの兆候が見えてる気がします...
- 近いうちにPython 3.11~に移行するかもしれません。（型引数内でのアンパッキングができるようになるらしいので...）
 
