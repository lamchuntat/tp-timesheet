"""Unit tests for the config module"""
import os
import sys
import configparser
import pytest
from tp_timesheet.config import Config

tests_path = os.path.dirname(os.path.abspath(__file__))
src_path = tests_path + "/../"
sys.path.insert(0, src_path)


@pytest.fixture(name="tmp_config")
def fixture_create_tmp_config():
    """
    Creates a tmp config file prior to running a test that uses this fixture.
    It then cleans up the tmp file after the test has run
    """
    # Fake config loaded by pytest
    test_config_path = Config.CONFIG_DIR.joinpath("tmp_pytest.conf")
    config_str = """
[configuration]
tp_email = fake@email.com
tp_url = https://example.com/path
    """
    with open(test_config_path, "w", encoding="utf8") as conf_file:
        conf_file.write(config_str)
    yield test_config_path
    os.remove(test_config_path)


def test_config_upgrade_process(tmp_config):
    """
    test the config from <=0.3.0 (email and url only),
    upgrades succesfully to include new parameters
    """
    new_parameters = Config.DEFAULT_CONF

    def read_config_as_text(path):
        with open(path, "r", encoding="utf8") as config_f:
            return config_f.readlines()

    def read_config_as_dict(path):
        input_config = configparser.ConfigParser()
        input_config.read(path)
        return input_config

    # Check config file exists already (created by fixture)
    assert os.path.exists(tmp_config)

    # Assert no config parameters exist in config prior to upgrade
    config_text = read_config_as_text(tmp_config)
    for line in config_text:
        for parameter in new_parameters:
            assert parameter not in line

    # Test config file reads correctly and only <=0.3.0 parameters exist
    config_dict = read_config_as_dict(tmp_config)
    assert config_dict.sections() == ["configuration"]
    assert list(config_dict["configuration"]) == ["tp_email", "tp_url"]

    # Initialize config which performs the upgrade
    Config(config_filename=tmp_config)

    # Test config file reads correctly and contains all the new parameters
    config_dict = read_config_as_dict(tmp_config)
    assert config_dict.sections() == ["configuration"]
    assert list(config_dict["configuration"]) == ["tp_email", "tp_url"] + list(
        new_parameters.keys()
    )
    for key, item in new_parameters.items():
        assert config_dict.get("configuration", key) == item