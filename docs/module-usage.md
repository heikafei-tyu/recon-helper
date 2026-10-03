# 分析模块用法

```python
from recon.dupes import find_duplicates
from recon.profile import column_profile
from recon.anomalies import detect_iqr
from recon.schema import validate_schema
from recon.fuzzy import match_column
```

这些函数接受字典行序列，返回可序列化的字典和列表。金额分析前应先用单位或汇率模块统一口径；结构校验应在正式核对前执行。
