from unittest.mock import patch

import pytest

from src.config import APP_CONFIG
from src.services import LinkedInLogin

linkedin_login = LinkedInLogin(config={**APP_CONFIG, "CLIENT_ID": "some_client_id"})


def test_get_auth_url():
    assert (
        linkedin_login.get_auth_url(redirect_uri=["some_redirect_uri"])
        == "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=some_client_id&redirect_uri=some_redirect_uri&scope=r_liteprofile%20r_emailaddress"
    )


@pytest.mark.xfail
def test_authenticate():
    with patch("src.services.requests.post"), patch("src.services.requests.get"), patch(
        "src.services.UserService.create_if_not_exists"
    ):
        linkedin_login.authenticate(
            code="some_code", redirect_uri="some_redirect_uri", user_type="buyer"
        )
