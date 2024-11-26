#!/usr/bin/python
"""esri scraper"""

import logging
from typing import Optional

import arcgis

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)


class Esri:
    def __init__(
        self,
        configuration: Configuration,
        retriever: Retrieve,
        username: str,
        password: str,
    ):
        self._configuration = configuration
        self._retriever = retriever
        self._username = username
        self._password = password
        self.data = {}

    def list_layers(self) -> None:
        portal = arcgis.gis.GIS(
            self._configuration["base_url"],
            username=self._username,
            password=self._password,
        )
        maps = portal.content.search(
            query="type:Web Map", item_type="Web Map", max_items=1000
        )

    def generate_dataset(self, layer: str) -> Optional[Dataset]:
        # To be generated
        dataset_name = None
        dataset_title = None
        dataset_time_period = None
        dataset_tags = None
        dataset_country_iso3 = None

        # Dataset info
        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
            }
        )

        dataset.set_time_period(dataset_time_period)
        dataset.add_tags(dataset_tags)
        # Only if needed
        dataset.set_subnational(True)
        dataset.add_country_location(dataset_country_iso3)

        # Add resources here

        return dataset
