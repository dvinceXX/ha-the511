"""Ontario 511 provider.

Data source: https://511on.ca/developers/doc — Ontario requires a free
developer API key. The shared Travel-IQ client sends it as the ``key``
query parameter. Cameras and events use the same "GET" REST shape as the other
Travel-IQ provinces; road conditions are published under the
``roadconditions`` resource with the status in a ``Condition`` list.
Weather stations and travel times are not published.
"""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY

from .travel_iq import TravelIQProvider


class OntarioProvider(TravelIQProvider):
    """Provider for the Ontario 511 system (511on.ca)."""

    provider_id = "ontario"
    name = "Ontario"
    region = "Ontario"
    base_url = "https://511on.ca"

    required_config_keys = (CONF_API_KEY,)
    secret_config_keys = (CONF_API_KEY,)

    road_conditions_resource = "roadconditions"
    road_conditions_status_field = "Condition"

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
