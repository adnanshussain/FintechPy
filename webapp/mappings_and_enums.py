from enum import Enum

###############################
### Custom Enums            ###
###############################
class UserTypesEnum(Enum):
    public_portal = 1
    control_panel = 2
    cp_admin = 3
    developer = 4

###############################
### ID to Name Mappings     ###
###############################
STOCK_ENTITY_TYPE_TABLE_NAME = {
    1: "companies",
    2: "commodities",
    3: "markets",
    4: "sectors"
}
