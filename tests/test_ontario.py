"""Tests for the Ontario 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.ontario import OntarioProvider


API_KEY = "test-ontario-api-key"
API_PARAMS = {"format": "json", "key": API_KEY}


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{OntarioProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build an OntarioProvider bound to the mocked aiohttp session."""
    return OntarioProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_ontario_provider_registered():
    """Ontario should be registered under its provider_id."""
    assert get_provider_class("ontario") is OntarioProvider


def test_ontario_capabilities():
    """Ontario supports cameras, incidents, and road conditions."""
    provider = OntarioProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times


def test_ontario_requires_secret_api_key():
    """Ontario requires the developer key and treats it as a secret."""
    provider = OntarioProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert CONF_API_KEY in OntarioProvider.required_config_keys
    assert CONF_API_KEY in OntarioProvider.secret_config_keys
    assert provider._api_key == API_KEY


async def test_update_fetches_all_supported_resources_with_key(hass, aioclient_mock):
    """async_update should send the developer key for every resource."""
    aioclient_mock.get(_url("cameras"), params=API_PARAMS, json=[])
    aioclient_mock.get(_url("event"), params=API_PARAMS, json=[])
    aioclient_mock.get(
        _url("roadconditions", version=3), params=API_PARAMS, json=[]
    )

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 3


async def test_road_conditions_use_condition_list(hass, aioclient_mock):
    """Ontario reports the surface as a Condition list under roadconditions."""
    aioclient_mock.get(
        _url("roadconditions", version=3),
        params=API_PARAMS,
        json=[
            {
                "RoadwayName": "ON-401",
                "Condition": ["No Report"],
                "LocationDescription": "between Windsor and Toronto",
            }
        ],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert len(conditions) == 1
    assert conditions[0].road == "ON-401"
    assert conditions[0].surface == "No Report"


async def test_road_conditions_join_multi_condition_list(hass, aioclient_mock):
    """A multi-entry Condition list should be joined for display."""
    aioclient_mock.get(
        _url("roadconditions", version=3),
        params=API_PARAMS,
        json=[{"RoadwayName": "ON-401", "Condition": ["Bare Dry", "Loose Snow"]}],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert conditions[0].surface == "Bare Dry, Loose Snow"
