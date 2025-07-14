from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import uuid
import re
import traceback
import os

# Настройка headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)  # Ждёт до 5 секунд при поиске элемента

BASE_URL = "http://localhost:8080"

unique = str(uuid.uuid4())[:4]
email = f"test_{unique}@test"
name = f"test_{unique}"
password = "Test123!"

print("Test values:")
print(f"name: {name}")
print(f"email: {email}")
print(f"password: {password}\n")

def test_register_and_login():
    # Регистрация
    driver.get(f"{BASE_URL}/register")
    WebDriverWait(driver, 10).until(EC.url_contains("/register"))
    
    driver.find_element(By.ID, "regUsername").send_keys(name)
    driver.find_element(By.ID, "regEmail").send_keys(email)
    driver.find_element(By.ID, "regPassword").send_keys(password)
    driver.find_element(By.ID, "btnRegister").click()
    
    WebDriverWait(driver, 10).until(EC.url_contains("/login"))

    # Переход на логин
    driver.find_element(By.ID, "loginUsername").send_keys(name)
    driver.find_element(By.ID, "loginPassword").send_keys(password)
    driver.find_element(By.ID, "btnLogin").click()
    time.sleep(2)

    WebDriverWait(driver, 10).until(EC.url_contains("/puzzles"))
    assert "/puzzles" in driver.current_url

def test_edit_profile(test_avatar_path, test_cert_path):
    # Открываем страницу профиля
    driver.get(f"{BASE_URL}/profile")
    time.sleep(1)

    # === Изменение описания профиля ===
    driver.find_element(By.ID, "edit-profile-btn").click()
    time.sleep(1)

    bio_input = driver.find_element(By.ID, "bio-textarea")
    new_bio = "Тестовое описание профиля"
    bio_input.clear()
    bio_input.send_keys(new_bio)

    # === Загрузка аватара ===
    avatar_input = driver.find_element(By.ID, "avatar-input")  # input type="file"
    avatar_input.send_keys(os.path.abspath(test_avatar_path))  # Путь до тестового изображения
    time.sleep(1)

    from pdf import generate_PDF
    generate_PDF(name)
    from main import sign_pdf
    sign_pdf()

    # === Загрузка сертификата ===
    cert_input = driver.find_element(By.ID, "certificate-input-edit")  # input type="file"
    cert_input.send_keys(os.path.abspath(test_cert_path))  # Путь до PDF-файла
    time.sleep(1)

    driver.find_element(By.ID, "save-all-btn").click()
    time.sleep(1)

    # Проверка — биография обновлена (по желанию)
    updated_bio = driver.find_element(By.ID, "profile-bio").text
    assert updated_bio == new_bio, f"Биография не обновилась! {updated_bio}"

def test_create_news_post():
    # Переход на страницу новостей
    driver.get(f"{BASE_URL}/news")
    time.sleep(1)

    content = "Тестовая новость " + str(uuid.uuid4())[:8]
    textarea = driver.find_element(By.ID, "news-content")
    textarea.clear()
    textarea.send_keys(content)

    driver.find_element(By.ID, "submit-post").click()
    time.sleep(1)

    posts = driver.find_elements(By.CLASS_NAME, "news-post-content")
    assert any(content in post.text for post in posts)

def test_send_msg_in_chat():
    driver.get(f"{BASE_URL}/chat")
    time.sleep(1)

    content = "Тестовое сообщение" + str(uuid.uuid4())[:8]
    textarea = driver.find_element(By.ID, "message-input")
    textarea.clear()
    textarea.send_keys(content)

    driver.find_element(By.ID, "send-button").click()
    time.sleep(1)

    msgs = driver.find_elements(By.ID, "chat-messages")
    assert any(content in msg.text for msg in msgs)

def test_users_list():
    driver.get(f"{BASE_URL}/users")
    time.sleep(1)

    # Ждём появления хотя бы одной строки
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#users-list tr"))
    )

    # Находим все строки
    rows = driver.find_elements(By.CSS_SELECTOR, "#users-list tr")

    names = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            names.append(cols[1].text)

    assert name in names

