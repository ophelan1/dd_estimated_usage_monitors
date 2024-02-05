#!/opt/homebrew/bin/python3
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.model.monitor import Monitor
from datadog_api_client.v1.model.monitor_formula_and_function_event_aggregation import (
    MonitorFormulaAndFunctionEventAggregation,
)
from datadog_api_client.v1.model.monitor_formula_and_function_event_query_definition import (
    MonitorFormulaAndFunctionEventQueryDefinition,
)
from datadog_api_client.v1.model.monitor_formula_and_function_event_query_definition_compute import (
    MonitorFormulaAndFunctionEventQueryDefinitionCompute,
)
from datadog_api_client.v1.model.monitor_formula_and_function_event_query_definition_search import (
    MonitorFormulaAndFunctionEventQueryDefinitionSearch,
)
from datadog_api_client.v1.model.monitor_formula_and_function_events_data_source import (
    MonitorFormulaAndFunctionEventsDataSource,
)
from datadog_api_client.v1.model.monitor_options import MonitorOptions
from datadog_api_client.v1.model.monitor_thresholds import MonitorThresholds
from datadog_api_client.v1.model.monitor_type import MonitorType
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

##############################
### Function Definitions #####
##############################
# Function to create an estimated usage monitor given the metric name
def create_monitor(metric_name, global_config):

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


# Function to get the list of estimated usage metrics
def get_est_metrics(global_config):
    metric_list = []
    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)
        response = api_instance.list_active_metrics(
            _from=int(time.time()),
        )

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
            _from=int((datetime.now() + relativedelta(minutes=-30)).timestamp()),
            to=int(datetime.now().timestamp()),
            query=metric+"{*}",
        )

    return (response.series[0].pointlist)

##############################
### Global Variables #########
##############################
configuration = Configuration()
time_window=30


# This section gets all metrics, and adds those with "datadog.estiamted_usage" in the name to the list "estimated_usage_metrics"
estimated_usage_metrics = get_est_metrics(configuration)
print("Done Getting Existing Metrics")

# This section gets sample values for each metric
for metric in estimated_usage_metrics:
    metric_values=get_metric_values(configuration, metric)
    print(metric_values)
    for value in metric_values:
        print(value.value[1])
    print("Done Getting Metric Values for: "+metric)





# This section goes through estimated_usage_metrics and creates a monitor for each metric            
#for metric in estimated_usage_metrics:
#    create_monitor(metric, configuration)
#    break