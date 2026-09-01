from pathlib import Path

from amon_hen.common.filesystem import get_script_data_dir, get_script_log_dir

SCRIPT_NAME = __package__.split(".")[-1]

# Storage
DATA_DIR = get_script_data_dir(SCRIPT_NAME)
LOG_DIR = get_script_log_dir(SCRIPT_NAME)

CLEARED_DIR = DATA_DIR / "cleared"
FRAMEWORK_DIR = DATA_DIR / "framework"

# QUERY SETTINGS
MAX_RESULTS = 999999

CLEARED_PARAMS = {
    "id": "gsp_index",
}

CLEARED_DATA = {
    "async_load_trigger": "viewport",
    "async_load": False,
    "color": "default",
    "sp_column_dv": "",
    "sp_column": "63617df797abba1079fcf1511153af09",
    "sp_page": "",
    "title": "Blue List Products",
    "enable_filter": "false",
    "sys_class_name": "sp_instance_table",
    "size_dv": "Medium",
    "window_size": str(MAX_RESULTS),
    "advanced_placeholder_dimensions": False,
    "sys_name": "Blue List Products",
    "show_breadcrumbs": True,
    "field_list": "name,cmdb_model_category,manufacturer",
    "table": "cmdb_model",
    "sp_widget": "a1d7078997d0cb10f66f32121153af6e",
    "order": -1,
    "sys_class_name_dv": "Instance with Table",
    "d": "asc",
    "useInstanceTitle": True,
    "active": False,
    "async_load_device_type": "desktop,tablet,mobile",
    "color_dv": "Default",
    "order_direction": "asc",
    "sys_tags": "",
    "placeholder_dimensions_script": 'function evaluateConfig(options) { return {\t"mobile": {\t\t"height": "250px",\t\t"width": "100%"\t},\t"desktop": {\t\t"height": "250px",\t\t"width": "100%"\t},\t"tablet": {\t\t"height": "250px",\t\t"width": "100%"\t}}; }',
    "o": "name",
    "filter": "cmdb_model_category=ff00a95597844b9079fcf1511153afa3",
    "maximum_entries": 15,
    "preserve_placeholder_size": False,
    "sp_widget_dv": "",
    "async_load_trigger_dv": "Viewport | The widget will only load when it comes into view on the screen",
    "size": "md",
    "sp_page_dv": "",
    "order_by": "sys_created_on",
    "placeholder_dimensions": '{\r\t"mobile": {\r\t\t"height": "250px",\r\t\t"width": "100%"\r\t},\r\t"desktop": {\r\t\t"height": "250px",\r\t\t"width": "100%"\r\t},\r\t"tablet": {\r\t\t"height": "250px",\r\t\t"width": "100%"\r\t}\r}',
    "placeholder_template": '<!-- \n\tAngularJS template with configurable options.\n\tUse the `options` object to control dynamic behavior.\n\tExample: Display an element when max row count is 10:\n\t<div ng-if="options.maxRowCount === 10"></div>\n\tThe `skeleton-container` class is used for loading placeholders.\n-->\n\t<div class="skeleton-container">\n\t<!-- Header Skeleton -->\n\t<div class="skeleton-box skeleton-header"></div>\n\t<!-- Body Skeleton -->\n\t<div class="skeleton-box skeleton-line"></div>\n\t<div class="skeleton-box skeleton-line small"></div>\n\t<div class="skeleton-box skeleton-line medium"></div>\n</div>',
    "fields": "name,cmdb_model_category,manufacturer",
    "order_direction_dv": "Ascending",
    "headerTitle": "Blue List Products",
    "columnFilters": {
        "cmdb_model_category": "ff00a95597844b9079fcf1511153afa3",
    },
    "filterOutConditions": [],
    "p": 1,
    "activeKeywords": None,
    "sessionRotationTrigger": True,
}

FRAMEWORK_PARAMS = {
    "id": "framework_list",
}

FRAMEWORK_DATA = {
    "async_load_trigger": "viewport",
    "async_load": False,
    "color": "default",
    "show_keywords": True,
    "sp_column_dv": "",
    "sp_column": "e7eb9ef697800b10f66f32121153af27",
    "sp_page": "",
    "title": "List of Cleared Components",
    "enable_filter": True,
    "sys_class_name": "sp_instance_table",
    "size_dv": "Medium",
    "window_size": str(MAX_RESULTS),
    "advanced_placeholder_dimensions": False,
    "sys_name": "List of Cleared Components",
    "show_breadcrumbs": True,
    "field_list": "name,cmdb_model_category,manufacturer",
    "table": "cmdb_model",
    "sp_widget": "a1d7078997d0cb10f66f32121153af6e",
    "order": -1,
    "sys_class_name_dv": "Instance with Table",
    "d": "desc",
    "widget_parameters": '{\n\t"enable_filter": {\n\t\t"value": true,\n\t\t"displayValue": true\n\t},\n\t"show_keywords": true,\n\t"show_breadcrumbs": true\n}',
    "useInstanceTitle": True,
    "active": False,
    "async_load_device_type": "desktop,tablet,mobile",
    "color_dv": "Default",
    "order_direction": "desc",
    "sys_tags": "",
    "placeholder_dimensions_script": 'function evaluateConfig(options) { return {\t"mobile": {\t\t"height": "250px",\t\t"width": "100%"\t},\t"desktop": {\t\t"height": "250px",\t\t"width": "100%"\t},\t"tablet": {\t\t"height": "250px",\t\t"width": "100%"\t}}; }',
    "o": "sys_created_on",
    "filter": "parent_cateogry=b700a95597844b9079fcf1511153afa2",
    "maximum_entries": 50,
    "preserve_placeholder_size": False,
    "sp_widget_dv": "",
    "async_load_trigger_dv": "Viewport | The widget will only load when it comes into view on the screen",
    "size": "md",
    "sp_page_dv": "",
    "order_by": "sys_created_on",
    "placeholder_dimensions": '{\r\t"mobile": {\r\t\t"height": "250px",\r\t\t"width": "100%"\r\t},\r\t"desktop": {\r\t\t"height": "250px",\r\t\t"width": "100%"\r\t},\r\t"tablet": {\r\t\t"height": "250px",\r\t\t"width": "100%"\r\t}\r}',
    "placeholder_template": '<!-- \n\tAngularJS template with configurable options.\n\tUse the `options` object to control dynamic behavior.\n\tExample: Display an element when max row count is 10:\n\t<div ng-if="options.maxRowCount === 10"></div>\n\tThe `skeleton-container` class is used for loading placeholders.\n-->\n\t<div class="skeleton-container">\n\t<!-- Header Skeleton -->\n\t<div class="skeleton-box skeleton-header"></div>\n\t<!-- Body Skeleton -->\n\t<div class="skeleton-box skeleton-line"></div>\n\t<div class="skeleton-box skeleton-line small"></div>\n\t<div class="skeleton-box skeleton-line medium"></div>\n</div>',
    "fields": "name,cmdb_model_category,manufacturer",
    "order_direction_dv": "Descending",
    "headerTitle": "List of Cleared Components",
    "sessionRotationTrigger": True,
}

# URLs
BLUE_LIST_URL = "https://tyrionprod.servicenowservices.com/api/now/sp/widget/4cebea4d9710cb10f66f32121153afaa"
