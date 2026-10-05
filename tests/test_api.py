from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_mode_mock():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["mode"] == "mock"


def test_detection_francais():
    r = client.post("/detect-language",
                    json={"text": "Je ne peux plus acceder a mon compte."})
    assert r.status_code == 200
    assert r.json()["language"] == "fr"


def test_detection_anglais():
    r = client.post("/detect-language",
                    json={"text": "Hello, I forgot my password"})
    assert r.status_code == 200
    assert r.json()["language"] == "en"


def test_detection_arabe():
    r = client.post("/detect-language",
                    json={"text": "لا أستطيع الدخول إلى حسابي"})
    assert r.status_code == 200
    assert r.json()["language"] == "ar"


def test_texte_trop_court_rejete():
    r = client.post("/detect-language", json={"text": "ab"})
    assert r.status_code == 422


def test_champ_text_absent():
    r = client.post("/detect-language", json={})
    assert r.status_code == 422


def test_fournisseur_en_panne(monkeypatch):
    from app import main

    def boom(text):
        raise RuntimeError("panne simulée")

    monkeypatch.setattr(main.provider, "detect_language", boom)
    r = client.post("/detect-language", json={"text": "Bonjour tout le monde"})
    assert r.status_code == 503
    assert "panne" not in r.text  # no technical detail leaks to the client