# Copyright (c) 2015 Cisco Systems
# Copyright (c) 2013-2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Marshal exception subclasses
"""

from six.moves.urllib.parse import urlparse

import marshal_agent.i18n as u

_FATAL_EXCEPTION_FORMAT_ERRORS = False


class RedirectException(Exception):
    def __init__(self, url):
        self.url = urlparse(url)


class MarshalException(Exception):
    """Base Marshal Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = u._("An unknown exception occurred")

    def __init__(self, message_arg=None, *args, **kwargs):
        if not message_arg:
            message_arg = self.message
        try:
            self.message = message_arg % kwargs
        except Exception as e:
            if _FATAL_EXCEPTION_FORMAT_ERRORS:
                raise e
            else:
                # at least get the core message out if something happened
                pass
        super(MarshalException, self).__init__(self.message)


class MarshalHTTPException(MarshalException):
    """Base Marshal Exception to handle HTTP responses

    To correctly use this class, inherit from it and define the following
    properties:

    - message: The message that will be displayed in the server log.
    - client_message: The message that will actually be outputted to the
                      client.
    - status_code: The HTTP status code that should be returned.
                   The default status code is 500.
    """
    client_message = u._("failure seen - please contact site administrator.")

    def __init__(self, message_arg=None, client_message=None, status_code=500,
                 *args, **kwargs):
        self.status_code = status_code
        if not client_message:
            client_message = self.client_message
        try:
            self.client_message = client_message % kwargs
        except Exception as e:
            if _FATAL_EXCEPTION_FORMAT_ERRORS:
                raise e
            else:
                # at least get the core message out if something happened
                pass
        super(MarshalHTTPException, self).__init__(
            message_arg, self.client_message, *args, **kwargs)


class MissingKMSConfigurationError(MarshalException):
    message = u._("One or more KMS configuration elements could not be found.")


class MissingArgumentError(MarshalException):
    message = u._("Missing required argument.")


class MissingCredentialError(MarshalException):
    message = u._("Missing required credential: %(required)s")


class MissingMetadataField(MarshalHTTPException):
    message = u._("Missing required metadata field for %(required)s")
    client_message = message
    status_code = 400


class InvalidSubjectDN(MarshalHTTPException):
    message = u._("Invalid subject DN: %(subject_dn)s")
    client_message = message
    status_code = 400


class InvalidContainer(MarshalHTTPException):
    message = u._("Invalid container: %(reason)s")
    client_message = message
    status_code = 400


class InvalidExtensionsData(MarshalHTTPException):
    message = u._("Invalid extensions data.")
    client_message = message
    status_code = 400


class InvalidCMCData(MarshalHTTPException):
    message = u._("Invalid CMC Data")
    client_message = message
    status_code = 400


class InvalidPKCS10Data(MarshalHTTPException):
    message = u._("Invalid PKCS10 Data: %(reason)s")
    client_message = message
    status_code = 400


class InvalidCertificateRequestType(MarshalHTTPException):
    message = u._("Invalid Certificate Request Type")
    client_message = message
    status_code = 400


class CertificateExtensionsNotSupported(MarshalHTTPException):
    message = u._("Extensions are not yet supported.  "
                  "Specify a valid profile instead.")
    client_message = message
    status_code = 400


class FullCMCNotSupported(MarshalHTTPException):
    message = u._("Full CMC Requests are not yet supported.")
    client_message = message
    status_code = 400


class BadAuthStrategy(MarshalException):
    message = u._("Incorrect auth strategy, expected \"%(expected)s\" but "
                  "received \"%(received)s\"")


class NotFound(MarshalException):
    message = u._("An object with the specified identifier was not found.")


class UnknownScheme(MarshalException):
    message = u._("Unknown scheme '%(scheme)s' found in URI")


class BadStoreUri(MarshalException):
    message = u._("The Store URI was malformed.")


class Duplicate(MarshalException):
    message = u._("An object with the same identifier already exists.")


class StorageFull(MarshalException):
    message = u._("There is not enough disk space on the image storage media.")


