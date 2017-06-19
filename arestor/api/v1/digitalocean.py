# Copyright 2017 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Arestor API endpoint for DigitalOcean Mocked Metadata."""
import json
import base64
import cherrypy

from oslo_log import log as logging

from arestor.api import base as base_api
from arestor.common import exception


LOG = logging.getLogger(__name__)


class _DigitalOceanResource(base_api.Resource):
    """Base class for DigitalOcean resources."""

    exposed = True

    def _get_digitalocean_data(self, name, field=None):
        """Retrieve the required resource from the DigitalOcean namespace"""
        data = None
        try:
            data = self._get_data(namespace="digitalocean",
                                  name=name, field=field)
            if field == "data":
                data = json.loads(data)
        except (exception.NotFound, ValueError):
            pass
        return data

    def _set_digitalocean_data(self, name, field=None, value=None):
        """Set the required resource from the DigitalOcean namespace."""
        data = None
        try:
            data = self._set_data(namespace="digitalocean",
                                  name=name, field=field, value=value)
        except (ValueError, TypeError):
            pass
        return data


class _DropletIdResource(_DigitalOceanResource):

    def GET(self):
        """The representation of the droplet_id resource."""
        dropplet_id = self._get_digitalocean_data("uuid", "data")
        return dropplet_id


class _HostnameResource(_DigitalOceanResource):

    def GET(self):
        """The representation of the hostname resource."""
        hostname = self._get_digitalocean_data("hostname", "data")
        return hostname


class _UserDataResource(_DigitalOceanResource):

    def GET(self):
        userdata = self._get_digitalocean_data("user_data", "data")
        if userdata:
            return base64.b64decode(userdata)
        return ""


class _VendorDataResource(_DigitalOceanResource):

    def GET(self):
        vendor_data = self._get_digitalocean_data("vendor_data", "data")
        return vendor_data


class _PublicKeysResource(_DigitalOceanResource):

    def GET(self):
        """The representation of the droplet_id resource."""
        return self._get_digitalocean_data("public_keys", "data")


class _RegionResource(_DigitalOceanResource):

    def GET(self):
        return self._get_digitalocean_data("region", "data")


class _DigitalOceanV1(base_api.BaseAPI):

    """Container for all the resources from version 1 of the API."""
    exposed = True
    resources = [
        ("id", _DropletIdResource),
        ("hostname", _HostnameResource),
        ("user_data", _UserDataResource),
        ("vendor_data", _VendorDataResource),
        ("public_keys", _PublicKeysResource),
        ("region", _RegionResource)
    ]


class _DigitalOceanV1Json(_DigitalOceanResource):

    @cherrypy.tools.json_out()
    def GET(self):
        metadata = {
            "id": self._get_digitalocean_data("uuid", "data"),
            "hostname": self._get_digitalocean_data("hostname", "data"),
            "user_data": self._get_digitalocean_data("user_data", "data"),
            "vendor_data": self._get_digitalocean_data("vendor_data", "data"),
            "public_keys": self._get_digitalocean_data("public_keys", "data"),
            "region": self._get_digitalocean_data("region", "data")
        }
        return metadata


class _Metadata(base_api.BaseAPI):

    exposed = True
    resources = [
        ("v1", _DigitalOceanV1),
        ("v1_json", _DigitalOceanV1Json),
    ]


class DigitalOceanEndpoint(base_api.BaseAPI):

    """Arestor API endpoint for DigitalOcean Mocked Metadata."""

    resources = [
        ("metadata", _Metadata),
    ]
    """A list that contains all the resources (endpoints) available for the
    current metadata service."""

    exposed = True
    """Whether this application should be available for clients."""

    def __getattr__(self, name):
        """Handle for invalid resource name or alias."""

        # Note(alexcoman): The cherrypy MethodDispatcher will replace the
        # `-` from the resource / endpoint name with `_`. In order to avoid
        # any problems we will try to avoid this scenario.
        if "_" in name:
            return self.__dict__.get(name.replace("_", "-"))

        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, name))
