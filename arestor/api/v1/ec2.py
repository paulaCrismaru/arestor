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

"""Arestor API endpoint for EC2 Mocked Metadata."""
import json
import base64
import cherrypy

from oslo_log import log as logging

from arestor.api import base as base_api
from arestor.common import exception
from arestor.common import util as arestor_util


LOG = logging.getLogger(__name__)


class _EC2Resource(base_api.Resource):
    """Base class for EC2 resources."""

    exposed = True

    def _get_ec2_data(self, name, field=None):
        """Retrieve the required resource from the EC2 namespace."""
        data = None
        try:
            data = self._get_data(namespace="ec2",
                                  name=name, field=field)

            if field == "data":
                data = json.loads(arestor_util.get_as_string(data))
        except (exception.NotFound, ValueError):
            pass
        return data

    def _set_ec2_data(self, name, field=None, value=None):
        """Set the required resource from the EC2 namespace."""
        data = None
        try:
            data = self._set_data(namespace="ec2",
                                  name=name, field=field, value=value)
        except (ValueError, TypeError):
            pass
        return data


class _PublicKeysResource(_EC2Resource):

    @cherrypy.popargs('key')
    @cherrypy.popargs('index')
    def GET(self, index=None, key=None):
        public_keys = self._get_ec2_data("public_keys", "data")
        if index is None and key is None:
            return ["{index}=public_key".format(index=i)
                    for i in range(len(public_keys))]
        elif index is not None and key is None:
            return "openssh-key"
        else:
            return public_keys[int(index)]


class _HostnameResource(_EC2Resource):

    def GET(self):
        return self._get_ec2_data("hostname", "data")


class _InstanceIdResource(_EC2Resource):

    def GET(self):
        return self._get_ec2_data("uuid", "data")


class _MetadataResource(base_api.BaseAPI):
    """Metadata resource for EC2 Endpoint."""

    resources = [
        ("public-keys", _PublicKeysResource),
        ("local_hostname", _HostnameResource),
        ("instance-id", _InstanceIdResource)
    ]

    def __getattr__(self, name):
        """Handle for invalid resource name or alias."""

        # NOTE(mmicu): Add this method in base

        # Note(mmicu): The cherrypy MethodDispatcher will replace the
        # `-` from the resource / endpoint name with `_`. In order to avoid
        # any problems we will try to avoid this scenario.
        if "_" in name:
            return self.__dict__.get(name.replace("_", "-"))

        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, name))


class _UserdataResource(_EC2Resource):
    """Userdata resource for EC2 Endpoint."""

    def GET(self):
        """The representation of userdata resource."""
        userdata = self._get_ec2_data("user_data", "data")
        if userdata:
            return base64.b64decode(userdata)
        return ""


class EC2Endpoint(base_api.BaseAPI):
    exposed = True
    resources = [
        ('meta_data', _MetadataResource),
        ('user_data', _UserdataResource)
    ]


class EC2EndpointNamespace(base_api.BaseAPI):

    """The API Namespace for EC2."""
    resources = [
        ("2009-04-04", EC2Endpoint)
    ]

    """A list that contains all the resources (endpoints) available for the
    current metadata service."""

    exposed = True
    """Whether this application should be available for clients."""

    def __getattr__(self, name):
        """Handle for invalid resource name or alias."""

        # NOTE(mmicu): Add this method in base

        # Note(mmicu): The cherrypy MethodDispatcher will replace the
        # `-` from the resource / endpoint name with `_`. In order to avoid
        # any problems we will try to avoid this scenario.
        if "_" in name:
            return self.__dict__.get(name.replace("_", "-"))

        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, name))