class StorageWriteDenied(MarshalException):
    message = u._("Permission to write image storage media denied.")


class AuthBadRequest(MarshalException):
    message = u._("Connect error/bad request to Auth service at URL %(url)s.")


class AuthUrlNotFound(MarshalException):
    message = u._("Auth service at URL %(url)s not found.")


class AuthorizationFailure(MarshalException):
    message = u._("Authorization failed.")


class NotAuthenticated(MarshalException):
    message = u._("You are not authenticated.")


class Forbidden(MarshalException):
    message = u._("You are not authorized to complete this action.")


class NotSupported(MarshalException):
    message = u._("Operation is not supported.")


class ForbiddenPublicImage(Forbidden):
    message = u._("You are not authorized to complete this action.")


class ProtectedImageDelete(Forbidden):
    message = u._("Image %(image_id)s is protected and cannot be deleted.")


# NOTE(bcwaldon): here for backwards-compatibility, need to deprecate.
class NotAuthorized(Forbidden):
    message = u._("You are not authorized to complete this action.")


class Invalid(MarshalException):
    message = u._("Data supplied was not valid.")


class NoDataToProcess(MarshalHTTPException):
    message = u._("No data supplied to process.")
    client_message = message
    status_code = 400


class InvalidSortKey(Invalid):
    message = u._("Sort key supplied was not valid.")


class InvalidFilterRangeValue(Invalid):
    message = u._("Unable to filter using the specified range.")


class ReadonlyProperty(Forbidden):
    message = u._("Attribute '%(property)s' is read-only.")


class ReservedProperty(Forbidden):
    message = u._("Attribute '%(property)s' is reserved.")


class AuthorizationRedirect(MarshalException):
    message = u._("Redirecting to %(uri)s for authorization.")


class DatabaseMigrationError(MarshalException):
    message = u._("There was an error migrating the database.")


class ClientConnectionError(MarshalException):
    message = u._("There was an error connecting to a server")


class ClientConfigurationError(MarshalException):
    message = u._("There was an error configuring the client.")


class MultipleChoices(MarshalException):
    message = u._("The request returned a 302 Multiple Choices. This "
                  "generally means that you have not included a version "
                  "indicator in a request URI.\n\nThe body of response "
                  "returned:\n%(body)s")


class LimitExceeded(MarshalHTTPException):
    message = u._("The request returned a 413 Request Entity Too Large. This "
                  "generally means that rate limiting or a quota threshold "
                  "was breached.\n\nThe response body:\n%(body)s")
    client_message = u._("Provided information too large to process")
    status_code = 413

    def __init__(self, *args, **kwargs):
        super(LimitExceeded, self).__init__(*args, **kwargs)
        self.retry_after = (int(kwargs['retry']) if kwargs.get('retry')
                            else None)


class ServiceUnavailable(MarshalException):
    message = u._("The request returned 503 Service Unavilable. This "
                  "generally occurs on service overload or other transient "
                  "outage.")

    def __init__(self, *args, **kwargs):
        super(ServiceUnavailable, self).__init__(*args, **kwargs)
        self.retry_after = (int(kwargs['retry']) if kwargs.get('retry')
                            else None)


class ServerError(MarshalException):
    message = u._("The request returned 500 Internal Server Error.")


class UnexpectedStatus(MarshalException):
    message = u._("The request returned an unexpected status: %(status)s."
                  "\n\nThe response body:\n%(body)s")


class InvalidContentType(MarshalException):
    message = u._("Invalid content type %(content_type)s")


class InvalidContentEncoding(MarshalException):
    message = u._("Invalid content encoding %(content_encoding)s")


class BadRegistryConnectionConfiguration(MarshalException):
    message = u._("Registry was not configured correctly on API server. "
                  "Reason: %(reason)s")


class BadStoreConfiguration(MarshalException):
    message = u._("Store %(store_name)s could not be configured correctly. "
                  "Reason: %(reason)s")


