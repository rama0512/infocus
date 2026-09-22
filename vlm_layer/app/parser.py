def parse_prediction(prediction: str):
    if not prediction:
        return None

    result = {}

    for line in prediction.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        result[key.strip()] = value.strip()
    print("[parser]",result)
    return result