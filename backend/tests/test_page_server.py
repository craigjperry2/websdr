import pytest
import logging
import requests

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)


@scenario("page_server.feature", "Serve page and assets")
def test_serve_page_and_assets():
    pass


@given("a client connects with a web browser to <url> using <method>")
def client(url, method, server):
    return requests.request(method, "http://127.0.0.1:8000" + url)


@when("the webserver is ready")
def the_webserver_is_ready(server):
    logging.info(f"Spawned server with pid {server.pid}")


@then("they receive an http response containing <content> with <code>")
def they_receive_an_http_response_containing_content_with_code(content, code, client):
    assert int(code) == client.status_code
    assert content in client.text
