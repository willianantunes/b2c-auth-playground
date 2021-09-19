import logging

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from b2c_auth_playground.apps.core.api.api_exception import B2CContractNotRespectedException
from b2c_auth_playground.apps.core.api.api_exception import ServiceUnavailable
from b2c_auth_playground.apps.core.services.microsoft_b2c import verify_flow

logger = logging.getLogger(__name__)


@api_view(["GET"])
def handle_response_oidc(request: Request) -> Response:
    current_referer = request.headers.get("referer")
    logger.info("It came from %s", current_referer)

    code_from_user_flow = request.query_params.get("code")
    auth_flow_details = request.session.pop("flow", {})
    auth_flow_details = auth_flow_details if auth_flow_details else request.session.pop("flow-edit", {})
    if not code_from_user_flow or not auth_flow_details:
        raise B2CContractNotRespectedException

    logger.debug("Trying to finish the flow")
    acquire_token_details = verify_flow(auth_flow_details, request.query_params)
    if acquire_token_details.error:
        logger.error(
            "We got %s! Its description: %s",
            acquire_token_details.error,
            acquire_token_details.error_description,
        )
        raise ServiceUnavailable
    else:
        # I could set a cookie with HttpOnly right here for instance
        request.session["user"] = acquire_token_details.id_token_claims
        location_index = reverse("index")
        return redirect(location_index)
