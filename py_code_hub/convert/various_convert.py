def dynamic_cast(value, target_type: str):
    type_map = {
        "str": str,
        "int": int,
        "float": float,
        "bool": lambda v: str(v).lower() in ['true', '1', 'yes'],
        "list": lambda v: list(v) if isinstance(v, (str, list, set, tuple)) else [v],
        "set": lambda v: set(v) if isinstance(v, (str, list, set, tuple)) else {v},
        "dict": lambda v: eval(v) if isinstance(v, str) and v.strip().startswith("{") else {},
    }

    try:
        cast_func = type_map.get(target_type.lower())
        if not cast_func:
            raise ValueError(f"Unsupported target type: {target_type}")
        return cast_func(value)
    except Exception as e:
        print(f"Conversion error: {e}")
        return None  # Or raise if strict handling is preferred


print(dynamic_cast("1", "dict"))
