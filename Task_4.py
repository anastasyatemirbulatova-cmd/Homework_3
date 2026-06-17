import sqlite3
from typing import List, Optional


# Подключение к базе данных (создаст файл db.sqlite3, если его нет)
conn = sqlite3.connect('clients.db')
cursor = conn.cursor()


def create_tables():
    """Создаёт таблицы для хранения информации о клиентах и их телефонах."""
    # Таблица клиентов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')

    # Таблица телефонов (связь «один ко многим»: один клиент — много телефонов)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            phone TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    conn.commit()

def add_client(first_name: str, last_name: str, email: str) -> int:
    """Добавляет нового клиента. Возвращает ID клиента."""
    try:
        cursor.execute(
            'INSERT INTO clients (first_name, last_name, email) VALUES (?, ?, ?)',
            (first_name, last_name, email)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Ошибка при добавлении клиента: {e}")
        return -1

def add_phone(client_id: int, phone: str) -> bool:
    """Добавляет телефон для существующего клиента. Возвращает True при успехе."""
    cursor.execute('SELECT id FROM clients WHERE id = ?', (client_id,))
    if cursor.fetchone() is None:
        print("Клиент с указанным ID не найден.")
        return False

    try:
        cursor.execute(
            'INSERT INTO phones (client_id, phone) VALUES (?, ?)',
            (client_id, phone)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Ошибка при добавлении телефона: {e}")
        return False

def update_client(client_id: int, first_name: Optional[str] = None,
                  last_name: Optional[str] = None, email: Optional[str] = None) -> bool:
    """Изменяет данные о клиенте. Возвращает True при успехе."""
    updates = []
    params = []

    if first_name is not None:
        updates.append("first_name = ?")
        params.append(first_name)
    if last_name is not None:
        updates.append("last_name = ?")
        params.append(last_name)
    if email is not None:
        updates.append("email = ?")
        params.append(email)

    if not updates:
        return False

    params.append(client_id)
    query = f"UPDATE clients SET {', '.join(updates)} WHERE id = ?"

    cursor.execute(query, params)
    conn.commit()
    return cursor.rowcount > 0

def delete_phone(client_id: int, phone: str) -> bool:
    """Удаляет телефон для существующего клиента. Возвращает True при успехе."""
    cursor.execute(
        'DELETE FROM phones WHERE client_id = ? AND phone = ?',
        (client_id, phone)
    )
    conn.commit()
    return cursor.rowcount > 0

def delete_client(client_id: int) -> bool:
    """Удаляет существующего клиента и все его телефоны. Возвращает True при успехе."""
    # Сначала удаляем телефоны
    cursor.execute('DELETE FROM phones WHERE client_id = ?', (client_id,))
    # Затем удаляем клиента
    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    return cursor.rowcount > 0

def find_client(search_term: str) -> List[dict]:
    """Находит клиента по имени, фамилии, email или телефону. Возвращает список найденных клиентов."""
    results = []

    # Поиск по имени, фамилии и email в таблице clients
    cursor.execute('''
        SELECT c.id, c.first_name, c.last_name, c.email
        FROM clients c
        WHERE c.first_name LIKE ? OR c.last_name LIKE ? OR c.email LIKE ?
    ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))

    for row in cursor.fetchall():
        client_id = row[0]
        # Получаем все телефоны клиента
        cursor.execute('SELECT phone FROM phones WHERE client_id = ?', (client_id,))
        phones = [p[0] for p in cursor.fetchall()]

        results.append({
            'id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'email': row[3],
            'phones': phones
        })

    # Поиск по телефону в таблице phones
    cursor.execute('''
        SELECT c.id, c.first_name, c.last_name, c.email, p.phone
        FROM clients c
        JOIN phones p ON c.id = p.client_id
        WHERE p.phone LIKE ?
    ''', (f'%{search_term}%',))

    for row in cursor.fetchall():
        client_id = row[0]
        if not any(client['id'] == client_id for client in results):
            # Получаем все телефоны клиента, чтобы не потерять остальные номера
            cursor.execute('SELECT phone FROM phones WHERE client_id = ?', (client_id,))
            phones = [p[0] for p in cursor.fetchall()]
            results.append({
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'phones': phones
            })

    return results

def display_clients():
    """Вспомогательная функция для отображения всех клиентов с их телефонами."""
    clients = find_client("")  # Пустая строка вернёт всех клиентов
    for client in clients:
        print(f"ID: {client['id']}")
        print(f"Имя: {client['first_name']}")
        print(f"Фамилия: {client['last_name']}")
        print(f"Email: {client['email']}")
        print(f"Телефоны: {', '.join(client['phones']) if client['phones'] else 'нет телефонов'}")
        print("-" * 40)

# Демонстрация работы функций
if __name__ == "__main__":
    # Создаём таблицы
    create_tables()

    print("=== Добавление клиентов ===")
    client1_id = add_client("Иван", "Иванов", "ivan@example.com")
    client2_id = add_client("Пётр", "Петров", "petr@example.com")

    print(f"Добавлен клиент с ID: {client1_id}")
    print(f"Добавлен клиент с ID: {client2_id}")

    print("\n=== Добавление телефонов ===")
    add_phone(client1_id, "+7-999-123-45-67")
    add_phone(client1_id, "+7-999-765-43-21")
    add_phone(client2_id, "+7-988-111-22-33")

    print("Телефоны добавлены.")

    print("\n=== Отображение всех клиентов ===")
    display_clients()

    print("\n=== Изменение данных клиента ===")
    update_client(client1_id, first_name="Иван", last_name="Сидоров")
    print("Данные клиента обновлены.")

    print("\n=== Поиск клиента ===")
    found_clients = find_client("Сидоров")
    for client in found_clients:
        print(f"Найден клиент: {client['first_name']} {client['last_name']}, Email: {client['email']}, Телефоны: {', '.join(client['phones'])}")

    print("\n=== Удаление телефона ===")
    delete_phone(client1_id, "+7-999-765-43-21")
    print("Телефон удалён.")

    print("\n=== Удаление клиента ===")