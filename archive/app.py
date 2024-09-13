import requests
import json
import concurrent.futures
import time
import openpyxl

url = "https://api.arliai.com/v1/chat/completions"

# Список всех API ключей
apis = [
    'ccaa6221-5588-4cc2-82d5-6f8b5ca9b6e4',
    'c2455aa0-850d-47b7-a09b-9a6eb50debad',
    '9c1589cb-c65a-4c6f-a8b4-6663dcc9268c',
    '60dee623-8ecd-4187-9e28-4624397055ff',
    '3f5c76a6-a561-47c5-bdb0-9d55d56ca663',
    '1e1f602e-38c7-4c97-98fc-803f17dfe9e8',
    '3f101c98-d27a-4faa-8dd9-b6e45efbf6a0',
    '3f33979e-2f93-40cf-9338-9ac49da47840',
    '730392cc-b18f-49de-8e4e-3f22656f2408',
    '27e24933-a21d-4602-b39c-3d9da1cb87c0',
    '9962c4a1-21b3-4f9c-8c19-328c9aec56e1',
    'dfaf6574-fc34-41e4-b41d-91f39d5ccc3d',
    '10cf3979-f07a-45ce-93d4-3f3194bb2d0b',
    'cf1d2a1c-f213-4d7a-9a6b-90353c02bedf',
    '87dec2b4-1750-47d4-8194-0eb9afb1d59b',
    'f8082d0e-3ae7-4aa5-b140-56a64e5e1aeb',
    '9b7f4109-70f4-4b56-a0d6-0f1fe9d24ddd',
    '44be0b68-a20d-4e30-889a-5f28fd471f41',
    'ca7ab9d1-7662-4a63-a1b9-beb961891993',
    '57fafc78-83d6-4f6a-8ac7-1d59aa04723f',
    'd391e988-a826-4161-92ae-327c997164f7',
    '7f6af3c1-dd36-4d4e-83e5-5fa30ae6008c',
    'd8a64892-6483-4c23-9a88-9538c7545053',
    '2e838b43-e6ee-4d82-9656-c718332a1bb2',
    'eeb63f76-8daf-437e-ac09-3ddbfad1ba22',
    'fcd4012c-9aca-4528-ab24-557857dfd110',
    'ed3124d9-5121-422f-bfe2-6c1c3ef63fed',
    '0d9b8cc5-a080-4774-9cc2-fcd7dfc9e23d',
    'b4a69d6c-14d4-49c7-87f8-a60f8fd09bd5',
    '05828cc7-230e-4c53-9b3d-882b9c3f2312',
    '2fdde39f-0f73-4d99-9690-19ec4d3e2a65',
    'ee32cb98-a2f3-4501-8a5e-569a4cd411c1',
    'da4ef08a-68b1-4275-8546-9f993d076621',
    '87e8f9c6-7226-4f2d-b4c4-bc925891310f',
    '7fd3b095-3982-4e11-93fa-26b043deee13',
    'e9609ed6-1ed9-4420-98a4-b7447b1640c3',
    '933e8529-9cdd-4818-800c-70875511057a',
    '79200607-85b0-418e-bc3f-1605abfd123e',
    'faf23493-819e-40c6-a40e-a3c8faf771a1',
    '02b8a52d-7246-4d0e-8381-b080bd3dafc0',
    'a1f125d4-c02c-4853-929b-8dd8f3383381',
    'f6f96896-ebd1-4466-8f92-133f5c990dcd',
    '332084e6-7eda-4aaa-ad51-b612ac1aad8b',
    '15f4ce4a-7e4a-42e6-9a0a-dcf1d28344a0',
    '02b3c573-fa94-4f5c-b038-ca797a876750',
    '19f53db7-01de-425c-9fbc-eea864451115',
    '5409c493-5835-46f7-8ea1-99b0060b93cc',
    '519fe7e4-8da8-439e-9e78-b673154aa0c8',
    'd250441e-14ff-4673-a7a5-e6c41a2bf850',
    '506ecbf3-c095-466c-a8f9-bcdead3820ed',
    '19262b7c-6155-4f4c-b861-dc8584a7328d',
    '26b389ba-8c6f-4ef5-b674-0a68925ea764',
    'b7d1031f-ec00-4180-b1b5-f9c3fb71ff3d',
    '9609df4c-1870-4fc9-89fb-1d866581d75e',
    '3d62c9c6-627b-4dd0-a71a-651b6dff3589',
    '5cdf9c3f-beee-4c19-aed7-78cbaa0f3688',
    '85784112-628a-4021-9892-ec9bd8ec79cb',
    '30796c37-c758-479b-b305-8560e32855f4',
    '51fb5f7a-6a49-4586-9737-43727111c86d',
    '1c179546-b75b-40bd-b925-26707d1439b4',
    'f07b0c8f-5f54-4419-8ce7-e1f267a7aa81',
    '1c270538-a9f7-48bc-9688-c9b9bd2341c0',
    'b0afd31d-9703-4b73-a16e-8b9004a2d886',
    'b65ee9c0-959d-42f2-b3a4-acefac9c0e20',
    'fca61ab3-8460-49e1-9ac6-b696022d8647',
    '6697e0d6-181b-4910-acc4-54194b969c93',
    'ec7b3d3b-49d3-4f9e-8610-c626de90d9fb',
    '84ad01be-c40a-441f-b6c3-07ceb3806683',
    '03437094-bb15-4284-a06e-d12f1d239ed9',
    '2d6056e1-6df5-448f-b943-be801844af79',
    '5dcd1a4a-1dca-4a60-86a1-3d08570a6b50',
    '66a14929-1181-4a4d-acb4-cde2c457cf5f',
    '0ad16c91-dbac-4a80-9dbc-df5d651bcaf1',
    '94e20799-0831-444b-94af-808c4aac09bc',
    '2674f43e-f995-4c7f-ad8e-ff4ce3239937',
    '350f77e7-250c-4295-bd64-5a4344d4cc2b',
    '55eedeff-d02f-470e-ae65-26b8f8209723',
    'cf72c8a1-5e49-4196-832c-0f63245ae362',
    '891e79aa-8fcb-4422-986a-009fdfd77f5b',
    'c9014585-4ce0-466d-83bd-2569c351c52f',
    '6ff0d863-7ec0-410c-b32e-57c605f96223',
    'fc2f0f04-b700-497c-ae52-2360bc548686',
    '081c6ca9-2a29-48f7-8b96-5f48b2017b1e',
    '4bccb5dc-9912-4cd1-b63b-5e6f6d32fde4',
    '15753c08-f0ab-485e-87ee-72abbd4ff281',
    '7f2878fb-8d12-48d0-8446-185bce68f1c7',
    'adc2c9d2-a05a-419f-bb0d-6b56abcda5b6',
    '4c86acfd-3f0e-4d53-812b-f9e3e104ba54',
    '4ee445c5-e358-40cd-8940-ec7f2d2377ec',
    'e73d95e0-235a-424a-bea1-2c5455fe2e92',
    '548ab8c8-63e5-4b41-bb0a-c7ea315d178f',
    'ff6a7959-6e5a-4875-84a3-0c614d3a5d78',
    'b2f5401e-840f-4d04-962c-98e2a9111595',
    '9c8a3f0b-5f1b-420c-aeea-bbb824baed83',
    '41170380-5cd9-45e2-bb68-d10df75588d8',
    'ae9ef6b9-b15d-4ab9-b2f9-4b704e70b93b',
    '6df3af40-f860-4e1f-8875-18bbf03cecc1',
    'e70e9571-acff-4dc0-b7b8-ff6fdd2d6264',
    '34f555bd-2061-48dc-ac02-36b96fa8574c',
    '86af954f-64bd-4425-b43e-97e71ade45a2',
    'bc413584-cb5e-4b30-816f-d59b69a018ba',
    '7bbdd320-1e1b-493a-8e75-30cb0495d5d2',
    '1a9ff8a7-c852-4e20-95d4-83819a785b00',
    'e651692e-2a28-4877-9a5c-663b15ce192f',
    'ee42d077-b382-4747-a549-9a0b97ed5d2f',
    '45dcd02d-41e4-4edd-ae91-9bda1f3269f3',
    '96da8f9b-a65d-44ee-b28a-6ef8590d0fcc',
    '7cb05ee0-6715-4a3b-af1c-dd3674fa5801',
    '7511e25a-4da7-4948-b329-d8329c761135',
    'ec284430-1696-4ef6-924c-524d41f7162d',
    '67e97bb0-5413-4ddb-8b75-94255cf11c81',
    'ab496172-f1b1-4a71-9963-c0ba21cee019',
    '46cba636-d5ef-4cd9-9880-70f14cf7f74f',
    'd4369f3e-4fc7-4458-8fae-50a28cd5532b',
    '13b5aa88-712a-4fee-b1de-64d0fb2c4600',
    '44633a10-4297-45da-a8e5-87b4d325b8f7',
    '65b64bee-b216-492a-b31f-deecb8eec685',
    '0f22a4ea-6c1f-4869-b180-ac352d9cf638',
    '9c32bc03-f5c6-433e-9a6a-e1463c9b2024',
    '55abacf8-c24d-4c1d-a349-dfd933e809c6',
    '123cfe00-b755-453c-b14e-e60b02d6ccb8',
    'c34aea14-2d6d-4fdf-b4e3-66d099fe04b6',
    'ea4fe7d6-fa0c-4a08-80b1-e92b6de21b12',
    '2bcb3733-0204-405d-9ed0-be7ef6b4bcc2',
    '2bb38f34-bc2d-437a-a281-54e4ecac3a45',
    '9f421fac-6430-451f-b4d1-a56a7af9ffa4',
    'ae284775-285a-4d85-9621-89c325193080',
    'aa474e26-eff1-4c9b-bc41-1971cfd07f2a',
    '5d774c6b-f8df-49b4-8601-fabfde52e83c',
    '84262d5f-0466-4850-967d-c05e18c5ff89',
    'ef9409f8-a457-44cf-93c6-4c9b98634747',
    '3b9f0c5f-784d-4a76-9051-f0f669a57f94',
    'd6453638-6c37-4b9e-8555-75eeb0c59e4b',
    '99ac5134-fc17-4a67-9f68-783b5abea968',
    'b3f64fe1-45fe-4fa4-9126-cfcbe609a9be',
    'fb765c61-4f2c-4528-a57b-ac425bc17d53',
    '9cc28865-d23c-4b85-8bc2-c80769508e56',
    '0929f65f-f13d-4f5a-ad1f-5cea4b71d728',
    'f98b6310-52ae-47aa-9076-b8bd7464fe34',
    '407d8f0a-b935-4e33-9a47-64d22fe493a4',
    'd2000f89-00dd-43bc-9eac-ceef7d571c3d',
    '0a1b600a-25b1-49bb-840d-331f8ba3b7c3',
    '322f2358-e669-435e-b762-39ca2ca6480d',
    'cbe8cfa4-0fda-4f39-8b5e-c0960e78d1db',
    '1db7dc9e-c860-48ac-bef6-4f96b80a3219',
    '0aeb06a1-ff72-40b1-b1e8-79c119a2308b',
    '8d69b430-fb55-4bc6-8e21-22d35144302a',
    '962c8bed-2ab9-4400-889f-7cf9bfdee4d9',
    '3eb3bbc6-23be-41d2-a6a2-d4b0bfb3c30c',
    '9f176e41-35f8-43e3-9087-8b7f70a0499b',
    'b75cee29-dcf6-4cda-b125-f19489e9870c',
    'f602109d-ce74-4074-a251-5c13f74b7484',
    '2e88db2e-424d-420e-ad57-bbb77c5a7bb4',
    '80532303-4887-4465-8d85-980a4580c006',
    '55a5626f-3ce0-4665-aee7-da8b4d5cb7f7',
    '97f8bf79-9e59-4923-b716-8e3c39c11386',
    '0be1259a-bfb7-4946-8160-5bfcaca380b2'
]


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

