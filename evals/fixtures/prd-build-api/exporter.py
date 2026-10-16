from sdk import Dimensions, encode


def export(text, width, height):
    dimensions = Dimensions(width, height)
    return encode_frame(text, dimensions.width_px, dimensions.height_px)
