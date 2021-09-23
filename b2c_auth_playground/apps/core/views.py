from dataclasses import asdict

from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from b2c_auth_playground.apps.core.services.microsoft_b2c import build_auth_code_flow
from b2c_auth_playground.apps.core.services.microsoft_b2c import build_logout_uri
from b2c_auth_playground.settings import B2C_AUTHORITY_PROFILE_EDITING
from b2c_auth_playground.settings import B2C_AUTHORITY_SIGN_UP_SIGN_IN
from b2c_auth_playground.settings import B2C_SCOPES


def index(request):
    logged_user = request.session.get("user")
    context = {}

    if logged_user:
        redirect_uri = _build_redirect_uri(request)
        auth_flow_edit = build_auth_code_flow(authority=B2C_AUTHORITY_PROFILE_EDITING, redirect_uri=redirect_uri)
        request.session["flow-edit"] = asdict(auth_flow_edit)
        context["auth_flow_edit_uri"] = auth_flow_edit.auth_uri

    return render(request, "core/pages/home.html", context)


def logout(request):
    request.session.flush()
    index_request_path = reverse("index")
    redirect_uri = request.build_absolute_uri(index_request_path)
    redirect_uri = redirect_uri.replace("http", "https") if "localhost" not in redirect_uri else redirect_uri
    final_address = build_logout_uri(redirect_uri)
    return redirect(final_address)


def initiate_login_flow(request):
    redirect_uri = _build_redirect_uri(request)
    auth_flow_details = build_auth_code_flow(
        authority=B2C_AUTHORITY_SIGN_UP_SIGN_IN, scopes=B2C_SCOPES, redirect_uri=redirect_uri
    )
    # So we can retrieve it later
    request.session["flow"] = asdict(auth_flow_details)
    # Then we redirect the user
    return redirect(auth_flow_details.auth_uri)


def _build_redirect_uri(request):
    location_redirect = reverse("v1/response-oidc")
    redirect_uri = request.build_absolute_uri(location_redirect)
    return redirect_uri.replace("http", "https") if "localhost" not in redirect_uri else redirect_uri
