#!/usr/bin/python
"""esri scraper"""

import logging
from datetime import datetime
from typing import Optional

import arcgis

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset

logger = logging.getLogger(__name__)


class Esri:
    def __init__(
        self,
        configuration: Configuration,
        username: str,
        password: str,
    ):
        self._configuration = configuration
        self._username = username
        self._password = password
        self.data = {}

    def list_layers(self) -> None:
        portal = arcgis.gis.GIS(
            self._configuration["base_url"],
            username=self._username,
            password=self._password,
        )
        maps = portal.content.search(query="tags:HDX Public", max_items=1000)
        for map in maps:
            date_created = map["created"] / 1000
            date_created = datetime.utcfromtimestamp(date_created)
            self.data[map["name"]] = {
                "name": map["name"],
                "description": map["description"],
                "date_created": date_created,
                "owner": map["owner"],
                "tags": map["tags"],
                "title": map["title"],
                "type": map["type"],
                "url": map["url"],
            }

    def generate_dataset(self, layer_info: dict) -> Optional[Dataset]:
        dataset_name = layer_info["name"]
        dataset_title = layer_info["title"].replace("_", " ")
        dataset_time_period = layer_info["date_created"]
        dataset_tags = layer_info["tags"]
        dataset_country_iso3 = dataset_name[:3]

        # Dataset info
        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
            }
        )

        dataset.set_time_period(dataset_time_period)
        dataset.add_tags(dataset_tags)
        dataset.set_subnational(True)
        dataset.add_country_location(dataset_country_iso3)

        resource_data = {
            "name": layer_info["name"],
            "description": " ",
            "url": layer_info["url"],
            "format": layer_info["type"],
        }

        dataset.add_update_resource(resource_data)

        return dataset