def test_puzzles():
    driver.get(f"{BASE_URL}/create_puzzle")
    time.sleep(1)

    content = "Тестовый пазл " + str(uuid.uuid4())[:8]
    textarea = driver.find_element(By.ID, "title")
    textarea.clear()
    textarea.send_keys(content)
    time.sleep(1)

    FEN = "6k1/5ppp/8/8/8/8/5PPP/6K1 w - - 0 1"
    textarea = driver.find_element(By.ID, "fen")
    textarea.clear()
    textarea.send_keys(FEN)
    time.sleep(1)

    ans = "Тестовый ответ " + str(uuid.uuid4())[:8]
    textarea = driver.find_element(By.ID, "answer")
    textarea.clear()
    textarea.send_keys(ans)
    time.sleep(1)

    prize = "Тестовый приз " + str(uuid.uuid4())[:8]
    textarea = driver.find_element(By.ID, "prize")
    textarea.clear()
    textarea.send_keys(prize)
    time.sleep(1)

    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(1)

    msg = driver.find_element(By.ID, "result").text
    match = re.search(r'ID: (\w+)', msg)
    if match:
        puzzle_id = match.group(1)
    else:
        raise Exception("ID не найден в сообщении")

    driver.get(f"{BASE_URL}/my_puzzles")
    time.sleep(1)

    # Ждём появления хотя бы одной строки
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#my-puzzles-table tr"))
    )

    # Находим все строки
    rows = driver.find_elements(By.CSS_SELECTOR, "#my-puzzles-table tr")

    # Извлекаем значения первого столбца (ID)
    ids = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            ids.append(cols[0].text)

    # Например, проверим, что нужный ID есть
    assert puzzle_id in ids

    driver.get(f"{BASE_URL}/puzzles")
    time.sleep(1)

    # Ждём появления хотя бы одной строки
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#puzzles-list tr"))
    )

    # Находим все строки
    rows = driver.find_elements(By.CSS_SELECTOR, "#puzzles-list tr")

    # Извлекаем значения первого столбца (ID)
    p_ids = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            p_ids.append(cols[0].text)

    # Например, проверим, что нужный ID есть
    assert puzzle_id in p_ids

    driver.get(f"{BASE_URL}/search")
    time.sleep(1)

    search_input = driver.find_element(By.ID, "search-input")
    search_input.clear()
    search_input.send_keys(content)

    driver.find_element(By.ID, "search-button").click()
    time.sleep(1)

    # Ждём появления хотя бы одной строки
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#puzzles-list tr"))
    )

    # Находим все строки
    rows = driver.find_elements(By.CSS_SELECTOR, "#puzzles-list tr")

    # Извлекаем значения первого столбца (ID)
    s_ids = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            s_ids.append(cols[0].text)

    # Например, проверим, что нужный ID есть
    assert puzzle_id in s_ids
    assert puzzle_id in p_ids
    assert puzzle_id in ids

def test_create_game():
    driver.get(f"{BASE_URL}/create_game")
    time.sleep(1)

    content = "Тестовый приз" + str(uuid.uuid4())[:8]
    textarea = driver.find_element(By.ID, "prize")
    textarea.clear()
    textarea.send_keys(content)
    time.sleep(1)

    select_elem = Select(driver.find_element(By.ID, "engine"))
    select_elem.select_by_value("script.sh")

    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(1)

    msg1 = driver.find_element(By.ID, "result").text
    match = re.search(r'ID: (\w+)', msg1)
    if match:
        game1_id = match.group(1)
    else:
        raise Exception("ID не найден в сообщении")

    textarea.clear()
    textarea.send_keys(content)
    select_elem.select_by_value("stockfish.sh")

    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(1)

    msg2 = driver.find_element(By.ID, "result").text
    match = re.search(r'ID: (\w+)', msg2)
    if match:
        game2_id = match.group(1)
    else:
        raise Exception("ID не найден в сообщении")

    driver.get(f"{BASE_URL}/my_games")
    time.sleep(1)

    # Ждём появления хотя бы одной строки
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#games-list tr"))
    )

    # Находим все строки
    rows = driver.find_elements(By.CSS_SELECTOR, "#games-list tr")

    # Извлекаем значения первого столбца (ID)
    ids = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            ids.append(cols[0].text)

    # Например, проверим, что нужный ID есть
    assert (game1_id in ids) and (game2_id in ids)

def test_create_note():
    driver.get(f"{BASE_URL}/notes")
    WebDriverWait(driver, 10).until(EC.url_contains("/notes"))

    content = "Тестовая заметка " + str(uuid.uuid4())[:8]
    textarea = driver.find_element(By.ID, "new-note-content")
    textarea.clear()
    textarea.send_keys(content)

    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(1)

    notes = driver.find_elements(By.CLASS_NAME, "note-content")

    WebDriverWait(driver, 10).until(
    lambda d: any(note.text.strip() for note in d.find_elements(By.CLASS_NAME, "note-content"))
    )

    assert any(content in note.text for note in notes)

if __name__ == "__main__":
    try:
        print("Test started")
        test_register_and_login()
        print("register and login: passed ✅")
        test_edit_profile("avatar.jpg", "signed.pdf")
        print("profile: passed ✅")
        test_create_news_post()
        print("news: passed ✅")
        test_create_note()
        print("notes: passed ✅")
        test_send_msg_in_chat()
        print("chat: passed ✅")
        test_users_list()
        print("users list: passed ✅")
        test_create_game()
        print("games: passed ✅")
        test_puzzles()
        print("puzzles: passed ✅")
        print("✅ Все тесты прошли успешно.")
    except Exception as e:
        print("❌ Ошибка в тестах:", e)
        traceback.print_exc()
    finally:
        driver.quit()