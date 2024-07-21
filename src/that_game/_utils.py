def is_float_close(f1: float, f2: float) -> bool:
    """比较两个浮点数是否足够接近。"""
    return abs(f1 - f2) < 1e-9