def send_request(api):
    global successful_requests
    global sad
    global total_requests
    total_requests += 1

    payload = json.dumps({
        "model": "Meta-Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "user", "content": "Напиши короткий стих"}
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

    # Повторение запроса, если ответ пустой
    attempts = 0
    while not answer and attempts < 3:
        attempts += 1
        print(f"Пустой ответ от API, попытка {attempts}")
        response = requests.request("POST", url, headers=headers, data=payload)
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

    if not answer:  # Если ответ пустой после 3 попыток
        answer = "[0]"
        sad += 1
        print(f"Не удалось получить ответ от API после 3 попыток.")
    else:
        successful_requests += 1

    return answer

# Выполняем 1000 итераций
for i in range(1000):
    print(f"Итерация {i+1}:")
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(apis)) as executor:
        futures = {executor.submit(send_request, api): api for api in apis}
        for future in concurrent.futures.as_completed(futures):
            api_index = list(futures.keys()).index(future) + 1  # Получаем индекс API + 1
            try:
                answer = future.result()
                print(f"Ответ от API {api_index}: {answer}")
                worksheet.append([i+1, answer, api_index, 1])  # Записываем данные в Excel
            except Exception as e:
                print(f"Ошибка при запросе к API {api_index}: {e}")
                worksheet.append([i+1, f"Ошибка: {e}", api_index, 0])  # Записываем данные в Excel
    end_time = time.time()
    total_time += end_time - start_time
    print(f"Время выполнения итерации: {end_time - start_time} секунд\n")

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