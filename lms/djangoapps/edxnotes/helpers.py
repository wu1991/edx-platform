"""
Helper methods related to EdxNotes.
"""
import json
import requests
import logging
from uuid import uuid4
from json import JSONEncoder
from datetime import datetime
from courseware.access import has_access
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _

from student.models import anonymous_id_for_user
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from util.date_utils import get_default_time_display
from dateutil.parser import parse as dateutil_parse
from provider.oauth2.models import AccessToken, Client
import oauth2_provider.oidc as oidc
from provider.utils import now
from .exceptions import EdxNotesParseError

log = logging.getLogger(__name__)


class NoteJSONEncoder(JSONEncoder):
    """
    Custom JSON encoder that encode datetime objects to appropriate time strings.
    """
    # pylint: disable=method-hidden
    def default(self, obj):
        if isinstance(obj, datetime):
            return get_default_time_display(obj)
        return json.JSONEncoder.default(self, obj)


def get_id_token(user):
    """
    Generates JWT ID-Token, using or creating user's OAuth access token.
    """
    try:
        client = Client.objects.get(name="edx-notes")
    except Client.DoesNotExist:
        raise ImproperlyConfigured("OAuth2 Client with name 'edx-notes' is not present in the DB")
    try:
        access_token = AccessToken.objects.get(
            client=client,
            user=user,
            expires__gt=now()
        )
    except AccessToken.DoesNotExist:
        access_token = AccessToken(client=client, user=user)
        access_token.save()

    id_token = oidc.id_token(access_token)
    secret = id_token.access_token.client.client_secret
    return id_token.encode(secret)


def get_token_url(course_id):
    """
    Returns token url for the course.
    """
    return reverse("get_token", kwargs={
        "course_id": course_id.to_deprecated_string(),
    })


def send_request(user, course_id, path="", query_string=""):
    """
    Sends a request with appropriate parameters and headers.
    """
    url = get_endpoint(path)
    params = {
        "user": anonymous_id_for_user(user, None),
        "course_id": unicode(course_id).encode("utf-8"),
    }

    if query_string:
        params.update({
            "text": query_string,
        })

    response = requests.get(
        url,
        headers={
            "x-annotator-auth-token": get_id_token(user)
        },
        params=params
    )

    return response


def preprocess_collection(user, course, collection):
    """
    Reprocess provided `collection(list)`: adds information about ancestor,
    converts "updated" date, sorts the collection in descending order.

    Raises:
        ItemNotFoundError - when appropriate module is not found.
    """
    store = modulestore()
    filtered_collection = list()
    with store.bulk_operations(course.id):
        for model in collection:
            usage_key = course.id.make_usage_key_from_deprecated_string(model["usage_id"])
            try:
                item = store.get_item(usage_key)
            except ItemNotFoundError:
                log.warning("Module not found: %s", usage_key)
                continue

            if not has_access(user, "load", item, course_key=course.id):
                continue

            model.update({
                u"unit": get_ancestor_context(course, store, usage_key),
                u"updated": dateutil_parse(model["updated"]),
            })
            filtered_collection.append(model)

    return filtered_collection


def search(user, course, query_string):
    """
    Returns search results for the `query_string(str)`.
    """
    response = send_request(user, course.id, "search", query_string)

    try:
        content = json.loads(response.content)
        collection = content["rows"]
    except (ValueError, KeyError):
        log.warning("invalid JSON: %s", response.content)
        raise EdxNotesParseError(_("Server error. Try again in a few minutes."))

    content.update({
        "rows": preprocess_collection(user, course, collection)
    })

    return json.dumps(content, cls=NoteJSONEncoder)


def get_notes(user, course):
    """
    Returns all notes for the user.
    """
    response = send_request(user, course.id, "annotations")

    try:
        collection = json.loads(response.content)
    except ValueError:
        return None

    if not collection:
        return None

    return json.dumps(preprocess_collection(user, course, collection), cls=NoteJSONEncoder)


def get_ancestor(store, usage_key):
    """
    Returns ancestor module for the passed `usage_key`.
    """
    location = store.get_parent_location(usage_key)
    if not location:
        log.warning("Parent location for the module not found: %s", usage_key)
        return
    try:
        return store.get_item(location)
    except ItemNotFoundError:
        log.warning("Parent module not found: %s", location)
        return


def get_ancestor_context(course, store, usage_key):
    """
    Returns dispay_name and url for the parent module.
    """
    parent = get_ancestor(store, usage_key)

    if not parent:
        return {
            u"display_name": None,
            u"url": None,
        }

    url = reverse("jump_to", kwargs={
        "course_id": course.id.to_deprecated_string(),
        "location": parent.location.to_deprecated_string(),
    })

    return {
        u"display_name": parent.display_name_with_default,
        u"url": url,
    }


def get_endpoint(path=""):
    """
    Returns endpoint.
    """
    try:
        url = settings.EDXNOTES_INTERFACE['url']
        if not url.endswith("/"):
            url += "/"

        if path:
            if path.startswith("/"):
                path = path.lstrip("/")
            if not path.endswith("/"):
                path += "/"

        return url + path
    except (AttributeError, KeyError):
        raise ImproperlyConfigured(_("No endpoint was provided for EdxNotes."))


def generate_uid():
    """
    Generates unique id.
    """
    return uuid4().int  # pylint: disable=no-member


def is_feature_enabled(course):
    """
    Returns True if the edxnotes app is enabled for the course, False otherwise.

    In order for the app to be enabled it must be:
        1) enabled globally via FEATURES.
        2) present in the course tab configuration.
    """
    tab_found = next((True for t in course.tabs if t["type"] == "edxnotes"), False)
    feature_enabled = settings.FEATURES.get("ENABLE_EDXNOTES")

    return feature_enabled and tab_found
