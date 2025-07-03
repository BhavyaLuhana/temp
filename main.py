from flask import Flask, render_template, request, redirect, url_for, flash
import cv2
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'babvbebfananbae15v1adv'

PHOTOS_DIR = 'photos'
CSV_FILE = 'users.csv'
os.makedirs(PHOTOS_DIR, exist_ok=True)

def load_users():
    if not os.path.isfile(CSV_FILE):
        return []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader if 'Photo' in row and row['Photo']]

def save_user(name, phone, photo_filename):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Name', 'Phone', 'Photo'])
        writer.writerow([name, phone, photo_filename])

def write_all_users(users):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Phone', 'Photo'])
        writer.writeheader()
        writer.writerows(users)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']

        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()

        if ret:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}.jpg"
            path = os.path.join(PHOTOS_DIR, filename)
            cv2.imwrite(path, frame)

            save_user(name, phone, filename)
            flash(f"User {name} added successfully!")
            return redirect(url_for('index'))
        else:
            return "Webcam not accessible", 500

    return render_template('index.html')

@app.route('/users')
def users():
    all_users = load_users()
    print("Loaded users:")
    for user in all_users:
        print(user)
    return render_template('users.html', users=all_users)

@app.route('/delete/<photo>')
def delete(photo):
    users = load_users()
    updated_users = [user for user in users if user['Photo'] != photo]

    # Delete image
    photo_path = os.path.join(PHOTOS_DIR, photo)
    if os.path.exists(photo_path):
        os.remove(photo_path)

    # Save updated CSV
    write_all_users(updated_users)

    return redirect(url_for('users'))

if __name__ == '__main__':
    app.run(debug=True)
