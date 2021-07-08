"""
asset-create service

The png module contains functions to handle PNG assets triggers
"""
from .logentry import LogEntry

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

def handle_png(filename: str, log: LogEntry):
    """
    A handler function that performs the asset handle runtime for PNG assets.

    Adds the path to the file to the corresponding Firestore document and then 
    checks if that document has all the asset paths assigned, and if it does, 
    sends a PubSub message to the trigger the appropriate PDF build runtime.
    """
    from google.cloud import firestore

    log.addtrace("started PNG asset handler runtime")

    try:
        docpath = generate_assetdoc(filename)
        log.addtrace(f"asset document path generated. docpath - {docpath}")

        db = firestore.Client()
        log.addtrace(f"firestore client initialized")

        docref = db.document(docpath)
        docsnap = docref.get()

        if not docsnap.exists:
            log.addtrace(f"execution broke - could not find asset document on database.")
            return "CRITICAL", "runtime error.", "error-acknowledge"
            
    except NameError as e:
        log.addtrace(f"execution broke - could not generate asset document path from filename. {e}")
        return "ERROR", "runtime error.", "error-acknowledge"

    except TypeError as e:
        log.addtrace(f"execution terminated - triggered by unsupported asset type - {e}")
        return "INFO", "runtime terminated.", "termination-acknowledge"

    except Exception as e:
        log.addtrace(f"execution broke - could not initialize firestore client. {e}")
        return "ALERT", "system error.", "error-acknowledge"

    log.addtrace(f"asset document path valudated.")

    try:
        assetid = generate_assetid(filename)
        docref.set({f"asset-paths": {assetid: filename}}, merge=True)

    except NameError as e:
        log.addtrace(f"execution broke - could not generate asset ID from filename. {e}")
        return "ERROR", "runtime error.", "error-acknowledge"
        
    except Exception as e:
        log.addtrace(f"execution broke - could not update asset document. {e}")
        return "ALERT", "system error.", "error-acknowledge"
    
    log.addtrace(f"asset document updated")
    log.addtrace("ended PNG asset handler runtime")
    return "INFO", "PNG runtime complete", "success-acknowledge"
