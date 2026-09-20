import sys
sys.path.append("Device1/scripts")
from test_exact_drc import build_board

# Let us test:
# L3 at (6.7, 8.3, 0)
# C22 at (6.7, 7.25, 0)
# C23 at (6.7, 6.2, 0)
# R1 at (7.9, 4.2, 0)
# And BOOT0 routed on In2.Cu or B.Cu with a clean via at (7.9, 8.5) or (7.9, 7.6)!

# Wait, let us test where BOOT0 can drop a via!
# What if BOOT0 trace on F.Cu goes from (7.25, 9.5625) to (7.25, 8.9) -> (7.9, 8.9) -> (7.9, 8.5)?
# Let us check!
