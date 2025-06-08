import random
import pytest
from httpx import AsyncClient
import httpx
from app.main import app
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud, models, schemas

# Test for prototype routes

def test_get_all_prototypes(client: TestClient, db_session: Session):
    """Test retrieving all prototypes with verification of existing and new items"""
    # Get initial count of prototypes
    initial_response = client.get("/prototypes")
    initial_prototypes = initial_response.json()
    initial_count = len(initial_prototypes)
    existing_ids = {p["prototype_id"] for p in initial_prototypes} if initial_prototypes else set()

    # Generate two unique random IDs not already taken
    available_ids = set(range(0, 51)) - existing_ids
    assert len(available_ids) >= 2, "Not enough available IDs for testing"
    random_ids = random.sample(list(available_ids), 2)

    new_prototypes = [
        {"prototype_id": random_ids[0], "prototype_name": "First prototype"},
        {"prototype_id": random_ids[1], "prototype_name": "Second prototype"}
    ]

    # Add new prototypes
    for proto in new_prototypes:
        crud.post_prototype(db=db_session, prototype=schemas.Prototype(**proto))

    # Test GET request
    response = client.get("/prototypes")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify response
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == initial_count + 2  # Should have 2 more than before

    # Verify all new prototypes are present
    for proto in new_prototypes:
        matching_protos = [p for p in data if p["prototype_id"] == proto["prototype_id"]]
        assert len(matching_protos) == 1, \
            f"Expected exactly one prototype with ID {proto['prototype_id']}"
        assert matching_protos[0]["prototype_name"] == proto["prototype_name"]

