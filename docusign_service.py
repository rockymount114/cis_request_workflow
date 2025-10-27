
import os
import jwt
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, CarbonCopy, SignHere, Tabs, Recipients
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def get_access_token():
    """Get access token using JWT Grant flow."""
    try:
        api_client = ApiClient()
        api_client.set_base_path(os.environ.get('DOCUSIGN_BASE_PATH'))
        private_key = os.path.join(dirname(__file__), "private.key") # Create a file named private.key with your DocuSign private key
        
        return api_client.request_jwt_user_token(
            client_id=os.environ.get('DOCUSIGN_INTEGRATOR_KEY'),
            user_id=os.environ.get('DOCUSIGN_USER_ID'),
            oauth_host_name=os.environ.get('DOCUSIGN_OAUTH_HOST', 'account-d.docusign.com'),
            private_key_bytes=private_key,
            expires_in=3600,
            scopes=["signature", "impersonation"]
        )
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def create_and_send_envelope(user_request, document_html):
    """
    Creates and sends an envelope with the user request data for signature.
    """
    access_token_response = get_access_token()
    if not access_token_response:
        return None

    access_token = access_token_response.access_token

    # Create a DocuSign client
    api_client = ApiClient()
    api_client.host = os.environ.get('DOCUSIGN_BASE_PATH')
    api_client.set_default_header("Authorization", "Bearer " + access_token)

    # Create an envelope definition
    envelope_definition = EnvelopeDefinition(
        email_subject="New User Request - Please Sign",
        documents=[
            Document(
                document_base64=document_html, # Base64 encoded HTML document
                name="User Request Form",
                file_extension="html",
                document_id="1"
            )
        ],
        status="sent"
    )

    # Add recipients
    signer1 = Signer(
        email=user_request.work_email, # For now, sending to the user who requested
        name=f"{user_request.first_name} {user_request.last_name}",
        recipient_id="1",
        routing_order="1",
        tabs=Tabs(sign_here_tabs=[SignHere(document_id='1', page_number='1', x_position='100', y_position='100')])
    )

    recipients = Recipients(signers=[signer1])
    envelope_definition.recipients = recipients

    # Send the envelope
    envelopes_api = EnvelopesApi(api_client)
    results = envelopes_api.create_envelope(os.environ.get('DOCUSIGN_API_ACCOUNT_ID'), envelope_definition=envelope_definition)

    return results.envelope_id
