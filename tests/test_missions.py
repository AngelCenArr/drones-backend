import pytest
from fastapi import status

# 1. Verificar bloqueo por falta de autenticación (401 Unauthorized)
def test_create_mission_without_token(client):
    payload = {
        "nombre": "Ruta No Autorizada",
        "descripcion": "Intento sin token",
        "waypoints": [
            {"orden_waypoint": 1, "latitud": 20.588, "longitud": -100.389, "altitud_metros": 15.0},
            {"orden_waypoint": 2, "latitud": 20.589, "longitud": -100.390, "altitud_metros": 15.0}
        ]
    }
    response = client.post("/api/v1/missions/", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# 2. Verificar bloqueo de GUARDIA al intentar crear misiones (403 Forbidden)
def test_guardia_cannot_create_mission(client, guardia_token):
    headers = {"Authorization": f"Bearer {guardia_token}"}
    payload = {
        "nombre": "Misión Intrusión",
        "descripcion": "Creada por guardia (no permitido)",
        "waypoints": [
            {"orden_waypoint": 1, "latitud": 20.588, "longitud": -100.389, "altitud_metros": 15.0},
            {"orden_waypoint": 2, "latitud": 20.589, "longitud": -100.390, "altitud_metros": 15.0}
        ]
    }
    response = client.post("/api/v1/missions/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Operación no permitida para el rol asignado."

# 3. Verificar que ADMIN sí puede crear misiones (201 Created)
def test_admin_can_create_mission(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "nombre": "Patrullaje Nocturno Aulas",
        "descripcion": "Vigilancia de pasillos exteriores",
        "waypoints": [
            {"orden_waypoint": 1, "latitud": 20.5881, "longitud": -100.3891, "altitud_metros": 15.0},
            {"orden_waypoint": 2, "latitud": 20.5892, "longitud": -100.3902, "altitud_metros": 18.0}
        ]
    }
    response = client.post("/api/v1/missions/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["nombre"] == "Patrullaje Nocturno Aulas"
    assert data["estado"] == "PROGRAMADA"
    assert len(data["waypoints"]) == 2

# 4. Verificar que tanto GUARDIA como ADMIN pueden listar misiones
def test_guardia_can_list_missions(client, guardia_token):
    headers = {"Authorization": f"Bearer {guardia_token}"}
    response = client.get("/api/v1/missions/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

# 5. Verificar cancelación de misión (Guardia o Admin)
def test_cancel_mission(client, admin_token, guardia_token):
    # Crear como Admin
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "nombre": "Misión para Cancelar",
        "waypoints": [
            {"orden_waypoint": 1, "latitud": 20.588, "longitud": -100.389, "altitud_metros": 15.0},
            {"orden_waypoint": 2, "latitud": 20.589, "longitud": -100.390, "altitud_metros": 15.0}
        ]
    }
    mision_res = client.post("/api/v1/missions/", json=payload, headers=headers_admin).json()
    mision_id = mision_res["id"]

    # Cancelar con token de Guardia
    headers_guardia = {"Authorization": f"Bearer {guardia_token}"}
    cancel_res = client.post(f"/api/v1/missions/{mision_id}/cancel", headers=headers_guardia)
    assert cancel_res.status_code == status.HTTP_200_OK
    assert cancel_res.json()["estado"] == "CANCELADA"