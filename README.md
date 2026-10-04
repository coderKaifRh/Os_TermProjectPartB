# CSE-307: Operating Systems - Term Paper Project
Topic: Learning-Augmented Page Replacement vs. Classical Policies

---

## Setup Instructions

Requirements:
- Python 3.8 or any newer version.
- Operating System: Ubuntu Linux (or any Linux distribution inside VMware / VirtualBox).
- No external libraries or pip installations needed. The entire project is written in standard Python and runs out of the box.

Setup Steps:
1. Clone this repository into your Ubuntu environment:
   git clone https://github.com/coderKaifRh/Os_TermProjectPartB.git
2. Open a terminal inside the project directory:
   cd Os_TermProjectPartB
3. Verify Python 3 is installed by running:
   python3 --version

---

## How to Run

1. Run on Ubuntu / VMware with Kernel Resource Tracking:
   Command: bash run_ubuntu.sh
   (or: /usr/bin/time -v python3 main.py --ubuntu)
   This executes the benchmark and memory workload inside Ubuntu Linux, capturing kernel-level page faults, memory allocation, and context switches.

2. Run the Full Experiment Benchmark:
   Command: python3 main.py
   This executes the benchmark across FIFO, LRU, Optimal, and the Learned model, and automatically generates tables and charts in the results folder.

---

## Summary of Results

We evaluated FIFO, LRU, Belady's Optimal, and our Learned Decision Tree model on a 2,000-access reference string with a physical memory capacity of 6 frames. An abrupt workload shift was introduced at timestep 1000, transitioning from a locality-heavy pattern to random access and bursty streaming scans.

1. Algorithm Performance Comparison (Page Replacement):

Policy: FIFO
- Pre-Shift Hit Ratio: 59.80% (402 faults)
- Post-Shift Hit Ratio: 8.00% (920 faults)
- Overall Hit Ratio: 33.90%
- Total Page Faults: 1322

Policy: LRU
- Pre-Shift Hit Ratio: 60.00% (400 faults)
- Post-Shift Hit Ratio: 8.00% (920 faults)
- Overall Hit Ratio: 34.00%
- Total Page Faults: 1320

Policy: Optimal (Belady)
- Pre-Shift Hit Ratio: 69.80% (302 faults)
- Post-Shift Hit Ratio: 32.80% (672 faults)
- Overall Hit Ratio: 51.30%
- Total Page Faults: 974

Policy: Learned (Decision Tree)
- Pre-Shift Hit Ratio: 50.60% (494 faults)
- Post-Shift Hit Ratio: 13.50% (865 faults)
- Overall Hit Ratio: 32.05%
- Total Page Faults: 1359

2. Ubuntu / VMware System Measurements under Resource Constraints:
A 600 MB memory workload was executed inside an Ubuntu VM under three distinct resource conditions to observe Linux kernel demand paging and virtualization behavior:

Condition 1: High RAM (2 GB, Unconstrained)
- Major Page Faults: 0
- Minor Page Faults: 153,640
- Execution Time: 0.48 seconds
- OS Behavior: Clean demand paging in physical memory, zero disk swapping.

Condition 2: Moderate RAM (1 GB, Constrained)
- Major Page Faults: 42
- Minor Page Faults: 153,640
- Execution Time: 0.92 seconds
- OS Behavior: Moderate memory pressure, Linux kswapd background daemon activates to reclaim page cache.

Condition 3: Low RAM (512 MB, Overcommitted)
- Major Page Faults: 3,890 (Severe jump)
- Minor Page Faults: 153,640
- Execution Time: 3.84 seconds (8x slowdown)
- OS Behavior: Severe thrashing, RAM exhausted, active disk swap I/O (si/so).

3. Key Findings:
1. When the workload shifted from locality to random/bursty scanning, both FIFO and LRU collapsed by 86.7%, dropping from 60.00% to 8.00% hit ratio due to streaming scans causing cache pollution and thrashing.
2. The Learned model showed much higher resilience after the shift, maintaining a 13.50% hit ratio, which is nearly 70% higher than LRU and FIFO. Its decision tree uses both recency and windowed frequency, preventing single-use scan pages from flushing the active working set.
3. Belady's Optimal policy achieved the highest overall hit ratio of 51.30%, defining the theoretical upper bound.
4. The VM resource experiment verified core Virtualization and Memory Management concepts: dropping VM RAM from 2 GB to 512 MB caused major page faults to explode from 0 to 3,890, showing how physical memory overcommitment forces the hypervisor and guest OS into disk thrashing.

---

AI Disclosure:
Antigravity assistance was utilized for code syntax and debugging.
