import pandas as pd
from utils.viz import bar_chart, line_chart_timeseries

# Test bar_chart without color
_df = pd.DataFrame({"reg_name": ["A", "B"], "val": [1, 2]})
chart1 = bar_chart(_df, x="reg_name", y="val")
print("bar_chart ok:", type(chart1).__name__)

# Test line_chart_timeseries without color
_df2 = pd.DataFrame({"year": [2020, 2021], "value": [10, 12]})
chart2 = line_chart_timeseries(_df2, x="year", y="value")
print("line_chart ok:", type(chart2).__name__)
