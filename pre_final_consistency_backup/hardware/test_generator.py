#!/usr/bin/env python3
"""
Test script to diagnose and optimize Device 1 Rev 2.0 routing
"""
import os
import re
import math
import pcbnew

def mm_to_nm(mm):
    return int(mm * 1e6)

def nm_to_mm(nm):
    return nm / 1e6

def vec(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm_to_nm(x_mm), mm_to_nm(y_mm))

print("pcbnew loaded successfully")
