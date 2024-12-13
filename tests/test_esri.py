import json
from os.path import join

import pytest
from hdx.api.configuration import Configuration
from hdx.utilities.errors_onexit import ErrorsOnExit
from hdx.utilities.useragent import UserAgent

from hdx.scraper.esri.esri import Esri


class TestEsri:
    @pytest.fixture(scope="function")
    def configuration(self, config_dir):
        UserAgent.set_global("test")
        Configuration._create(
            hdx_read_only=True,
            hdx_site="prod",
            project_config_yaml=join(config_dir, "project_configuration.yaml"),
        )
        return Configuration.read()

    @pytest.fixture(scope="class")
    def fixtures_dir(self):
        return join("tests", "fixtures")

    @pytest.fixture(scope="class")
    def input_dir(self, fixtures_dir):
        return join(fixtures_dir, "input")

    @pytest.fixture(scope="class")
    def config_dir(self, fixtures_dir):
        return join("src", "hdx", "scraper", "esri", "config")

    def test_esri(self, configuration, fixtures_dir, input_dir, config_dir):
        esri = Esri(configuration, "", "", ErrorsOnExit())
        with open(join(input_dir, "contents.json")) as f:
            contents = json.loads(f.read())
        layer_names = esri.list_layers(contents)
        assert layer_names == ["HTI_Webmaps_ITOS_OSM_vector_tile_cad"]

        dataset = esri.generate_dataset("HTI_Webmaps_ITOS_OSM_vector_tile_cad")
        dataset.update_from_yaml(path=join(config_dir, "hdx_dataset_static.yaml"))
        assert dataset == {
            "name": "hti-webmaps-itos-osm-vector-tile-cad",
            "title": "Haiti: Webmaps ITOS OSM vector tile cad",
            "notes": "test",
            "dataset_date": "[2024-06-27T00:00:00 TO 2024-06-27T00:00:00]",
            "tags": [
                {
                    "name": "roads",
                    "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                }
            ],
            "groups": [{"name": "hti"}],
            "license_id": "cc-by",
            "methodology": "Other",
            "methodology_other": "Other",
            "caveats": "None",
            "dataset_source": "HDX",
            "package_creator": "HDX Data Systems Team",
            "private": False,
            "maintainer": "aa13de36-28c5-47a7-8d0b-6d7c754ba8c8",
            "owner_org": "hdx",
            "data_update_frequency": 365,
            "subnational": "1",
            "dataset_preview": "no_preview",
        }

        resources = dataset.get_resources()
        assert resources == [
            {
                "name": "HTI_Webmaps_ITOS_OSM_vector_tile_cad",
                "description": " ",
                "url": "https://gis.unocha.org/server/rest/services/Hosted/HTI_Webmaps_ITOS_OSM_vector_tile_cad/VectorTileServer",
                "format": "geoservice",
                "resource_type": "api",
                "url_type": "api",
            }
        ]
