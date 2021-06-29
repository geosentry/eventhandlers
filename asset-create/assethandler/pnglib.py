"""
Terrascope AssetHandler Package

The pnglib module contains functions to handle PNG assets triggers
"""

def generate_assetid(filename: str):
    """doc"""
    try:
        return filename.split("/")[-1].split(".")[0]

    except Exception as e:
        raise NameError(e)

def generate_assetdoc(filename: str):
    """doc"""
    try:
        pieces = filename.split("/")
        assettype = pieces[0]

        if assettype == "regions":
            return f"regions/{pieces[1]}/acquisitions/{pieces[2]}"
        elif assettype == "visuals":
            return f"visuals/{pieces[1]}"
        else:
            raise TypeError(assettype)

    except TypeError as e:
        raise TypeError(e)
    except Exception as e:
        raise NameError(e)
