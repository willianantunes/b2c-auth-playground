import logging

from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import msal

from django.http import QueryDict
from msal import ConfidentialClientApplication
from msal import SerializableTokenCache

from b2c_auth_playground.settings import B2C_AUTHORITY_SIGN_UP_SIGN_IN
from b2c_auth_playground.settings import B2C_YOUR_APP_CLIENT_APPLICATION_ID
from b2c_auth_playground.settings import B2C_YOUR_APP_CLIENT_CREDENTIAL

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthFlowDetails:
    state: str
    scope: List[str]
    auth_uri: str
    code_verifier: str
    nonce: str
    claims_challenge: str
    redirect_uri: Optional[str] = None


@dataclass(frozen=True)
class AcquireTokenDetails:
    id_token: str
    token_type: str
    not_before: int
    client_info: str
    scope: str
    refresh_token: str
    refresh_token_expires_in: int
    id_token_claims: Dict[str, Union[int, str, List[str]]]
    error: Optional[str] = None
    error_description: Optional[str] = None


def retrieve_client_app(cache: SerializableTokenCache = None, authority: str = None) -> ConfidentialClientApplication:
    return msal.ConfidentialClientApplication(
        B2C_YOUR_APP_CLIENT_APPLICATION_ID,
        authority=authority,
        client_credential=B2C_YOUR_APP_CLIENT_CREDENTIAL,
        token_cache=cache,
    )


def build_logout_uri(post_logout_redirect_uri: str = None):
    # https://xptoorg.b2clogin.com/xptoorg.onmicrosoft.com/v2.0/.well-known/openid-configuration?p=B2C_1_sign-in-sign-up
    # You can grab the link above if you click on "Run user flow"
    address = f"{B2C_AUTHORITY_SIGN_UP_SIGN_IN}/oauth2/v2.0/logout"

    if post_logout_redirect_uri:
        return f"{address}?post_logout_redirect_uri={post_logout_redirect_uri}"

    return address


