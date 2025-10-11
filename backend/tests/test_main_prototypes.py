from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models
from random import randint
import pytest

@pytest.fixture
def dummy_prototype(db_session: Session):
    """Insert dummy prototype in DB and return it"""
    random_id = randint(1, 9999)
    # Ensure ID is unique
    while random_id in db_session.query(models.Prototype.prototype_id).all():
        random_id = randint(1, 9999)
    # Create prototype and add to DB
    new_proto = models.Prototype(prototype_id=random_id, prototype_name="Test Proto")
    db_session.add(new_proto)
    db_session.flush()
    yield new_proto


def test_get_all_prototypes(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes endpoint that retrieves all prototypes"""
    prototypes_list = db_session.query(models.Prototype).all() # Get all prototypes from DB
    
    response = client.get("/prototypes")
    assert response.status_code == 200, "Expected status code 200"
    data = response.json()
    
    assert len(data) == len(prototypes_list), "Response length should match prototypes in DB"

    # Check if each prototype is in the response
    for proto in prototypes_list:
        assert {"prototype_id": proto.prototype_id, "prototype_name": proto.prototype_name} in data, \
            f"Prototype with ID {proto.prototype_id} should be in response"


def test_get_prototype_by_id(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes/{prototype_id} endpoint to retrieve a prototype by its id"""
    response = client.get(f"/prototypes/{dummy_prototype.prototype_id}")
    assert response.status_code == 200, "Expected status code 200"
    data = response.json()

    assert {"prototype_id": dummy_prototype.prototype_id, "prototype_name": dummy_prototype.prototype_name} == data, \
        "Response data should match the test prototype"


def test_get_non_existent_prototype_by_id(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes/{prototype_id} endpoint with a non-existent prototype id"""
    db_session.delete(dummy_prototype) # Remove the dummy prototype to ensure ID does not exist

    response = client.get(f"/prototypes/{dummy_prototype.prototype_id}")
    assert response.status_code == 404, "Expected status code 404 for non-existent prototype"
    data = response.json()
    assert data["detail"] == "Prototype not found", "Expected 'Prototype not found' message"



def test_post_duplicate_id_prototype(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes endpoint to add a prototype with an existing prototype_id"""
    duplicate_proto = {"prototype_id": dummy_prototype.prototype_id, "prototype_name": "Duplicate Proto"}

    response = client.post("/prototypes", json=duplicate_proto)
    assert response.status_code == 409, "Expected status code 409 for duplicate prototype_id"
    data = response.json()
    assert data["detail"] == "Prototype with this id already exists", "Expected 'Prototype with this id already exists' message"