#!/opt/homebrew/bin/python3
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.model.monitor import Monitor
from datadog_api_client.v1.model.monitor_type import MonitorType
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

##############################
### Function Definitions #####
##############################


# Function to create an estimated usage anomaly monitor given the metric name
def create_anomaly_monitor(metric_name, global_config):

    body = Monitor(
        name="Estimated Usage - "+metric_name,
        type=MonitorType.QUERY_ALERT,
        # query="avg(last_30m):outliers(avg:datadog.estimated_usage.sds.scanned_bytes{role:es-events-data} by {host}, 'dbscan', 7) > 0",
        query="avg(last_4h):anomalies(avg:datadog.estimated_usage.sds.scanned_bytes{*}, 'agile', 2, direction='above', interval=60, alert_window='last_10m', count_default_zero='true', seasonality='hourly') >= 0.75",
        message="test_message",
        tags=[
            "monitor_type:estimated_usage",
            "env:dev",
        ]
    )

    with ApiClient(global_config) as api_client:
        api_instance = MonitorsApi(api_client)
        response = api_instance.create_monitor(body=body)

        print(response)



# Function to create an estimated usage threshold monitor given the metric name, time window, and user-defined threshold
def create_threshold_monitor(metric_name, global_config, window, threshold):

    body = Monitor(
        name="Estimated Usage - "+metric_name[24:],
        type=MonitorType.QUERY_ALERT,
        query="avg(last_"+str(window)+"m):"+metric_name+"{*} > "+str(threshold),
        message="test_message",
        tags=[
            "monitor_type:estimated_usage",
            "env:dev",
        ]
    )

    with ApiClient(global_config) as api_client:
        api_instance = MonitorsApi(api_client)
        try:
            response = api_instance.create_monitor(body=body)
        except:
            print("Failed to Create Monitor")



# Function to get the list of estimated usage metrics
def get_est_metrics(global_config):
    metric_list = []
    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)
        try:
            response = api_instance.list_active_metrics(
                _from=int(time.time()),
            )
        except:
            print("Failed to Gather Estimated Metrics")

        for metric in response.metrics:
            # Fill the array with estimated_usage metrics
            if "datadog.estimated_usage" in metric:
                metric_list.append(metric)
    
    return metric_list



# Function to get the most recent values of a metric
def get_metric_values(global_config, metric):
    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)

        response = api_instance.query_metrics(
            _from=int((datetime.now() + relativedelta(minutes=-240)).timestamp()),
            to=int(datetime.now().timestamp()),
            query=metric+"{*}",
        )

    return (response.series[0].pointlist)

##############################
### Global Variables #########
##############################
configuration = Configuration()
time_window=10



##############################
### Main Program #############
##############################
# This section gets all estimated_usage metrics, and adds them to the list "estimated_usage_metrics"
print("The Selected Time Window Is: "+str(time_window)+ " min")
estimated_usage_metrics = get_est_metrics(configuration)
print("Done Getting Existing Estimated Usage Metrics from Your Account\n")

# This section gets sample values for each metric
for metric in estimated_usage_metrics:
    metric_values=get_metric_values(configuration, metric)
    value_count = len(metric_values)
    total = 0
    max_value = 0

    for item in metric_values:
        total = total + item.value[1]
        if item.value[1] > max_value: 
            max_value = item.value[1]
    
    avg_value = total / value_count


    print("Done Getting Metric Values for: "+metric)
    print("Avg Value over Last 4 Hours: " + str(avg_value))
    # print("Max Value over Last 4 Hours: " + str(max_value))

    create_bool = input("Would you like to create a monitor for this metric? (Y/N) : ")
    if create_bool == "Y": 
        user_threshold = input("What would you like the threshold to be? : ") 
        create_threshold_monitor(metric, configuration, time_window, user_threshold)

