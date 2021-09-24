import logging

import msal

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from b2c_auth_playground.apps.core.api.api_exception import B2CContractNotRespectedException
from b2c_auth_playground.apps.core.api.api_exception import ServiceUnavailable
from b2c_auth_playground.apps.core.services.microsoft_b2c import obtain_access_token
from b2c_auth_playground.apps.core.services.microsoft_b2c import verify_flow
from b2c_auth_playground.settings import B2C_AUTHORITY_SIGN_UP_SIGN_IN
from b2c_auth_playground.settings import B2C_SCOPES

logger = logging.getLogger(__name__)


@api_view(["GET"])
def handle_response_oidc(request: Request) -> Response:
    current_referer = request.headers.get("referer")
    logger.info("It came from %s", current_referer)

    code_from_user_flow = request.query_params.get("code")
    auth_flow_details = request.session.pop("flow", {})
    auth_flow_details = auth_flow_details if auth_flow_details else request.session.pop("flow-edit", {})
    if not code_from_user_flow or not auth_flow_details:
        # I got this error after cancelling my PROFILE EDIT flow: error=access_denied&error_description=AADB2C90091: The user has cancelled entering self-asserted information.
        raise B2CContractNotRespectedException

    logger.debug("Trying to finish the flow")
    cache = _load_cache(request)
    acquire_token_details = verify_flow(auth_flow_details, request.query_params, cache)
    if acquire_token_details.error:
        logger.error(
            "We got %s! Its description: %s",
            acquire_token_details.error,
            acquire_token_details.error_description,
        )
        raise ServiceUnavailable
    else:
        _save_cache(request, cache)
        # I could set a cookie with HttpOnly right here for instance
        request.session["user"] = acquire_token_details.id_token_claims
        location_index = reverse("index")
        return redirect(location_index)


@api_view(["GET"])
def consult_user_data(request):
    cache = _load_cache(request)
    hard_coded_scopes = B2C_SCOPES
    result = obtain_access_token(hard_coded_scopes, cache, B2C_AUTHORITY_SIGN_UP_SIGN_IN)
    _save_cache(request, cache)

    try:
        access_token = result.get("access_token")
        if not access_token:
            logger.warning(
                "Authentication gives you an id token only. Authorisation to a resource gives you access tokens"
            )
    except AttributeError:
        result = {"error": "did you use ROPC?!"}

    return Response(data=result)


@api_view(["GET"])
def what_do_i_have(request):
    id_token_claims = request.session["user"]
    return Response(data=id_token_claims)


def _load_cache(request):
    cache = msal.SerializableTokenCache()
    token_cache = request.session.get("token_cache")
    if token_cache:
        cache.deserialize(token_cache)
    return cache


