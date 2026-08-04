# orders/test_orders.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(username="testuser", email="test@test.com", password="password123")
    return user

@pytest.fixture
def test_order(db, test_user):
    return Order.objects.create(user=test_user, total_price=100.00)


@pytest.mark.django_db
def test_get_orders_without_auth(api_client):
   
    response = api_client.get('/api/orders/')
    assert response.status_code == 401 

@pytest.mark.django_db
def test_get_orders_with_auth(api_client, test_user, test_order):
    
    api_client.force_authenticate(user=test_user)
    
    response = api_client.get('/api/orders/')
    
    assert response.status_code == 200
    assert len(response.data['results']) == 1 
    assert response.data['results'][0]['total_price'] == "100.00"