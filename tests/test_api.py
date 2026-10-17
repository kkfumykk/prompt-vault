import io
from PIL import Image
import pytest
from fastapi.testclient import TestClient

from app.domain.services import TagParser
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def create_dummy_image_bytes():
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def test_public_settings(client):
    res = client.get("/api/settings/public")
    assert res.status_code == 200
    data = res.json()
    assert data["x_username"] == "amkki_aipix"
    assert "pixai_promo_enabled" in data


def test_x_auth_roles_and_protected_entry_lifecycle(client):
    img_bytes = create_dummy_image_bytes()
    prompt = "1girl, solo, masterpiece, cyberpunk city"

    # 1. 未認証での登録は 403 Forbidden
    unauth_res = client.post(
        "/api/entries",
        files={"file": ("test.png", img_bytes, "image/png")},
        data={"prompt": prompt},
    )
    assert unauth_res.status_code == 403

    # 2. 一般フォロワーとしてログイン
    follower_login = client.post(
        "/api/auth/x/login",
        json={"username": "general_fan", "following_confirmed": True},
    )
    assert follower_login.status_code == 200
    follower_data = follower_login.json()
    assert follower_data["is_admin"] is False
    assert follower_data["is_following"] is True
    follower_headers = {"Authorization": f"Bearer {follower_data['token']}"}

    # 一般フォロワーでは登録不可 (403)
    res_follower_try = client.post(
        "/api/entries",
        headers=follower_headers,
        files={"file": ("test.png", img_bytes, "image/png")},
        data={"prompt": prompt},
    )
    assert res_follower_try.status_code == 403

    # 3. @amkki_aipix はパスワードなしではログイン不可 (401)
    admin_no_pass = client.post(
        "/api/auth/x/login",
        json={"username": "@amkki_aipix", "following_confirmed": True},
    )
    assert admin_no_pass.status_code == 401

    # 4. 誤ったパスワードでもログイン不可 (401)
    admin_wrong_pass = client.post(
        "/api/auth/x/login",
        json={"username": "@amkki_aipix", "following_confirmed": True, "password": "wrong_password"},
    )
    assert admin_wrong_pass.status_code == 401

    # 5. 正しいパスワードで管理者としてログイン成功 (200)
    admin_login = client.post(
        "/api/auth/x/login",
        json={"username": "@amkki_aipix", "following_confirmed": True, "password": "admin"},
    )
    assert admin_login.status_code == 200
    admin_data = admin_login.json()
    assert admin_data["is_admin"] is True
    assert admin_data["username"] == "amkki_aipix"
    admin_headers = {"Authorization": f"Bearer {admin_data['token']}"}

    # 6. パスワード変更テスト
    change_res = client.post(
        "/api/auth/change-password",
        headers=admin_headers,
        json={"current_password": "admin", "new_password": "new_secure_pass123"}
    )
    assert change_res.status_code == 200

    # 元のパスワードに戻す
    client.post(
        "/api/auth/change-password",
        headers=admin_headers,
        json={"current_password": "new_secure_pass123", "new_password": "admin"}
    )

    # 7. @amkki_aipix のトークンで登録成功 (200)
    res_admin = client.post(
        "/api/entries",
        headers=admin_headers,
        files={"file": ("test.png", img_bytes, "image/png")},
        data={"prompt": prompt},
    )
    assert res_admin.status_code == 200
    entry_id = res_admin.json()["id"]

    # 5. 一般フォロワーでは削除不可 (403)
    del_follower_try = client.delete(f"/api/entries/{entry_id}", headers=follower_headers)
    assert del_follower_try.status_code == 403

    # 6. @amkki_aipix のトークンで削除成功 (200)
    del_admin = client.delete(f"/api/entries/{entry_id}", headers=admin_headers)
    assert del_admin.status_code == 200


def test_tools_api_public_and_admin(client):
    # 1. 未ログインでもツール一覧は取得可能
    tools_res = client.get("/api/tools")
    assert tools_res.status_code == 200
    tools = tools_res.json()
    assert isinstance(tools, list)
    assert len(tools) >= 1
    # 最初のツールにPixAIクレジット回収スクリプトが含まれる
    pixai_tool = next((t for t in tools if "PixAI" in t["title"]), None)
    assert pixai_tool is not None

    # 2. 未認証または一般フォロワーでの追加は 403
    unauth_create = client.post(
        "/api/tools",
        json={"title": "Test Tool", "description": "Desc"},
    )
    assert unauth_create.status_code == 403

    # 3. @amkki_aipix としてログイン (パスワード必須)
    admin_login = client.post(
        "/api/auth/x/login",
        json={"username": "amkki_aipix", "following_confirmed": True, "password": "admin"},
    )
    assert admin_login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['token']}"}

    # 4. 管理者による新規ツールの追加 (200)
    create_res = client.post(
        "/api/tools",
        headers=admin_headers,
        json={
            "title": "新自動化スクリプト",
            "description": "テスト説明文",
            "badge": "公開中",
            "tags": "Python, RPA",
            "url": "https://example.com",
            "status": "active",
        },
    )
    assert create_res.status_code == 200
    created_id = create_res.json()["id"]

    # 5. 管理者によるツールの更新 (200)
    update_res = client.put(
        f"/api/tools/{created_id}",
        headers=admin_headers,
        json={"title": "更新版スクリプト"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "更新版スクリプト"

    # 6. 管理者によるツールの削除 (200)
    delete_res = client.delete(f"/api/tools/{created_id}", headers=admin_headers)
    assert delete_res.status_code == 200
