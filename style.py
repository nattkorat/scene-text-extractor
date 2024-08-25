def border():
    return """
        border: 1px solid gray;
        border-radius: 10px;
        qproperty-alignment: AlignCenter;
        """

def button(color):
    return f"""
        width: 100px;
        background-color: {color};
        border: 1px solid {color};
        border-radius: 10px;
        padding: 5px;
    """

