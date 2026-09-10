from robot.api import FatalError
from robot.libraries.BuiltIn import BuiltIn
from Browser.utils import logger
 
def check_data_in_definition(name, field_definition, data):
    fail_missing = BuiltIn().get_variable_value("${fail_missing_field_definition}", False)
    nr_def_missing = 0
    for key, _ in data.items():
        if key not in field_definition:
            nr_def_missing += 1
            logger.warn(f"Data field '{key}' not found in definition of '{name}'" )

    if fail_missing and nr_def_missing > 0:
        raise FatalError(f"Missing definitions (count: {nr_def_missing}) in '{name}'. See warnings." )
