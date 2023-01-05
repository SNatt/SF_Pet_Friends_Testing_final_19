from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    ''' Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key'''

    status, result = pf.get_api_key(email, password)

    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    ''' Проверяем что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key.
        Далее используя этот ключ запрашиваем список всех питомцев и проверяем,
        что список не пустой. Доступное значение параметра filter - 'my_pets' либо - пусто.
    '''

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Тимоша', animal_type='Британец',
                                     age='6', pet_photo='images/cattim.jpg'):
    ''' Проверяем возможность добавления нового питомца с корректными данными '''

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result['name'] == name


def test_delete_self_pet():
    '''Проверяем возможность удаления своего питомца'''

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, 'Тимоша', 'Британец', '6', 'images/cattim.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_update_self_pet(name='Измена', animal_type='Изменённый', age='5'):
    '''Проверяем возможность обновления информации о своём питомце'''

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception('Мои питомцы отсутствуют')

def test_get_api_key_with_invalid_pass_and_valid_mail(email=valid_email, password= invalid_password):
    '''Проверяем запрос с некорректным паролем и корректным email'''

    status, result = pf.get_api_key(email, password)

    # Проверяем, что статус не равен 200, а результат не содержит ключ
    assert status != 200
    assert 'key' not in result

def test_get_api_key_with_invalid_mail_and_valid_password(email=invalid_email, password=valid_password):
    '''Проверяем запрос с некорректным email и корректным паролем.
    '''

    status, result = pf.get_api_key(email, password)

    # Проверяем, что статус не равен 200, а результат не содержит ключ
    assert status != 200
    assert 'key' not in result

def test_del_any_pet():
    '''Проверка с негативным сценарием. Попытка удалить не своего питомца из общего списка.
       Тест будет считаться невыполненным если попытка удаления будет успешной.'''

    filter = ''
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, any_pets = pf.get_list_of_pets(auth_key, filter)

    # Берём id последнего питомца из списка
    any_pet_id = any_pets['pets'][-1]['id']
    status, _ = pf.delete_pet(auth_key, any_pet_id)
    _, any_pets = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert any_pet_id not in any_pets.values()