def _save_cache(request, cache):
    if cache.has_state_changed:
        request.session["token_cache"] = cache.serialize()
        # Sample value of what is returned from `cache.serialize()`:
        # {
        #     "Account": {
        #         "21548d8f-47b3-4585-83ad-9aa4cd487ae1-b2c_1_sign-in-sign-up.03f16fb5-12d8-4a0b-a65e-d325ea25ed2a-xptoorg.b2clogin.com-xptoorg.onmicrosoft.com": {
        #             "home_account_id": "21548d8f-47b3-4585-83ad-9aa4cd487ae1-b2c_1_sign-in-sign-up.03f16fb5-12d8-4a0b-a65e-d325ea25ed2a",
        #             "environment": "xptoorg.b2clogin.com",
        #             "realm": "xptoorg.onmicrosoft.com",
        #             "local_account_id": "21548d8f-47b3-4585-83ad-9aa4cd487ae1",
        #             "username": "",
        #             "authority_type": "MSSTS",
        #         }
        #     },
        #     "IdToken": {
        #         "21548d8f-47b3-4585-83ad-9aa4cd487ae1-b2c_1_sign-in-sign-up.03f16fb5-12d8-4a0b-a65e-d325ea25ed2a-xptoorg.b2clogin.com-idtoken-c05d9c78-baab-4ee3-8ea7-b1a4b8074309-xptoorg.onmicrosoft.com-": {
        #             "credential_type": "IdToken",
        #             "secret": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ilg1ZVhrNHh5b2pORnVtMWtsMll0djhkbE5QNC1jNTdkTzZRR1RWQndhTmsifQ.eyJleHAiOjE2MzI0MTg5NTAsIm5iZiI6MTYzMjQxNTM1MCwidmVyIjoiMS4wIiwiaXNzIjoiaHR0cHM6Ly94cHRvb3JnLmIyY2xvZ2luLmNvbS8wM2YxNmZiNS0xMmQ4LTRhMGItYTY1ZS1kMzI1ZWEyNWVkMmEvdjIuMC8iLCJzdWIiOiIyMTU0OGQ4Zi00N2IzLTQ1ODUtODNhZC05YWE0Y2Q0ODdhZTEiLCJhdWQiOiJjMDVkOWM3OC1iYWFiLTRlZTMtOGVhNy1iMWE0YjgwNzQzMDkiLCJub25jZSI6IjVkZDQyZDU4MGM4YWQ3OTZkNWZiNmZlMGU2ZWVhY2I0M2EzNDI0MTQ3MzQxZWUxOGNkMTEwYTdiMDQ1Yzc3ODgiLCJpYXQiOjE2MzI0MTUzNTAsImF1dGhfdGltZSI6MTYzMjQxNTMzNywib2lkIjoiMjE1NDhkOGYtNDdiMy00NTg1LTgzYWQtOWFhNGNkNDg3YWUxIiwiZ2l2ZW5fbmFtZSI6IkdyZWdvcmlvIiwiZmFtaWx5X25hbWUiOiJBbG1laWRhIiwibmFtZSI6Ik5vdCB1bmtub3duIGFueW1vcmUiLCJjaXR5IjoiU8OjbyBQYXVsbyIsImNvdW50cnkiOiJCcmF6aWwiLCJ0ZnAiOiJCMkNfMV9zaWduLWluLXNpZ24tdXAifQ.UnHowU1OVNQqGIT4E5iSlNtx4JQN6kUX64cSF_348LH8g0mn9eFTqyckZX9hyA9bFRmtcq-y3Wxt-Gw8y8FyU8l42aNzXQ3RPBpOLP8zNxk_WBJAvch22Q23X6NriKDwOcsM3fE3dmvG1InWR1G4PL5SM-2nlVtr-X9hz4dCWTIgKBwuMmeBBKrSR_WSGwg7nndu08HtdIqUWDrxSQ21bCzULm_LDJCizfLPFAj83lr97hwLUlHyOX09pLdgo8Nvjl0ko05NG9klxmNv5nfIcfG_O0cOvxz32Mt1sQDdpzWq36OOWMBRqrBZG-tJQtoPmfQ_YHZtLv_uaFleeVreXQ",
        #             "home_account_id": "21548d8f-47b3-4585-83ad-9aa4cd487ae1-b2c_1_sign-in-sign-up.03f16fb5-12d8-4a0b-a65e-d325ea25ed2a",
        #             "environment": "xptoorg.b2clogin.com",
        #             "realm": "xptoorg.onmicrosoft.com",
        #             "client_id": "c05d9c78-baab-4ee3-8ea7-b1a4b8074309",
        #         }
        #     },
        #     "RefreshToken": {
        #         "21548d8f-47b3-4585-83ad-9aa4cd487ae1-b2c_1_sign-in-sign-up.03f16fb5-12d8-4a0b-a65e-d325ea25ed2a-xptoorg.b2clogin.com-refreshtoken-c05d9c78-baab-4ee3-8ea7-b1a4b8074309--": {
        #             "credential_type": "RefreshToken",
        #             "secret": "eyJraWQiOiJjcGltY29yZV8wOTI1MjAxNSIsInZlciI6IjEuMCIsInppcCI6IkRlZmxhdGUiLCJzZXIiOiIxLjAifQ..5B8on71EFR_5DJRZ.pFZnkpdk3DKVHlL7SPZP5DLqwjh2hm-tQWiIPRExjLMaHZ9zBRa80sUe7yA2BPpX9-wFcaE7rdUHUsFXfFQ_WGON3cLNETthgdbxIbfwrigyJnhpYm-x9mhppo4jgjz7h4nR16t2pJ4qR9P6X3VZeWDEe3j-61cV75O8ux6HA5leArX6Kld7RF7SiHs-MMgKxl0ybA0K4mpOIJpT_vc2mN2BspPEmvqSgTAb1fn1bTDtS2WHBqoxmOVHqFgYrPnEqVJkArBZupXZ2D2pLJB9rtMVddNbcUJqwHFF5CpXxW3Ovz6qhovBk1GR-eF19eEIXwOQo-4KhojBDwMjaF87nR1XPoaqTtz8kO2OZpaM9BNwZ1Vg2xA3ErLJaTg3RXPS9om3THgUbjrxm2QrrgjFnHCLxqnC9-5uTYaE_lgeNy3zNd92EPQ_Pw5e3edYUynQqEL28Vs0eJ3xvcwRZhlvPmnYlZfzwT5KKcJUH7jtC3RNYRNHsRC4HTxv1qSFXE5RbpRkGHWdGpBPg5ZlGCWqxqTsf-WwEA8aq7HTWfj6uEzlXt5DqFO1xDzXpw-OYratzDZ4DlTe9oEUGgBjvs3jnVk8iBkxobqW3yYe4yjPECTx2uPEutmbaddlNtKotibZjmHXpJXgAPcpE1M56HOws1D5r3dNSWIAKaeQVrtcSfq14nKpmYLvQh0KReDL-CAnkb775A23-mjEk2E2gyt4Ls2CVE-9nh9DcaclhyJ_-sXH4uhH.U2Evy4dzcw0Pd5IpxpVSWQ",
        #             "home_account_id": "21548d8f-47b3-4585-83ad-9aa4cd487ae1-b2c_1_sign-in-sign-up.03f16fb5-12d8-4a0b-a65e-d325ea25ed2a",
        #             "environment": "xptoorg.b2clogin.com",
        #             "client_id": "c05d9c78-baab-4ee3-8ea7-b1a4b8074309",
        #             "target": "",
        #             "last_modification_time": "1632415350",
        #         }
        #     },
        #     "AppMetadata": {
        #         "appmetadata-xptoorg.b2clogin.com-c05d9c78-baab-4ee3-8ea7-b1a4b8074309": {
        #             "client_id": "c05d9c78-baab-4ee3-8ea7-b1a4b8074309",
        #             "environment": "xptoorg.b2clogin.com",
        #         }
        #     },
        # }
