import re
import uuid
import random


def hash_processamento() -> str:
    
    string_uuid = re.sub("[^a-zA-Z0-9]", "", str(uuid.uuid4())).upper()
    hash = "".join(random.sample(string_uuid, 16))

    return hash
