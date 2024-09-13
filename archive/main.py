import requests
import pandas as pd
import time
import json
import openpyxl
import concurrent.futures
from apis import *  # Предполагается, что файл apis.py содержит список API ключей

url = "https://api.arliai.com/v1/chat/completions"
api = '44be0b68-a20d-4e30-889a-5f28fd471f41'  # Не используется в коде, так как используется список API ключей
headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {api}"
}

prompt_trigger_input_file = 'trigger_input.txt'
with open(prompt_trigger_input_file, 'r') as f:
    trigger_input = f.read()

prompt_trigger_process_file = 'prompt_trigger_process.txt'
with open(prompt_trigger_process_file, 'r') as f:
    prompt_trigger_process = f.read()

prompt_vacancy_process_file = 'prompt_vacancy_process.txt'
with open(prompt_vacancy_process_file, 'r') as f:
    prompt_vacancy_process = f.read()

# Создание Excel файла
workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet['A1'] = 'Номер итерации'
worksheet['B1'] = 'Ответ'
worksheet['C1'] = 'API индекс'
worksheet['D1'] = 'Успешный запрос'

# Статистика
total_requests = 0
successful_requests = 0
total_time = 0
sad = 0

# Настройки HH API
hh_headers = {
"User-Agent": "Your User Agent"
}

# Имя файла Excel
excel_file = 'vacancies.xlsx'

# Функция для генерации поисковых запросов
def generate_search_queries(trigger):
    start_time = time.time()
    query = f"Введеный пользователем фильтр: {trigger_input}, " + f"Задача: {prompt_trigger_process}"
    print(query)
    try:
        payload = json.dumps({
        "model": "Meta-Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "user", "content": query},
        ],
        "repetition_penalty": 1.1,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 1024,
        "stream": True
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        chunks = []
        for line in response.text.splitlines():
            if line.startswith('data: '):
                try:
                    chunk = json.loads(line[6:])
                    if 'choices' in chunk and chunk['choices']:
                        delta = chunk['choices'][0].get('delta', {})
                        if 'content' in delta:
                            chunks.append(delta['content'])
                except json.JSONDecodeError:
                    pass
        answer = ''.join(chunks)
        search_queries = answer.split('\n')
    except Exception as e:
        print(f"Ошибка при генерации поисковых запросов: {e}. Повторяем попытку.")
        time.sleep(5)  # Пауза перед повторной попыткой
        return generate_search_queries(trigger)
    end_time = time.time()
    print(f"Генерация поисковых запросов: {end_time - start_time:.2f} секунд")
    print(search_queries)
    return search_queries

# Функция для получения вакансий с HH API
def get_vacancies(keyword):
    start_time = time.time()
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "per_page": 10
    }
    try:
        response = requests.get(url, params=params, headers=hh_headers)
        if response.status_code == 200:
            data = response.json()
            vacancies = data.get("items")
            end_time = time.time()
            print(f"Получение вакансий: {end_time - start_time:.2f} секунд")
            return vacancies
        else:
            print(f"Ошибка при получении вакансий: {response.status_code}")
            return []
    except Exception as e:
        print(f"Ошибка при получении вакансий: {e}. Повторяем попытку.")
        time.sleep(5)  # Пауза перед повторной попыткой
        return get_vacancies(keyword)

# Функция для получения информации о вакансии
def get_vacancy_details(vacancy_id):
    start_time = time.time()
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    try:
        response = requests.get(url, headers=hh_headers)
        if response.status_code == 200:
            data = response.json()
            end_time = time.time()
            print(f"Получение информации о вакансии: {end_time - start_time:.2f} секунд")
            time.sleep(0.03)
            return data
        else:
            print(f"Ошибка при получении информации о вакансии: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при получении информации о вакансии: {e}. Повторяем попытку.")
        time.sleep(5)  # Пауза перед повторной попыткой
        return get_vacancy_details(vacancy_id)

