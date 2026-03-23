"""Constants for the Grizzl-E integration."""

DOMAIN = "grizzle"
MANUFACTURER = "United Chargers"

CONF_HOST = "host"

# API endpoints
ENDPOINT_INIT = "/init"
ENDPOINT_MAIN = "/main"
ENDPOINT_PAGE_EVENT = "/pageEvent"
ENDPOINT_OCPP_EVENT = "/ocppEvent"

# Charger states
CHARGER_STATES = {
    0: "Starting",
    1: "System Test",
    2: "Waiting",
    3: "Connected",
    4: "Charging",
    5: "Charge Complete",
    6: "Suspended",
    7: "Error",
}

CHARGER_ERRORS = {
    0: "No error",
    1: "Ground fault",
    2: "Leakage current H",
    3: "Relay error",
    4: "Leakage current L",
    5: "Box overheat",
    6: "Plug overheat",
    7: "Pilot error",
    8: "Low voltage",
    9: "Diode error",
    10: "Overcurrent",
    11: "Interface timeout",
    12: "Software failure",
    13: "GFCI test failure",
    14: "High voltage",
}

PILOT_STATES = {
    0: "Unknown",
    1: "Not connected",
    2: "Connected",
    3: "Charging",
}
