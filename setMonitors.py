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
import time

### Global Variables and Function Definitions #####
# First, set the global Configuration
configuration = Configuration()

# Function to create an estimated usage monitor given the metric name
def my_function(metric_name, global_config):

    body = Monitor(
        name="Estimated Usage - "+metric_name,
        type=MonitorType.QUERY_ALERT,
        query="avg(last_30m):outliers(avg:system.cpu.user{role:es-events-data} by {host}, 'dbscan', 7) > 0",
        message="test_message",
        tags=[
            "test:examplemonitor",
            "env:dev",
        ],
        priority=3
    )


    with ApiClient(global_config) as api_client:
        api_instance = MonitorsApi(api_client)
        response = api_instance.create_monitor(body=body)

        print(response)


# This section gets all metrics, and adds those with "datadog.estiamted_usage" in the name to the list "estimated_usage_metrics"
estimated_usage_metrics = []
with ApiClient(configuration) as api_client:
    api_instance = MetricsApi(api_client)
    response = api_instance.list_active_metrics(
        _from=int(time.time()),
    )

    for metric in response.metrics:
        if "datadog.estimated_usage" in metric:
            estimated_usage_metrics.append(metric)


# This section goes through estimated_usage_metrics and creates a monitor for each metric            
for metric in estimated_usage_metrics:
    my_function(metric, configuration)
    break