# Script for migrating Grafana dashbords and data sources from one server to another.

## General info

### Downlod the script.

```
wget https://raw.githubusercontent.com/renjithrp/Grafana/main/migrate_grafana.py
```
### Export required authentication keys.

```
export SOURCE_GRAFANA_URL = ""
export SOURCE_GRAFANA_KEY = “”
export DEST_GRAFANA_URL = "
export DEST_GRAFANA_KEY = “”
```

### Run the script.

```
python3 migrate_grafana.py

``

