import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from students.models import Course, Student
import json


@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory

@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory

# проверка получения первого курса
@pytest.mark.django_db
def test_course_one(client, courses_factory):
    #Arrange
    course = courses_factory(_quantity=1)
    #Act
    response = client.get(f'/api/v1/courses/{course[0].id}/')
    #Assert
    data = response.json()
    assert response.status_code == 200
    assert data['name'] == course[0].name

# проверка получения списка курсов
@pytest.mark.django_db
def test_list_of_courses(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    #Act
    response = client.get('/api/v1/courses/')
    #Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    for i, m in enumerate(data):
        assert m['name'] == courses[i].name

#проверка фильтрации списка курсов по id:
@pytest.mark.django_db
def test_filter_courses_id(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    #Act
    response = client.get('/api/v1/courses/', {'id': courses[5].id})
    #Assert
    data = response.json()
    assert data[0]['id'] == courses[5].id
    assert data[0]['name'] == courses[5].name

#проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_filter_courses_name(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    #Act
    response = client.get('/api/v1/courses/', {'name': courses[3].name})
    #Assert
    data = response.json()
    assert data[0]['name'] == courses[3].name

#тест успешного создания курса
@pytest.mark.django_db
def test_create_course(client):
    #Arrange
    count = Course.objects.count()
    course_new = {'name': 'Python'}
    #Act
    response = client.post('/api/v1/courses/', data=course_new, format='json')
    #Assert
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == course_new['name']
    assert Course.objects.count() == count + 1

#тест успешного обновления курса
@pytest.mark.django_db
def test_update_course(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    course_update = {'name': 'Django'}
    #Act
    response = client.patch(f'/api/v1/courses/{courses[3].id}/', data=course_update, format='json')
    #Assert
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == course_update['name']
    # print(data['name']) #для вывода на печать использовать команду pytest -s


#тест успешного удаления курса
@pytest.mark.django_db
def test_delete_course(client, courses_factory):
    #Arrange
    courses = courses_factory(_quantity=10)
    count = Course.objects.count()
    course_deleted = courses[3].id
    #Act
    response = client.delete(f'/api/v1/courses/{courses[3].id}/')
    #Assert
    assert response.status_code == 204
    assert Course.objects.count() == count - 1
    assert not Course.objects.filter(id=course_deleted).exists()
    response_deleted = client.get(f'/api/v1/courses/{course_deleted}/')
    assert response_deleted.status_code == 404