class BadDriverConfiguration(MarshalException):
    message = u._("Driver %(driver_name)s could not be configured correctly. "
                  "Reason: %(reason)s")


class StoreDeleteNotSupported(MarshalException):
    message = u._("Deleting images from this store is not supported.")


class StoreAddDisabled(MarshalException):
    message = u._("Configuration for store failed. Adding images to this "
                  "store is disabled.")


class InvalidNotifierStrategy(MarshalException):
    message = u._("'%(strategy)s' is not an available notifier strategy.")


class MaxRedirectsExceeded(MarshalException):
    message = u._("Maximum redirects (%(redirects)s) was exceeded.")


class InvalidRedirect(MarshalException):
    message = u._("Received invalid HTTP redirect.")


class NoServiceEndpoint(MarshalException):
    message = u._("Response from Keystone does not contain a "
                  "Marshal endpoint.")


class RegionAmbiguity(MarshalException):
    message = u._("Multiple 'image' service matches for region %(region)s. "
                  "This generally means that a region is required and you "
                  "have not supplied one.")


class WorkerCreationFailure(MarshalException):
    message = u._("Server worker creation failed: %(reason)s.")


class SchemaLoadError(MarshalException):
    message = u._("Unable to load schema: %(reason)s")


class InvalidObject(MarshalHTTPException):
    status_code = 400

    def __init__(self, *args, **kwargs):
        self.invalid_property = kwargs.get('property')
        self.message = u._("Failed to validate JSON information: ")
        self.client_message = u._("Provided object does not match "
                                  "schema '{schema}': "
                                  "{reason}").format(*args, **kwargs)
        self.message = self.message + self.client_message
        super(InvalidObject, self).__init__(*args, **kwargs)


class PayloadDecodingError(MarshalHTTPException):
    status_code = 400
    message = u._("Error while attempting to decode payload.")
    client_message = u._("Unable to decode request data.")


class UnsupportedField(MarshalHTTPException):
    message = u._("No support for value set on field '%(field)s' on "
                  "schema '%(schema)s': %(reason)s")
    client_message = u._("Provided field value is not supported")
    status_code = 400

    def __init__(self, *args, **kwargs):
        super(UnsupportedField, self).__init__(*args, **kwargs)
        self.invalid_field = kwargs.get('field')


class FeatureNotImplemented(MarshalException):
    message = u._("Feature not implemented for value set on field "
                  "'%(field)s' on " "schema '%(schema)s': %(reason)s")

    def __init__(self, *args, **kwargs):
        super(FeatureNotImplemented, self).__init__(*args, **kwargs)
        self.invalid_field = kwargs.get('field')


class UnsupportedHeaderFeature(MarshalException):
    message = u._("Provided header feature is unsupported: %(feature)s")


class InUseByStore(MarshalException):
    message = u._("The image cannot be deleted because it is in use through "
                  "the backend store outside of Marshal.")


class ImageSizeLimitExceeded(MarshalException):
    message = u._("The provided image is too large.")


class StoredKeyContainerNotFound(MarshalException):
    message = u._("Container %(container_id)s does not exist for stored "
                  "key certificate generation.")


class StoredKeyPrivateKeyNotFound(MarshalException):
    message = u._("Container %(container_id)s does not reference a private "
                  "key needed for stored key certificate generation.")


class InvalidUUIDInURI(MarshalHTTPException):
    message = u._("The provided UUID in the URI (%(uuid_string)s) is "
                  "malformed.")
    client_message = u._("The provided UUID in the URI is malformed.")
    status_code = 404


class InvalidCAID(MarshalHTTPException):
    message = u._("Invalid CA_ID: %(ca_id)s")
    client_message = u._("The ca_id provided in the request is invalid")
    status_code = 400


class CANotDefinedForProject(MarshalHTTPException):
    message = u._("CA specified by ca_id %(ca_id)s not defined for project: "
                  "%(project_id)s")
    client_message = u._("The ca_id provided in the request is not defined "
                         "for this project")
    status_code = 403
