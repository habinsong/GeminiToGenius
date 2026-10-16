"""이 사례에서 제공하는 SDK 전체입니다."""


class Dimensions:
    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("크기는 양수여야 합니다.")
        self.width = width
        self.height = height


def encode(text, dimensions):
    return {"text": text, "width": dimensions.width, "height": dimensions.height}
