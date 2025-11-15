from app.security.authentification import *

# Test log_in
def test_log_in_valid_user(db_session: Session, dummy_user: models.User):
    """Test the log_in function with a valid, logged out user"""
    dummy_user.logged_in = False
    log_in(db_session, dummy_user.username)

    assert dummy_user.logged_in == True, "User should be logged in"
    

def test_log_in_invalid_user(db_session: Session, dummy_user: models.User):
    """Test the the log_in function with a non-existent user"""
    dummy_user.logged_in = False

    db_session.delete(dummy_user)
    log_in(db_session, dummy_user.username)

    assert db_session.query(models.User).filter_by(username=dummy_user.username).count() == 0, \
        "Should not add user to DB"
    assert dummy_user.logged_in == False, "Should not log in a non-existent user"


def test_log_in_already_logged_in(db_session: Session, dummy_user: models.User):
    """Test the log_in function with a user that it already logged in"""
    log_in(db_session, dummy_user.username)
    
    assert dummy_user.logged_in, "Should not log out user"


# Test log_out
def test_log_out_valid_user(db_session: Session, dummy_user: models.User):
    """Test the log_out function with a valid, logged in user"""
    log_out(db_session, dummy_user.username)

    assert dummy_user.logged_in == False, "User should be logged out"
    

def test_log_out_invalid_user(db_session: Session, dummy_user: models.User):
    """Test the the log_out function with a non-existent user"""
    db_session.delete(dummy_user)
    log_out(db_session, dummy_user.username)

    assert db_session.query(models.User).filter_by(username=dummy_user.username).count() == 0, \
        "Should not add user to DB"
    assert dummy_user.logged_in == True, "Should not log out a non-existent user"


def test_log_out_already_logged_out(db_session: Session, dummy_user: models.User):
    """Test the log_out function with a user that it already logged out"""
    dummy_user.logged_in = False
    log_out(db_session, dummy_user.username)
    
    assert dummy_user.logged_in == False, "Should not log in user"


# Test get_user
def test_get_user_valid_user(db_session: Session, dummy_user: models.User):
    """Test the get_user function with a valid user"""
    assert get_user(db_session, dummy_user.username) == dummy_user, "Should return the same user"


def test_get_user_invalid_user(db_session: Session, dummy_user: models.User):
    """Test the get_user function with a non-existent user"""
    db_session.delete(dummy_user)

    assert get_user(db_session, dummy_user.username) == None, "Should return the same user"


# Test verify_password
def test_verify_password_valid(dummy_user: models.User):
    """Test the verify_password function with valid values"""
    assert verify_password("Dash", dummy_user.pw_salt, dummy_user.pw_hash) == True, \
        "Should return True for a valid password"


def test_verify_password_invalid(dummy_user: models.User):
    """Test the verify_password function with invalid values"""
    assert verify_password("Dasher", dummy_user.pw_salt, dummy_user.pw_hash) == False, \
        "Should return False for an invalid password"
    

# Test authenticate_user
def test_authenticate_user_valid(db_session: Session, dummy_user: models.User):
    """Test the authenticate_user function with an existing user and valid password"""
    assert authenticate_user(db_session, dummy_user.username, "Dash") == dummy_user, \
        "Should return the user"


def test_authenticate_user_invalid_username(db_session: Session, dummy_user: models.User):
    """Test the authenticate_user function with a non-existing user"""
    db_session.query(models.User).delete()
    
    assert authenticate_user(db_session, "Fish", "Byte") == False, \
        "Should return false for a non-existent user"


def test_authenticate_user_invalid_password(db_session: Session, dummy_user: models.User):
    """Test the authenticate_user function with a valid user and invalid password"""
    assert authenticate_user(db_session, dummy_user.username, "Dasher") == False, \
        "Should return false for a invalid password"