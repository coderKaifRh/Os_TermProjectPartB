# Page Replacement Policies: Comparative Evaluation

**Workload**: 2000 accesses across 40 virtual pages | **Cache Capacity**: 6 frames

| Policy | Pre-Shift Hit Ratio | Post-Shift Hit Ratio | Overall Hit Ratio | Total Faults |
| :--- | :---: | :---: | :---: | :---: |
| **FIFO** | 59.8% (402 faults) | 8.0% (920 faults) | **33.9%** | 1322 |
| **LRU** | 60.0% (400 faults) | 8.0% (920 faults) | **34.0%** | 1320 |
| **Optimal (Belady)** | 69.8% (302 faults) | 32.8% (672 faults) | **51.3%** | 974 |
| **Learned (Decision Tree)** | 37.5% (625 faults) | 13.2% (868 faults) | **25.35%** | 1493 |


## Bonus Track: Confidence Calibration Summary

| Confidence Bin | Total Evictions | Oracle Matches | Empirical Accuracy |
| :--- | :---: | :---: | :---: |
| Low Confidence [0.50 - 0.65) | 405 | 58 | 14.32% |
| Medium Confidence [0.65 - 0.80) | 53 | 7 | 13.21% |
| High Confidence [0.80 - 1.00] | 1029 | 168 | 16.33% |