def verify_flow(auth_flow_details: Dict, query_params: QueryDict) -> AcquireTokenDetails:
    authority = auth_flow_details["auth_uri"].split("/oauth2")[0]
    msal_app = retrieve_client_app(authority=authority)
    # This method may raise an exception like `"state missing from auth_code_flow" in ex.args` or `state mismatch: oprdHyGTJtIEhbLM vs FwGbuTpMeHsfXztv`
    # Thus it's interesting to wrap it with try/except for production ready apps
    result = msal_app.acquire_token_by_auth_code_flow(auth_flow_details, query_params)
    # {'error': 'access_denied', 'error_description': 'The user has denied access to the scope requested by the client application.'}
    # {'error': 'redirect_uri_mismatch', 'error_description': "AADB2C90006: The redirect URI '' provided in the request is not registered for the client id 'c05d9c78-baab-4ee3-8ea7-b1a4b8074309'.\r\nCorrelation ID: 2969296c-1fb2-47c1-85d0-288d88a94323\r\nTimestamp: 2021-09-19 17:11:23Z\r\n"}
    # {'error': 'invalid_client', 'error_description': 'AADB2C90081: The specified client_secret does not match the expected value for this client. Please correct the client_secret and try again.\r\nCorrelation ID: 24abcb7d-837d-4e06-b060-170904eac5c2\r\nTimestamp: 2021-09-19 20:06:38Z\r\n'}
    # {'error': 'invalid_grant', 'error_description': 'AADB2C90088: The provided grant has not been issued for this endpoint. Actual Value : B2C_1_sign-in-sign-up and Expected Value : B2C_1_profile_editing\r\nCorrelation ID: da82e598-f345-4f06-b47f-cc1ce3bc69a4\r\nTimestamp: 2021-09-19 22:51:31Z\r\n'}
    # {
    #     "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ilg1ZVhrNHh5b2pORnVtMWtsMll0djhkbE5QNC1jNTdkTzZRR1RWQndhTmsifQ.eyJleHAiOjE2MzIwODU5NDEsIm5iZiI6MTYzMjA4MjM0MSwidmVyIjoiMS4wIiwiaXNzIjoiaHR0cHM6Ly94cHRvb3JnLmIyY2xvZ2luLmNvbS8wM2YxNmZiNS0xMmQ4LTRhMGItYTY1ZS1kMzI1ZWEyNWVkMmEvdjIuMC8iLCJzdWIiOiIyMTU0OGQ4Zi00N2IzLTQ1ODUtODNhZC05YWE0Y2Q0ODdhZTEiLCJhdWQiOiJjMDVkOWM3OC1iYWFiLTRlZTMtOGVhNy1iMWE0YjgwNzQzMDkiLCJub25jZSI6IjUxYmZmYTg1NzAzNWFhMGRlZjY3NTQxYTZlZGQ0ZDg3Y2Y0MzU5ODEzZTVkZjM0YTRlMTI5NmQwODliZmU4MmYiLCJpYXQiOjE2MzIwODIzNDEsImF1dGhfdGltZSI6MTYzMjA4MjMyMywib2lkIjoiMjE1NDhkOGYtNDdiMy00NTg1LTgzYWQtOWFhNGNkNDg3YWUxIiwiZ2l2ZW5fbmFtZSI6IkdyZWdvcmlvIiwiZmFtaWx5X25hbWUiOiJBbG1laWRhIiwibmFtZSI6InVua25vd24iLCJlbWFpbHMiOlsid2lsbGlhbmxpbWFhbnR1bmVzQGdtYWlsLmNvbSJdLCJ0ZnAiOiJCMkNfMV9zaWduLWluLXNpZ24tdXAifQ.dTj55DQpG0VYef0FeVwuUlxHrYpMbBHaNCpKZu6dhu6zzxVZEf3fmWLItiDKBX5YZjgG7ufDjGRFiWA9jjYu0a0ctJ2fnK94ygxo9mwONWNUmAubDF2Gnidc9Iv0FpxbtKtEaYAHQuQcNpMDsiRJbvYpbPg9eFB0lQDgSa2RygNI3qKmPiqay1wPlvlz1bVwZZ1rtPpsTEPNbfIkSXZNZOv5x2YrbekQxUBgjneZLH4PqFpmG3mqSHsrFfWDlzgBhOCGu2kKaCLBDO7Z8Bn-ROpqt9xLgkYeMfmHILR8RikzcvHwZaFUj4E3WuZsq4vzk_vzlJGoqsuOcPbtcc5yOg",
    #     "token_type": "Bearer",
    #     "not_before": 1632082341,
    #     "client_info": "eyJ1aWQiOiIyMTU0OGQ4Zi00N2IzLTQ1ODUtODNhZC05YWE0Y2Q0ODdhZTEtYjJjXzFfc2lnbi1pbi1zaWduLXVwIiwidXRpZCI6IjAzZjE2ZmI1LTEyZDgtNGEwYi1hNjVlLWQzMjVlYTI1ZWQyYSJ9",
    #     "scope": "",
    #     "refresh_token": "eyJraWQiOiJjcGltY29yZV8wOTI1MjAxNSIsInZlciI6IjEuMCIsInppcCI6IkRlZmxhdGUiLCJzZXIiOiIxLjAifQ..ck1QuCFzfOR644Yz.1F8X91nltJu1oFLQ8kKGRoiaBwLvKncjvf_nnJG_PXzPciNIj-kbkKEyfiT3n_kHKak23PIC5N4cTsnwjw9IHtTdd83UsJ-5g5cXo2h6MPiZ_Tr7YIcuRN7QmggAKh04ahvvRm6HitNz6eUuHsfS8nmeZfXz-ulhpeTcstmIWnz61NywTmnheqSofTHODPHHAtqpT8z5WGESpUROMGN0APf7PuUYXkLKMuoQpsf_xI4TRYoz_WTHglsmCYe5kug5Um0aZijXTNOKyaJZjdH9DH6PU-aoIzag41NvuvoA-fi3bhX-okoumwApHAdhFTrh_98VwfVR8cWnCq_f_lCgrIxLlZs_A0peyV7xox_Uciw5LLfNdu_e-1IW6PLFLfIKIzs_TWSqcnmeBJ_aFmxEuujLgCm0TPd17csUh-1shSHLEFvlF_EtSnn65FxAgk80Os0CHHEp4QmlEZAnqJcesJfPrEyXLxzIRdQ9Xy4vFp54uVgcUJNZ2aJaAXTVDiypKJUj0z0oq8rVKRdQaYU2YUMnfnMvkylBHsdnAjPJnOks5UhFafHQfpJzLYmTIGh0YVy1hAGpp-qhcGRly0CtWmCNFBoH2NRREi2ZZCnwUlOYNvUKRuxRXpN2xAHHJbSMPeMAvxmYOGTszgNJgSRadFUIdt4Ud8w4xzn2RmSaCNue_oxeXfLYQr9sQVqy7RZZboIJoHI6WOFJl6eRc-oGpcg.BAJ_LChf-yMYjoa5CO3ngA",
    #     "refresh_token_expires_in": 1209600,
    #     "id_token_claims": {
    #         "exp": 1632085941, # "Expiration". The value of the exp attribute in the JWT claims set expresses the time of expiration in seconds, which is calculated from 1970-01-01T0:0:0Z as measured in Coordinated Universal Time (UTC)
    #         "nbf": 1632082341, # "Not Before".
    #         "ver": "1.0",
    #         "iss": "https://xptoorg.b2clogin.com/03f16fb5-12d8-4a0b-a65e-d325ea25ed2a/v2.0/", # This is the issuer!
    #         "sub": "21548d8f-47b3-4585-83ad-9aa4cd487ae1", # This is the subject (the party being asserted by the issuer). An identifier owned by the OpenID provider, which represents the end-user.
    #         "aud": "c05d9c78-baab-4ee3-8ea7-b1a4b8074309", # Audience. This is the same as B2C_YOUR_APP_CLIENT_APPLICATION_ID
    #         "nonce": "51bffa857035aa0def67541a6edd4d87cf4359813e5df34a4e1296d089bfe82f",
    #         "iat": 1632082341, #  The iat attribute in the JWT claims set expresses the time when the JWT was issued. The time difference between iat and exp in seconds isn’t the lifetime of the JWT when there’s an nbf (not before) attribute present in the claims set
    #         "auth_time": 1632082323,
    #         "oid": "21548d8f-47b3-4585-83ad-9aa4cd487ae1",
    #         "given_name": "Gregorio",
    #         "family_name": "Almeida",
    #         "name": "unknown",
    #         "emails": ["willianlimaantunes@gmail.com"],
    #         "tfp": "B2C_1_sign-in-sign-up",
    #     },
    # }
    acquire_token_details = AcquireTokenDetails(**result)
    logger.info("What is contained in id_token_claims: %s", acquire_token_details.id_token_claims)
    logger.info("You can change what is returned in `id_token_claims` if you go to USER FLOW / APPLICATION CLAIMS")
    return acquire_token_details


