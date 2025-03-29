import csv

def get_user_experience(user_id: int) -> str:
    try:
        with open('data/users.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['user_id']) == user_id:
                    return row['training_level']
        return "новичок"  # Значение по умолчанию, если пользователь не найден
    except FileNotFoundError:
        return "новичок"  # Если файл не найден
