#!/usr/bin/python
"""
Top level script. Calls other functions that generate datasets that this
script then creates in HDX.

"""

import argparse
import logging
from os import getenv
from os.path import dirname, expanduser, join

from esri import Esri
from hdx.api.configuration import Configuration
from hdx.facades.keyword_arguments import facade
from hdx.utilities.downloader import Download
from hdx.utilities.path import (
    wheretostart_tempdir_batch,
)
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)

_USER_AGENT_LOOKUP = "hdx-scraper-esri"
_SAVED_DATA_DIR = "saved_data"  # Keep in repo to avoid deletion in /tmp
_UPDATED_BY_SCRIPT = "HDX Scraper: Esri"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-un", "--username", default=None, help="Esri username")
    parser.add_argument("-pw", "--password", default=None, help="Esri password")
    parser.add_argument(
        "-sv",
        "--save",
        default=False,
        action="store_true",
        help="Save downloaded data",
    )
    parser.add_argument(
        "-usv",
        "--use_saved",
        default=False,
        action="store_true",
        help="Use saved data",
    )
    args = parser.parse_args()
    return args


def main(
    username: str,
    password: str,
    save: bool = True,
    use_saved: bool = False,
    **ignore,
) -> None:
    """Generate datasets and create them in HDX

    Args:
        username (str): Esri username
        password (str): Esri password
        save (bool): Save downloaded data. Defaults to True.
        use_saved (bool): Use saved data. Defaults to False.

    Returns:
        None
    """
    with wheretostart_tempdir_batch(folder=_USER_AGENT_LOOKUP) as info:
        temp_dir = info["folder"]
        with Download() as downloader:
            retriever = Retrieve(
                downloader=downloader,
                fallback_dir=temp_dir,
                saved_dir=_SAVED_DATA_DIR,
                temp_dir=temp_dir,
                save=save,
                use_saved=use_saved,
            )
            configuration = Configuration.read()
            esri = Esri(configuration, retriever, username, password)
            esri.list_layers()
            for layer in esri.data:
                dataset = esri.generate_dataset(layer)
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
        save=args.save,
        use_saved=args.use_saved,
    )
