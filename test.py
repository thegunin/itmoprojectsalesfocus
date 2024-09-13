import psycopg2
import json
import requests
import g4f
from g4f.client import Client
import time
import re
import sys

from config import *

_providers = [g4f.Provider.Chatgpt4o, g4f.Provider.ChatgptFree, g4f.Provider.HuggingChat]

# Функции
def create_tables(recreate_tables=True):
    # Подключение к базе данных
    conn = psycopg2.connect(
        host=host_config,
        database=database_config,
        user=user_config,
        password=password_config
    )

    # Создание курсора
    cur = conn.cursor()

    # Если recreate_tables равна True, удаляем таблицы
    if recreate_tables:
        cur.execute("DROP TABLE IF EXISTS user_inputs;")
        cur.execute("DROP TABLE IF EXISTS vacancies;")
        cur.execute("DROP TABLE IF EXISTS api_keys;")

    # Create Table 1
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_inputs (
            id SERIAL PRIMARY KEY,
            user_input TEXT,
            search_query TEXT
        );
    """)

    # Create Table 2
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            vacancy_url TEXT,
            vacancy_text TEXT,
            employer_url TEXT,
            signal TEXT
        );
    """)

    # Create Table 3
    cur.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id SERIAL PRIMARY KEY,
            api_key TEXT,
            is_used BOOLEAN
        );
    """)

    # Сохранение изменений
    conn.commit()

    # Закрытие курсора и соединения
    cur.close()
    conn.close()

def read_file_to_variable(file_name):
    with open(file_name, 'r') as file:
        text = file.read()
    return text

def LLM_request_arliai(query, model = "Meta-Llama-3.1-70B-Instruct", api = '3f5c76a6-a561-47c5-bdb0-9d55d56ca663'):
    start_time = time.time()
    url = "https://api.arliai.com/v1/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "user", "content": query}
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
    #print(response)

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

    end_time = time.time()
    processing_time = end_time - start_time
    #print(answer)
    #print(f"Время обработки: {processing_time:.2f} секунд")
    return(answer)

def LLM_request_freegpt(query, model = 'gpt-3.5-turbo'):
    start_time = time.time()
    client = Client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": query}],
        provider=g4f.Provider.HuggingChat
    )
    end_time = time.time()
    processing_time = end_time - start_time
    #print(f"Время обработки: {processing_time:.2f} секунд")
    #print(response.choices[0].message.content)
    return(response.choices[0].message.content)

# Функция для получения ID вакансий с HH API (с поиска)
def get_vacancies_ids_from_hh_search(query):
    vacancies_per_page = 10
    hh_headers = {
        "User-Agent": "Your User Agent"
        }
    start_time = time.time()
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,
        "per_page": vacancies_per_page
    }
    try:
        response = requests.get(url, params=params, headers=hh_headers)
        if response.status_code == 200:
            data = response.json()
            vacancies = data.get("items")
            print(f'    По запросу {query} найдено {len(vacancies)} вакансий c учетом ограничения MAX выдачи вакансий: {vacancies_per_page}')
            vacancies_id = []
            for vacancy in vacancies: 
                vacancies_id.append(vacancy.get('id'))
            end_time = time.time()
            print(f'    Время обработки: {end_time - start_time:.2f} секунд')
            return vacancies_id
        else:
            #print(f"Ошибка при получении вакансий: {response.status_code}")
            return []
    except Exception as e:
        #print(f"Ошибка при получении вакансий: {e}. Повторяем попытку.")
        time.sleep(5)  # Пауза перед повторной попыткой
        return get_vacancies_ids_from_hh_search(query)

# Функция для получения информации о вакансии (с ID)
def get_vacancy_details_from_id(vacancy_id):
    hh_headers = {
        "User-Agent": "Your User Agent"
        }
    start_time = time.time()
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    try:
        response = requests.get(url, headers=hh_headers)
        if response.status_code == 200:
            data = response.json()
            end_time = time.time()
            #print(f"Получение информации о вакансии: {end_time - start_time:.2f} секунд")
            vacancy_url = data.get("alternate_url")
            employer_url = data.get("employer").get("alternate_url")
            description = data.get("description")

            # Connect to the database
            conn = psycopg2.connect(
                host= host_config,
                database=database_config,
                user=user_config,
                password=password_config
            )
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO vacancies (id, vacancy_url, vacancy_text, employer_url)
                VALUES (%s, %s, %s, %s)
            """, (vacancy_id, vacancy_url, description, employer_url))

            conn.commit()
            conn.close()
            time.sleep(0.2)

        else:
            #print(f"Ошибка при получении информации о вакансии: {response.status_code}")
            return None
    except Exception as e:
        #print(f"Ошибка при получении информации о вакансии: {e}.")
        pass

def convert_LLM_answer_to_list(text):
    # Удалить все символы до и после квадратных скобок
    text = re.search(r'\[(.*?)\]', text, re.DOTALL).group(1)
    
    # Разделить текст на отдельные элементы массива
    array = re.split(r',\s*', text)
    
    # Удалить кавычки из элементов массива
    array = [element.strip().strip('"') for element in array]
    
    return array

