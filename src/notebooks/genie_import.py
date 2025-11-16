# Databricks notebook source
import requests
import json
from datetime import datetime
import os
import yaml

from utils import ImportGenie

# ---------------------------------------------------------
# Import an existing Genie Space from the JSON file
# Handles a single import for a given src_genie_space_id,
# tgt_genie_space_id, genie_dir
# ---------------------------------------------------------

# Load parameters from yaml / widgets
dbutils.widgets.text("src_genie_dir", "", "src genie directory")
dbutils.widgets.text("tgt_genie_dir", "", "tgt genie directory")
dbutils.widgets.text("src_genie_space_id", "", "src genie space id")
dbutils.widgets.text("tgt_genie_space_id", "", "target genie space id")
dbutils.widgets.text("host_name", "", "host name")
dbutils.widgets.text("warehouse_id", "", "sql warehouse id")
dbutils.widgets.text("env", "", "environment")

src_genie_dir = dbutils.widgets.get("src_genie_dir")
tgt_genie_dir = dbutils.widgets.get("tgt_genie_dir")
src_genie_space_id = dbutils.widgets.get("src_genie_space_id")
tgt_genie_space_id = dbutils.widgets.get("tgt_genie_space_id")
host_name = dbutils.widgets.get("host_name")
warehouse_id = dbutils.widgets.get("warehouse_id")
env = dbutils.widgets.get("env")

# api headers and authentication
TOKEN = (
    dbutils.notebook.entry_point.getDbutils()
    .notebook()
    .getContext()
    .apiToken()
    .get()
)

# import for all genie spaces defined in base_params
import_genie = ImportGenie(
    host_name,
    TOKEN,
    src_genie_dir,
    tgt_genie_dir,
    src_genie_space_id,
    tgt_genie_space_id,
    warehouse_id,
    env,
)
import_genie()