# Функция для проверки наличия триггера в описании вакансии
def check_trigger_presence(description, trigger, api):
    global successful_requests
    global sad
    global total_requests
    global total_time
    total_requests += 1
    start_time = time.time()
    message = f"Заданный фильтр на триггер: {trigger_input}" + f" Описание вакансии: {description}"+ f" Задача: {prompt_vacancy_process}"
    print(message)
    try:
        payload = json.dumps({
        "model": "Meta-Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "user", "content": message},
        ],
        "repetition_penalty": 1.1,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 1024,
        "stream": True
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {api}"
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        chunks = []
        for line in response.text.splitlines():
            if line.startswith('data: '):
                try:
                    chunk = json.loads(line[6:])
                    if 'choices' in chunk and chunk['choices']:
                        delta = chunk['choices'][0].get('delta', {})
                        if 'content' in delta:
                            chunks.append(delta['content'])
                except json.JSONDecodeError:
                    pass
        trigger_presence = ''.join(chunks)
        print(trigger_presence)
        if trigger_presence:
            successful_requests += 1
        else:
            sad += 1
        end_time = time.time()
        total_time += end_time - start_time
        return trigger_presence
    except Exception as e:
        print(f"Ошибка при проверке наличия триггера: {e}. Повторяем попытку.")
        return check_trigger_presence(description, trigger, api)

# Функция для обработки одной вакансии
def process_vacancy(row, trigger, api):
    description = row['description']
    try:
        trigger_presence = check_trigger_presence(description, trigger, api)
        return row.name, trigger_presence
    except Exception as e:
        print(f"Ошибка при обработке вакансии: {e}")
        return row.name, None

# Основная функция
def main():
    # Создание Excel файла, если его нет
    try:
        df = pd.read_excel(excel_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['id', 'vacancy_url', 'employer_url', 'description', 'trigger_presence'])
        df.to_excel(excel_file, index=False)

    # Генерация поисковых запросов
    search_queries = generate_search_queries(trigger_input)

    # Получение вакансий по каждому поисковому запросу
    vacancies_list = []
    for query in search_queries:
        vacancies = get_vacancies(query)
        if vacancies:
            for vacancy in vacancies:
                vacancy_id = vacancy.get("id")
                vacancy_details = get_vacancy_details(vacancy_id)
                if vacancy_details:
                    vacancy_url = vacancy_details.get("alternate_url")
                    employer_url = vacancy_details.get("employer").get("alternate_url")
                    description = vacancy_details.get("description")
                    # Добавление информации о вакансии в DataFrame
                    new_row = {'id': vacancy_id,
                              'vacancy_url': vacancy_url,
                              'employer_url': employer_url,
                              'description': description,
                              'trigger_presence': None}
                    vacancies_list.append(new_row)
    df = pd.concat([df, pd.DataFrame(vacancies_list)], ignore_index=True)
    # Сохраняем DataFrame в Excel после добавления новых вакансий
    df.to_excel(excel_file, index=False)

    # Проверка наличия триггера для всех вакансий
    vacancies_to_check = df[df['trigger_presence'].isna()]

    # Параллельная обработка вакансий с распределением API ключей
    api_index = 0
    # Создаем пул потоков *после* получения вакансий
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(apis), len(vacancies_to_check))) as executor:
        futures = []
        for index, row in vacancies_to_check.iterrows():
            if api_index >= len(apis):
                api_index = 0  # Возвращаемся к началу списка API
                print("Все API ключи исчерпаны, переходим к следующей итерации.")
                break  # Прекращаем обработку, так как ключи закончились
            api = apis[api_index]
            future = executor.submit(process_vacancy, row, trigger_input, api)
            futures.append((future, index))
            api_index += 1

        for future, index in futures:
            row_index, trigger_presence = future.result()
            if trigger_presence is not None:
                # Обновление trigger_presence в DataFrame
                df.loc[index, 'trigger_presence'] = trigger_presence
                # Сохранение изменений в Excel файл *сразу после обновления*
                df.to_excel(excel_file, index=False)

    # Выводим статистику в Excel
    worksheet['A2'] = 'Общая статистика'
    worksheet['A3'] = 'Общее количество запросов:'
    worksheet['B3'] = total_requests
    worksheet['A4'] = 'Успешных запросов:'
    worksheet['B4'] = successful_requests
    worksheet['A5'] = 'Неуспешных запросов:'
    worksheet['B5'] = total_requests - successful_requests
    worksheet['A6'] = 'Общее время генерации:'
    worksheet['B6'] = total_time
    worksheet['A7'] = 'Среднее время на запрос:'
    worksheet['B7'] = total_time / total_requests

    workbook.save("results.xlsx") 

if __name__ == "__main__":
    main()