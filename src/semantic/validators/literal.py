from semantic.custom_types import IntegerType, StringType, BoolType, NullType, ErrorType

def validateLiteral(text, errorList):
    if text.isdigit():
        return IntegerType()
    elif text.startswith('"') and text.endswith('"'):
        return StringType()
    elif text in ("true", "false"):
        return BoolType()
    elif text == "null":
        return NullType()
    else:
        errorList.append(f"Unknown literal type: {text}")
        return ErrorType()
