import csv

def save_to_csv(user_id, name, experience, level, registration_date):
    with open('data/users.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, name, experience, level, registration_date])