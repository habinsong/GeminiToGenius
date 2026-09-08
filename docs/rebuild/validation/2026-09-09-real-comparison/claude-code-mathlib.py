def clamp(value, lower, upper):
    if lower > upper:
        raise ValueError(f"lower({lower}) must not be greater than upper({upper})")
    return min(max(value, lower), upper)
