import json
from datetime import datetime
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    """
    MongoDB'den gelen ObjectId ve datetime gibi özel tipleri JSON'a dönüştürebilen encoder.
    """
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def dump_json(obj):
    """
    Nesneyi JSON formatına dönüştürür.
    
    Args:
        obj: JSON'a dönüştürülecek nesne
        
    Returns:
        str: JSON string
    """
    return json.dumps(obj, cls=JSONEncoder)

def convert_mongo_document(doc):
    """
    MongoDB belgesini JSON serileştirilebilir bir dict'e dönüştürür.
    
    Args:
        doc (dict): MongoDB belgesi
        
    Returns:
        dict: JSON serileştirilebilir dict
    """
    if doc is None:
        return None
        
    if isinstance(doc, list):
        return [convert_mongo_document(item) for item in doc]
        
    if not isinstance(doc, dict):
        if isinstance(doc, ObjectId):
            return str(doc)
        if isinstance(doc, datetime):
            return doc.isoformat()
        return doc
    
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = convert_mongo_document(value)
        elif isinstance(value, list):
            result[key] = [convert_mongo_document(item) for item in value]
        else:
            result[key] = value
    
    return result 