import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_login_success(async_client, test_user):
    """Test successful login with correct credentials."""
    login_data = {
        "email": test_user.email,
        "password": "correct_password"  # The plain text password used to create test_user
    }
    
    response = await async_client.post("/login", json=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client, test_user):
    """Test login failure when given an invalid password."""
    login_data = {
        "email": test_user.email,
        "password": "wrongpassword123"
    }
    
    response = await async_client.post("/login", json=login_data)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid Credentials"


@pytest.mark.asyncio
async def test_login_user_not_found(async_client):
    """Test login failure when the email does not exist."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "somepassword"
    }
    
    response = await async_client.post("/login", json=login_data)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Invalid Credentials"
