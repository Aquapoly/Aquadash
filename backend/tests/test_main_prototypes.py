from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models

# GET /prototypes
def test_get_all_prototypes(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes endpoint that retrieves all prototypes"""
    prototypes_list = db_session.query(models.Prototype).all()
    
    response = client.get("/prototypes")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    
    assert len(data) == len(prototypes_list), "Response length should match prototypes in DB"

    for proto in prototypes_list:
        assert {"prototype_id": proto.prototype_id, "prototype_name": proto.prototype_name} in data, \
            f"Prototype with ID {proto.prototype_id} should be in response"


# GET /prototypes/{prototype_id}
def test_get_prototype_by_id(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes/{prototype_id} endpoint to retrieve a prototype by its id"""
    response = client.get(f"/prototypes/{dummy_prototype.prototype_id}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()

    assert {"prototype_id": dummy_prototype.prototype_id, "prototype_name": dummy_prototype.prototype_name} == data, \
        "Response data should match the test prototype"


def test_get_non_existent_prototype_by_id(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes/{prototype_id} endpoint with a non-existent prototype id"""
    db_session.delete(dummy_prototype) # Remove the dummy prototype to ensure ID does not exist

    response = client.get(f"/prototypes/{dummy_prototype.prototype_id}")
    assert response.status_code == 404, f"Expected status code 404 for not found prototype, got {response.status_code}"


def test_get_prototypes_return_types(client: TestClient, db_session: Session,  dummy_prototype: models.Prototype):
    """Test /prototypes/{prototype_id} endpoint to check if it returns the right types"""
    response = client.get(f"/prototypes/{dummy_prototype.prototype_id}")
    data = response.json()

    assert isinstance(data["prototype_id"], int), f"Prototype id should be an int, was {type(data['prototype_id'])}"
    assert isinstance(data["prototype_name"], str), f"Prototype name should be a string, was {type(data['prototype_name'])}"


# POST /prototypes
def test_post_duplicate_id_prototype(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes endpoint to add a prototype with an existing prototype_id"""
    duplicate_proto = {"prototype_id": dummy_prototype.prototype_id, "prototype_name": "Duplicate Proto"}

    response = client.post("/prototypes", json=duplicate_proto)
    assert response.status_code == 409, f"Expected status code 409 for duplicate prototype_id, got {response.status_code}"


def test_post_invalid_prototype(client: TestClient, db_session: Session):
    """Test /prototypes endpoint to add a prototype with invalid data"""
    invalid_proto = {"prototype_name": "Invalid Proto"}  # Missing prototype_id

    response = client.post("/prototypes", json=invalid_proto)
    assert response.status_code == 400, f"Expected status code 400 for missing field, got {response.status_code}"
    assert db_session.query(models.Prototype).filter_by(prototype_name="Invalid Proto").count() == 0, \
        "Should not add prototype with no id to DB"
    
    invalid_proto = {"prototype_id": "id", "prototype_name": "Invalid Proto"}

    response = client.post("/prototypes", json=invalid_proto)
    assert response.status_code == 422, "Expected status code 422 for invalid type"
    assert db_session.query(models.Prototype).filter_by(prototype_name="Invalid Proto").count() == 0, \
        "Should not add prototype with invalid type to DB"


def test_post_prototype(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes endpoint to add a valid prototype"""
    db_session.delete(dummy_prototype) # Remove the dummy prototype to ensure ID does not exist

    new_proto = {"prototype_id": dummy_prototype.prototype_id, "prototype_name": "Valid Proto"}
    response = client.post("/prototypes", json=new_proto)
    assert response.status_code == 201, f"Expected status code 201 for created ressource, got {response.status_code}"


def test_post_special_char_prototype(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes endpoint to add a prototype with special characters in name"""
    db_session.delete(dummy_prototype) # Remove the dummy prototype to ensure ID does not exist

    new_proto = {"prototype_id": dummy_prototype.prototype_id, "prototype_name": """!@#$%^&*()_+{}|:\"<>?\\`~☺"""}
    response = client.post("/prototypes", json=new_proto)
    assert response.status_code == 201, f"Expected status code 201 for created ressource, got {response.status_code}"


def test_post_sql_injection_prototype(client: TestClient, db_session: Session, dummy_prototype: models.Prototype):
    """Test /prototypes endpoint to add a prototype with SQL injection attempt in name"""
    db_session.delete(dummy_prototype) # Remove the dummy prototype to ensure ID does not exist

    query = f"""INSERT INTO prototypes (prototype_id, prototype_name) VALUES ({dummy_prototype.prototype_id+1}, 'Injection'); --"""
    new_proto = {"prototype_id": dummy_prototype.prototype_id, "prototype_name": f"""Test'); {query}"""}
    response = client.post("/prototypes", json=new_proto)

    assert db_session.query(models.Prototype).filter_by(prototype_id=dummy_prototype.prototype_id+1).count() == 0, \
        "SQL Injection should not have succeeded in adding a new prototype"
    

def test_post_negative_id_prototype(client: TestClient, db_session: Session):
    """Test /prototypes endpoint with a prototype with a negative id"""
    new_proto = {"prototype_id": -1, "prototype_name": "Illegal Proto"}

    response = client.post("/prototypes", json=new_proto)
    assert response.status_code == 400, f"Should return 400 for bad request, got {response.status_code}"