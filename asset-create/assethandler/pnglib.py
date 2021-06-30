"""
Terrascope AssetHandler Package

The pnglib module contains functions to handle PNG assets triggers
"""

def generate_assetid(filename: str):
    """ A function that returns an asset ID for a given filename. """
    try:
        return filename.split("/")[-1].split(".")[0]

    except Exception as e:
        raise NameError(e)

def generate_assetdoc(filename: str):
    """ A function that returns an asset document path for a given filename. """
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

def handle_png(filename: str, logtraces: list):
    """
    A handler function that performs the asset handle runtime for PNG assets.

    Adds the path to the file to the corresponding Firestore document and then 
    checks if that document has all the asset paths assigned, and if it does, 
    sends a PubSub message to the trigger the appropriate PDF build runtime.
    """
    from google.cloud import firestore

    logtraces.append("started PNG asset handler runtime")

    try:
        docpath = generate_assetdoc(filename)
        logtraces.append(f"asset document path generated. docpath - {docpath}")

        db = firestore.Client()
        logtraces.append(f"firestore client initialized")

        docref = db.document(docpath)
        docsnap = docref.get()

        if not docsnap.exists:
            logtraces.append(f"execution broke - could not find asset document on database.")
            return "CRITICAL", "runtime error.", "error-acknowledge", logtraces
            
    except NameError as e:
        logtraces.append(f"execution broke - could not generate asset document path from filename. {e}")
        return "ERROR", "runtime error.", "error-acknowledge", logtraces

    except TypeError as e:
        logtraces.append(f"execution terminated - triggered by unsupported asset type - {e}")
        return "INFO", "runtime terminated.", "termination-acknowledge", logtraces

    except Exception as e:
        logtraces.append(f"execution broke - could not initialize firestore client. {e}")
        return "ALERT", "system error.", "error-acknowledge", logtraces

    logtraces.append(f"asset document path valudated.")

    try:
        assetid = generate_assetid(filename)
        docref.set({f"asset-paths": {assetid: filename}}, merge=True)

    except NameError as e:
        logtraces.append(f"execution broke - could not generate asset ID from filename. {e}")
        return "ERROR", "runtime error.", "error-acknowledge", logtraces
        
    except Exception as e:
        logtraces.append(f"execution broke - could not update asset document. {e}")
        return "ALERT", "system error.", "error-acknowledge", logtraces
    
    logtraces.append(f"asset document updated")
    
    # check if all document assets have been generated.
    # send pubsub trigger to pdf-builds if true 

    logtraces.append("ended PNG asset handler runtime")
    return "INFO", "PNG runtime complete", "success-acknowledge", logtraces
