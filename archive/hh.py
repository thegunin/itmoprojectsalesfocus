import requests
import time
import pandas as pd
from bs4 import BeautifulSoup

# Настройки HH API
hh_headers = {
"User-Agent": "Your User Agent"
}

# Функция для получения информации о вакансии
def get_vacancy_details(vacancy_id):
    start_time = time.time()
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    try:
        response = requests.get(url, headers=hh_headers)
        if response.status_code == 200:
            data = response.json()
            end_time = time.time()
            print(f"Получение информации о вакансии {vacancy_id}: {end_time - start_time:.2f} секунд")
            time.sleep(0.03)
            return data
        else:
            print(f"Ошибка при получении информации о вакансии {vacancy_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при получении информации о вакансии {vacancy_id}: {e}. Повторяем попытку.")
        time.sleep(5)  # Пауза перед повторной попыткой
        return get_vacancy_details(vacancy_id)

# Функция для обработки Excel файла
def process_excel_file(file_path):
    try:
        # Чтение Excel файла
        df = pd.read_excel(file_path)
        
        # Проверка наличия столбца 'vacancy_id'
        if 'vacancy_id' not in df.columns:
            print("Ошибка: в файле отсутствует столбец 'vacancy_id'")
            return
        
        # Создание нового столбца 'description'
        df['description'] = None
        
        # Получение информации о вакансиях и заполнение столбца 'description'
        for index, row in df.iterrows():
            vacancy_id = row['vacancy_id']
            vacancy_details = get_vacancy_details(vacancy_id)
            if vacancy_details is not None:
                description = vacancy_details.get("description")
                if description is not None:
                    soup = BeautifulSoup(description, 'html.parser')
                    description_text = soup.get_text()
                    df.loc[index, 'description'] = description_text
        
        # Сохранение измененного DataFrame в новый Excel файл
        df.to_excel('result.xlsx', index=False)
        print("Результаты сохранены в файл 'result.xlsx'")
    
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

# Пример использования
process_excel_file('input.xlsx')