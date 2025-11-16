# Databricks notebook source
import requests
import json
from datetime import datetime
import os
import yaml

from utils import ExportGenie

# Example parameters (for reference only; not executed here)
# Base Directory (location of git folder):
#   /Workspace/Users/<user>/Genie Spaces Eval/edh-enterprise-aibi-genie-sales
# dev genie space id (id of space to be updated):
#   01f0b8ff98dd1c2e8bae94417a321946
# genie_directory (location in the file system where genie
#   space has been developed):
#   /Workspace/enterprise_aibi_genie/sales/pipeline
# genie_name: Pipeline_and_CE_Analysis
# host_name: https://qualcomm-edh-enterprise-ws-dev.cloud.databricks.com
# path_to_genie_folder: src/sales_genie_spaces

# ---------------------------------------------------------
# Load parameters from yaml / widgets
# ---------------------------------------------------------

dbutils.widgets.text("host_name", "", "host name")
dbutils.widgets.text("src_genie_space_id", "", "dev genie space id")
dbutils.widgets.text("genie_dir", "", "genie directory")
dbutils.widgets.text("path_to_genie_folder", "", "path to genie folder")
dbutils.widgets.text("genie_name", "", "genie name")
dbutils.widgets.text("env", "", "environment")

host_name = dbutils.widgets.get("host_name")
src_genie_space_id = dbutils.widgets.get("src_genie_space_id")
path_to_genie_folder = dbutils.widgets.get("path_to_genie_folder")
genie_name = dbutils.widgets.get("genie_name")
env = dbutils.widgets.get("env")

# param by user
# root_dir: root path of the git directory
# ex. /Workspace/Users/<user>@qualcomm.com/edh-enterprise-aibi-genie-sales/
dbutils.widgets.text("root_dir", "", "Base Directory")
root_dir = dbutils.widgets.get("root_dir")

# api headers and authentication
TOKEN = (
    dbutils.notebook.entry_point.getDbutils()
    .notebook()
    .getContext()
    .apiToken()
    .get()
)

# ---------------------------------------------------------
# export all genie spaces
# ---------------------------------------------------------
export_genie = ExportGenie(
    host_name, TOKEN, root_dir, genie_name, src_genie_space_id, path_to_genie_folder, env
)
export_genie()