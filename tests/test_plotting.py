import mymltoolkit as mlt
import pandas as pd


def test_plotting():
    linedf = pd.DataFrame(
        {
            "a": [0, 1, 2],
            "b": [1, 3, 2],
        },
        index=[0, 1, 2],
    )
    _line = mlt.lineplot().func(linedf)
