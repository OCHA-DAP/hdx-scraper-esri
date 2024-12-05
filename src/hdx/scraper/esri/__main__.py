#!/usr/bin/python
"""
Top level script. Calls other functions that generate datasets that this
script then creates in HDX.

"""

import argparse
import logging
from os import getenv
from os.path import dirname, expanduser, join

from hdx.api.configuration import Configuration
from hdx.facades.keyword_arguments import facade
from hdx.utilities.path import (
    wheretostart_tempdir_batch,
)

from esri import Esri

logger = logging.getLogger(__name__)

_USER_AGENT_LOOKUP = "hdx-scraper-esri"
_SAVED_DATA_DIR = "saved_data"  # Keep in repo to avoid deletion in /tmp
_UPDATED_BY_SCRIPT = "HDX Scraper: Esri"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-un", "--username", default=None, help="Esri username")
    parser.add_argument("-pw", "--password", default=None, help="Esri password")
    args = parser.parse_args()
    return args


def main(
    username: str,
    password: str,
    **ignore,
) -> None:
    """Generate datasets and create them in HDX

    Args:
        username (str): Esri username
        password (str): Esri password

    Returns:
        None
    """
    with wheretostart_tempdir_batch(folder=_USER_AGENT_LOOKUP) as info:
        configuration = Configuration.read()
        esri = Esri(configuration, username, password)
        esri.list_layers()
        for layer_name in esri.data:
            dataset = esri.generate_dataset(layer_name)
            dataset.update_from_yaml(
                path=join(dirname(__file__), "config", "hdx_dataset_static.yaml")
            )
            dataset.create_in_hdx(
                remove_additional_resources=True,
                match_resource_order=False,
                hxl_update=False,
                updated_by_script=_UPDATED_BY_SCRIPT,
                batch=info["batch"],
            )


if __name__ == "__main__":
    args = parse_args()
    username = args.username
    if username is None:
        username = getenv("ESRI_USERNAME")
    password = args.password
    if password is None:
        password = getenv("ESRI_PASSWORD")
    facade(
        main,
        hdx_site="dev",
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yaml"),
        user_agent_lookup=_USER_AGENT_LOOKUP,
        project_config_yaml=join(
            dirname(__file__), "config", "project_configuration.yaml"
        ),
        username=username,
        password=password,
    )
