import secrets
import base64
import hashlib
import string
from urllib.parse import urlencode

from django.http import JsonResponse
from .models import Integrations
from django.views import View
from django.shortcuts import redirect
from django.shortcuts import render


from YP.logger import logger


def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    return code_verifier, code_challenge


def generate_random_string(length=32):
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def login_page(request):
    return render(request, 'vk_api/vk_login.html')


def start_vk_login(request):
    code_verifier, code_challenge = generate_pkce_pair()
    state = generate_random_string(32)

    Integrations.objects.create(
        state=state,
        code_verifier=code_verifier,
        code_challenge=code_challenge,
    )
    logger.info(f"Создал объект модели Integrations."
                f"\nstate - {state}\ncode_verifier - {code_verifier}\ncode_challenge - {code_challenge}")

    # params = {
    #     'response_type': 'code',
    #     'client_id': '53476139',
    #     'code_challenge': code_challenge,
    #     'code_challenge_method': 'S256',
    #     'redirect_uri': "https://parsx.ru/accept_requests/",
    #     'state': state,
    #     'scope': 'market',
    # }
    url = f"https://id.vk.com/authorize?response_type=code&client_id=53476139&scope=market&redirect_uri=https%3A%2F%2Fparsx.ru%2Faccept_requests%2F&state={state}&code_challenge={code_challenge}&code_challenge_method=S256"
    return redirect(url)


class VkAcceptCodeView(View):
    def get(self, request):
        request_data = request.GET
        code = request_data.get("code")
        state = request_data.get("state")
        device_id = request_data.get("device_id")

        obj, created = Integrations.objects.update_or_create(
            state=state,
            defaults={
                'device_id': device_id,
                'authorization_code': code,
            }
        )
        logger.info(f'obj: {obj}\n created: {created}')

        # Обработка отсутствующих параметров
        if not code:
            return JsonResponse({"error": "Missing 'code' parameter"}, status=400)

        return JsonResponse({
            "message": "Integration saved successfully",
            # "integration_id": integration.id
        })


"https://id.vk.com/authorize?response_type=code&client_id=12345&scope=email%20phone&redirect_uri=https%3A%2F%2Fyour.site&state=XXXRandomZZZ&code_challenge=K8KAyQ82WSEncryptedVerifierGYUDj8K&code_challenge_method=S256"
"https://id.vk.com/authorize?client_id=53476139&redirect_uri=https%3A%2F%2Fparsx.ru%2Faccept_requests%2F&response_type=code&state=GSEh0_Wu0h9TF7bhNF65qbRVxSE89uoS&scope=market&code_challenge=Bnavf77XDKMn3hdSx7A_cD-VJu5aakU9MPlWwuJ9Qbs&code_challenge_method=S256"
