# Grizzl-E Home Assistant Integration

## Project Overview
Home Assistant custom integration for the Grizzl-E Ultimate EV charger via its local HTTP API. Replaces the Grizzl-E Connect app with full local control through HA.

## Charger Details
- **Model:** GRU 48A 2024
- **Serial:** GRU-L0000361456
- **IP:** 192.168.20.52 (Dunlap WiFi, 2.4GHz)
- **Hardware:** ESP32 (Espressif), hostname UC_EVSE
- **Firmware:** GRU077L-01.07.5 / ULGRW000A-03.15.2
- **Charging protocol:** J1772 (no vehicle SOC data available)

## Local API (all POST to port 80)
- `/init` — config data (design current, wifi settings, min current)
- `/main` — live polling data (state, voltage, current, power, temps, session/total energy, OCPP status, etc.)
- `/pageEvent` — send commands via form-encoded `name=value` with `pageEvent` header
- `/ocppEvent` — send OCPP-related commands (same format as /pageEvent)
- `/config`, `/configAP`, `/configHttp` — wifi/auth configuration
- `/scan`, `/scanResult` — wifi scanning
- `/get_logResult` — logs
- `/ocppconfig` — OCPP config page (behind basic auth, credentials unknown)

## Key Commands
| Command | Endpoint | Values | Notes |
|---------|----------|--------|-------|
| `evseEnabled` | /pageEvent | 0=charging allowed, 1=stopped | "Stop charging" flag, not "enabled" |
| `currentSet` | /pageEvent | 7-48 | **Only works when OCPP is disabled** |
| `ocppEnabled` | /ocppEvent | 0=off, 1=on | Cloud reconnect resets currentSet to cloud value |

## OCPP Cloud Behavior
- OCPP (United Chargers cloud) locks out local `currentSet` commands
- Disabling OCPP allows full local current control
- Re-enabling OCPP causes the cloud to push its stored value back immediately
- `evseEnabled` works regardless of OCPP state

## Integration Architecture
```
custom_components/grizzle/
├── __init__.py          # Entry setup, options update listener
├── api.py               # HTTP client (send_command for /pageEvent, send_ocpp_command for /ocppEvent)
├── config_flow.py       # Setup flow (IP address) + options flow (cost per kWh)
├── const.py             # Constants, state/error/pilot maps
├── coordinator.py       # DataUpdateCoordinator, polls /main every 5 seconds
├── entity.py            # Base entity with device info
├── sensor.py            # 16 sensors (voltage, current, power, energy, temps, state, OCPP, cost)
├── switch.py            # Charging toggle + OCPP cloud toggle
├── number.py            # Current limit slider + cost per kWh input
├── manifest.json
├── strings.json
└── translations/en.json
```

## Entities
- **Sensors:** Voltage, Current, Power, Session energy, Total energy, Session time, Relay temp, Plug temp, Current limit, Session cost (calculated), Wi-Fi signal, Charger state, Error, Plug state, OCPP status, OCPP vendor
- **Switches:** Charging (on/off), OCPP cloud (on/off)
- **Numbers:** Current limit (7-48A slider), Cost per kWh (persisted in config entry options)

## Development Notes
- Session cost is calculated locally (sessionEnergy × cost_per_kwh) since the charger's sessionMoney just mirrors kWh
- Cost per kWh is stored in config entry options and persists across restarts
- HACS compatible via hacs.json
- No Docker stack — this is a pure HA custom component
