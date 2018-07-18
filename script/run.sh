#!/bin/bash

echo "csv2Properties"
./csv2Properties-all.sh

echo "sync"
python sync.py
