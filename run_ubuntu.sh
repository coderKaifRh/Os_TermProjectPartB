#!/bin/bash
echo "=========================================================="
echo "CSE-307: OS Memory & System Measurement Benchmark (Ubuntu)"
echo "Memory Management & Virtualization System Testing"
echo "=========================================================="
echo ""
echo "[1] Current Ubuntu Memory State (free -m):"
free -m
echo ""
echo "[2] Executing Benchmark with Kernel-level Resource Tracking (/usr/bin/time -v):"
/usr/bin/time -v python3 main.py --ubuntu
echo ""
echo "=========================================================="
echo "Measurements completed! Results saved in 'results/' folder."
echo "=========================================================="