# Получение ID и описаний необработанных вакансий
def db_get_unprocessed_vacancies_id_text():
    try:
        conn = psycopg2.connect(
            host=host_config,
            database=database_config,
            user=user_config,
            password=password_config
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, vacancy_text FROM vacancies WHERE signal IS NULL
        """)

        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result

    except psycopg2.Error as e:
        #print(f"Ошибка подключения к базе данных: {e}")
        return None

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
    """
    Печатает в консоль строку прогресса.

    Parameters
    ----------
    iteration : int
        Текущая итерация.
    total : int
        Общее количество итераций.
    prefix : str, optional
        Текст, который нужно вывести перед строкой прогресса.
    suffix : str, optional
        Текст, который нужно вывести после строки прогресса.
    decimals : int, optional
        Количество знаков после запятой в процентах.
    length : int, optional
        Длина строки прогресса.
    fill : str, optional
        Символ, который используется для заполнения строки прогресса.
    print_end : str, optional
        Символ, который нужно вывести в конце строки.
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\033[92m{prefix}|{bar}| {percent}% {suffix}\033[0m', end=print_end)

def print_status(status_text, color):
    """
    Выводит в консоль текст статуса с цветом.

    Parameters
    ----------
    status_text : str
        Текст статуса.
    color : str
        Цвет текста (например, 'green', 'red', 'yellow').
    """
    if color == 'green':
        print(f"\033[92m{status_text}\033[0m")
    elif color == 'red':
        print(f"\033[91m{status_text}\033[0m")
    elif color == 'yellow':
        print(f"\033[93m{status_text}\033[0m")
    else:
        print(f"{status_text}")

def print_animated_status(status_text, color):
    """
    Выводит в консоль текст статуса с цветом и анимацией.

    Parameters
    ----------
    status_text : str
        Текст статуса.
    color : str
        Цвет текста (например, 'green', 'red', 'yellow').
    """
    for i in range(len(status_text) + 1):
        print(f"\033[92m{status_text[:i]}\033[0m", end="\r")
        time.sleep(0.05)
        sys.stdout.flush()
    print(f"\033[92m{status_text}\033[0m")
 



# Основная программа
create_tables(recreate_tables=True)

# определение промптов 

print_status("Поиск компаний по заданному фильтру", 'green')
print("")

# Получение сигнала от пользователя
user_input = input("Введите фильтр для поиска компании: ")
print("")

print_status("➡️ Запуск системы", 'green')
print("")

# Формулировка сигнала от пользователя
print_status("🎯 Сигнал от пользователя:", 'green')
print(f"\033[97m{user_input}\033[0m") # Белый текст
print("")

total_hh_queries = 30
prompt_for_search_hh = f'Сигнал, заданный пользователем: {user_input}. Всего нужно сгенерировать запросов: {total_hh_queries}. Инструкция к сигналу: {read_file_to_variable("config/prompt_trigger_process.txt")}'

print_status("🔎 Генерация запросов для поиска вакансий на HH.RU", 'green')
print("")

# Добавление вакансий в БД по сформированным запросам
hh_search_queries_list = convert_LLM_answer_to_list(LLM_request_freegpt(prompt_for_search_hh))
print_status("🧠 Ответ LLM:", 'green')
print(f"\033[97m{hh_search_queries_list}\033[0m") # Белый текст
print("")

# Вывод прогресс-бара
print_status("⏳ Начало обработки вакансий", 'green')
for i in range(len(hh_search_queries_list) + 1):
    print_progress_bar(i, len(hh_search_queries_list), prefix='Обработка вакансий:', suffix='Завершено', length=50)
    time.sleep(0.1)
    sys.stdout.flush()

print("\n")

for i, query in enumerate(hh_search_queries_list):
    print_status(f"🔎 Обработка запроса №{i+1}: {query}", 'green')
    print("")
    for id in get_vacancies_ids_from_hh_search(query): 
        get_vacancy_details_from_id(id)
    print("")

print_status("🕵️‍♀️ Поиск сигналов в вакансиях", 'green')
print("")

unprocessed_vacancies_list = db_get_unprocessed_vacancies_id_text()

# Вывод прогресс-бара
for i in range(len(unprocessed_vacancies_list) + 1):
    print_progress_bar(i, len(unprocessed_vacancies_list), prefix='Обработка вакансий:', suffix='Завершено', length=50)
    time.sleep(0.1)
    sys.stdout.flush()

print("\n")

for i, unprocessed_vacancy in enumerate(unprocessed_vacancies_list):
    unprocessed_vacancy_id = unprocessed_vacancy[0]
    print_animated_status(f"🕵️‍♀️ Обработка вакансии №{i+1}:", 'green')
    print("")
    prompt_for_vacancy_process = f'1. Сигнал, заданный пользователем: {user_input}. 2. Текст вакансии: {unprocessed_vacancy[1]}. 3. Инструкция к поиску сигнала: {read_file_to_variable("config/prompt_vacancy_process.txt")}'
    signal_list = convert_LLM_answer_to_list(LLM_request_freegpt(prompt_for_vacancy_process))
    print_status("🧠 Ответ LLM:", 'green')
    print(f"\033[97m{signal_list}\033[0m") # Белый текст
    print("")

    conn = psycopg2.connect(
        host=host_config,
        database=database_config,
        user=user_config,
        password=password_config
    )
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE vacancies
        SET signal = %s
        WHERE id = %s
    """, (signal_list, unprocessed_vacancy_id))

    conn.commit()
    conn.close()

print("")
print_status("🎉 Завершение системы 🎉", 'green')