def build_auth_code_flow(authority: str = None, scopes: List[str] = None, redirect_uri: str = None) -> AuthFlowDetails:
    msal_app = retrieve_client_app(authority=authority)

    scopes = scopes if scopes else []
    value = msal_app.initiate_auth_code_flow(scopes, redirect_uri)
    # Sample `value` with authority "b2c_1_sign-in-sign-u":
    # {
    #     "state": "XHIlwMSuDtjVNTFk",
    #     "redirect_uri": "http://localhost:8000/api/v1/response-oidc",
    #     "scope": ["openid", "profile", "offline_access"],
    #     "auth_uri": "https://xptoorg.b2clogin.com/xptoorg.onmicrosoft.com/b2c_1_sign-in-sign-up/oauth2/v2.0/authorize?client_id=c05d9c78-baab-4ee3-8ea7-b1a4b8074309&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fv1%2Fresponse-oidc&scope=offline_access+openid+profile&state=XHIlwMSuDtjVNTFk&code_challenge=c6I2cwVD0h5qA0Hrjj4mTR6LgsmedOyLEt6IBEoy8Bk&code_challenge_method=S256&nonce=1b1322d4dd3eb0217d93a946faf447b025dec1b3bb2ce8e95af4a03f0529dfc5",
    #     "code_verifier": "wPq9sIvOEdz6DlhY_WS21g3GV-0BmHka8ojuU.Xy4b7",
    #     "nonce": "njZqlBVOfoDsFLWE",
    #     "claims_challenge": None,
    # }
    return AuthFlowDetails(**value)
