# Housekeeping script to retrieve IOT device battery voltage levels from an InfluxDB 2.X
# server and generate alert messages if those volues are less than specified thresholds.
# 
# Device specifics are stored in a separate devices.ini configuration file, allowing
# flexible management of many devices without having to modify the script itself.


from influxdb_client import InfluxDBClient
import configparser
import sys

# Set these to match the data schema used in InfuxDB.  The overall measurement
# used for data storage is defined by the string value of 'influx_meas', and the 
# battery voltage value is stored in the field identified by the string value of
# 'influx_bvfield'.   Further, the device(s) of interest are defined in the
# devices.ini config file with the 'Key' attribute there matching the device
# name associated with the "device" key in InfluxDB.  For further info on InfluxDB
# measurements, fields, and keys consult the InfluxDB documentation
#
# Change these to match your local InfluxDB schema

influx_meas = "device"
influx_bvfield = "battery_volts"

# Load and parse devices config file (and Influx config info too)
config = configparser.ConfigParser()
config.read('devices.ini')

# Connect to InfluxDB server using info in separate config file
with InfluxDBClient.from_config_file("influx.ini") as client:
    query_api = client.query_api()

    """
    Query: using Bind parameters
    """
    query_avg = '''from(bucket: "home") |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == _meas)
        |> filter(fn: (r) => r["device"] == _device)
        |> filter(fn: (r) => r["_field"] == _bv_field)
        |> movingAverage(n:3)
        |> last()
        '''

    query = '''from(bucket: "home") |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == _meas)
        |> filter(fn: (r) => r["device"] == _device)
        |> filter(fn: (r) => r["_field"] == _bv_field)
        |> last()
        '''

    alert = False
    # Check each devices voltage, averaged over the last 3 reported values
    for device in config.sections():
        devcfg = config[device]
        bind_params = {'_device': devcfg['Key'],'_meas': influx_meas,'_bv_field': influx_bvfield}
        tables = query_api.query(query_avg, params=bind_params)
        for record in [record for table in tables for record in table.records]:
            if float(record['_value']) <= float(devcfg['threshold']):
                alert = True
                print("** ALERT! RECHARGE '%s' device: Battery @ %.4f volts (avg), below threshold of %.2f" % (devcfg['name'], float(record['_value']),float(devcfg['threshold'])))

if alert:
    print("")
    print("***** DEVICE BATTERY STATUS REPORT (Most recent values) *****")
    for device in config.sections():
        devcfg = config[device]
        bind_params = {'_device': devcfg['Key'],'_meas': influx_meas,'_bv_field': influx_bvfield}
        tables = query_api.query(query, params=bind_params)
        for record in [record for table in tables for record in table.records]:
            print("%s: %.2f volts at %s (alert threshold %.2f volts)" % (devcfg['name'],record['_value'],record['_time'].strftime("%H:%M:%S %Z %m/%d/%Y"),float(devcfg['threshold'])))
    sys.exit(1)
else:
    sys.exit(0)
