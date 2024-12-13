#!/usr/bin/python
"""esri scraper"""

import logging
from datetime import datetime
from typing import List, Optional

import arcgis
from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.location.country import Country
from hdx.utilities.errors_onexit import ErrorsOnExit
from slugify import slugify

logger = logging.getLogger(__name__)


class Esri:
    def __init__(
        self,
        configuration: Configuration,
        username: str,
        password: str,
        errors: ErrorsOnExit,
    ):
        self._configuration = configuration
        self._username = username
        self._password = password
        self._errors = errors
        self.data = {}

    def get_portal_contents(self) -> List:
        portal = arcgis.gis.GIS(
            self._configuration["base_url"],
            username=self._username,
            password=self._password,
        )
        contents = portal.content.search(query="tags:HDX Public", max_items=1000)
        return contents

    def list_layers(self, contents: List) -> List[str]:
        for content in contents:
            date_created = content["created"] / 1000
            date_created = datetime.utcfromtimestamp(date_created)
            self.data[content["name"]] = {
                "name": content["name"],
                "description": content["description"],
                "date_created": date_created,
                "owner": content["owner"],
                "tags": content["tags"],
                "title": content["title"],
                "type": content["type"],
                "url": content["url"],
            }
        return list(self.data.keys())

    def generate_dataset(self, layer_name: str) -> Optional[Dataset]:
        layer_info = self.data[layer_name]
        dataset_name = slugify(layer_info["name"])
        dataset_title = layer_info["title"]
        dataset_time_period = layer_info["date_created"]
        dataset_tags = layer_info["tags"]
        dataset_country_iso3 = dataset_name[:3]

        country_name = Country.get_country_name_from_iso3(dataset_country_iso3)
        if not country_name:
            self._errors.add(f"{layer_name}: Could not find country name")
            return None

        dataset_title = dataset_title.replace("_", " ")
        dataset_title = f"{country_name}: {dataset_title[4:]}"

        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
            }
        )

        dataset["notes"] = layer_info["description"]
        dataset["notes"] = "test"  # TODO: remove once working
        if not dataset["notes"]:
            self._errors.add(f"{layer_name}: No dataset description")
            return None
        dataset.set_time_period(dataset_time_period)
        dataset.add_tags(dataset_tags)
        dataset.add_tags(["roads"])  # TODO: remove once working
        if len(dataset.get_tags()) == 0:
            self._errors.add(f"{layer_name}: No dataset tags")
            return None
        dataset.add_country_location(dataset_country_iso3)

        resource_format = layer_info["type"]
        resource_format = self._configuration["file_type_lookup"].get(
            resource_format, resource_format
        )
        resource_data = {
            "name": layer_info["name"],
            "description": " ",
            "url": layer_info["url"],
            "format": resource_format,
        }

        dataset.add_update_resource(resource_data)

        return dataset
