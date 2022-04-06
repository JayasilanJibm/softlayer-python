"""
    SoftLayer.transports.soap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SOAP Style transport library

    :license: MIT, see LICENSE for more details.
"""
import logging
import re
from string import Template
from zeep import Client, Settings, Transport, xsd
from zeep.helpers import serialize_object
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin

import requests

from SoftLayer import consts
from SoftLayer import exceptions

from .transport import _format_object_mask
from .transport import _proxies_dict
from .transport import ComplexEncoder
from .transport import get_session
from .transport import SoftLayerListResult

from pprint import pprint as pp
class SoapTransport(object):
    """XML-RPC transport."""

    def __init__(self, endpoint_url=None, timeout=None, proxy=None, user_agent=None, verify=True):

        # Throw an error for py < 3.6 because of f-strings
        logging.getLogger('zeep').setLevel(logging.ERROR)
        logging.getLogger('zeep.transports').setLevel(logging.DEBUG)
        self.endpoint_url = (endpoint_url or consts.API_PUBLIC_ENDPOINT).rstrip('/')
        self.timeout = timeout or None
        self.proxy = proxy
        self.user_agent = user_agent or consts.USER_AGENT
        self.verify = verify
        self._client = None
        self.history = HistoryPlugin()

    def __call__(self, request):
        """Makes a SoftLayer API call against the SOAP endpoint.

        :param request request: Request object
        """

        zeep_settings = Settings(strict=False, xml_huge_tree=True)
        zeep_transport = Transport(cache=SqliteCache(timeout=86400))
        client = Client(f"{self.endpoint_url}/{request.service}?wsdl",
                        settings=zeep_settings, transport=zeep_transport, plugins=[self.history])

        # MUST define headers like this because otherwise the objectMask header doesn't work
        # because it isn't sent in with a namespace.
        xsdUserAuth = xsd.Element(
            '{http://api.softlayer.com/soap/v3/}authenticate',
            xsd.ComplexType([
                xsd.Element('{http://api.service.softlayer.com/soap/v3/}username', xsd.String()),
                xsd.Element('{http://api.service.softlayer.com/soap/v3/}apiKey', xsd.String())
            ])
        )
        xsdMask = xsd.Element(
            '{http://api.service.softlayer.com/soap/v3.1/}SoftLayer_ObjectMask',
            xsd.ComplexType([
                xsd.Element('mask', xsd.String()),
            ])
        )

        headers = [
            xsdMask(mask=request.mask or ''),
            xsdUserAuth(username=request.transport_user, apiKey=request.transport_password)
        ]

        pp(headers)
        print("HEADERS ^^^^^")
        method = getattr(client.service, request.method)
        result = client.service.getObject(_soapheaders=headers)
        return serialize_object(result)
        # result = transport.post(f"{self.endpoint_url}/{request.service}")


    def print_reproduceable(self, request):
        """Prints out the minimal python code to reproduce a specific request

        The will also automatically replace the API key so its not accidently exposed.

        :param request request: Request object
        """
        
        return self.history.last_sent
