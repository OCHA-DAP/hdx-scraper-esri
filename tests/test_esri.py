from os.path import join

import pytest
from hdx.api.configuration import Configuration
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
        esri = Esri(configuration, username="", password="")
        esri.list_layers()
        assert esri.data == {}

        dataset = esri.generate_dataset("layer_name")
        dataset.update_from_yaml(path=join(config_dir, "hdx_dataset_static.yaml"))
        assert dataset == {}

        resources = dataset.get_resources()
        assert resources == {}
