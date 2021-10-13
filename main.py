import os, io
from google.cloud import vision_v1
from numpy import random
from pillow_utillity import draw_borders, Image
import pandas as pd
from google.cloud.vision_v1 import types
import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='root',
    # Connect to created database after we created it
    database='testdatabase'
)
mycursor = db.cursor()

# Create Database (only ones)
# mycursor.execute("CREATE DATABASE testdatabase")
# Create Table content only ones (we will have object's name, score and ID as a primary key)
# mycursor.execute("CREATE TABLE Object(name VARCHAR(50), score float UNSIGNED, objectID int PRIMARY KEY AUTO_INCREMENT)")

# Show Table
# mycursor.execute("DESCRIBE Object")
# for x in mycursor:
#     print(x)


# Google Vision API connection using KEY
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"key.json"
client = vision_v1.ImageAnnotatorClient()

# Picking image
file_name = 'canoe_water_nature_221611.jpg'
image_path = os.path.join('.\Images', file_name)

with io.open(image_path, 'rb') as image_file:
    content = image_file.read()

image = vision_v1.types.Image(content=content)
response = client.object_localization(
        image=image)
localized_object_annotations = response.localized_object_annotations

df = pd.DataFrame(columns=['name', 'score'])
for obj in localized_object_annotations:
    df = df.append(dict(name=obj.name, score=obj.score), ignore_index=True)

pillow_image = Image.open(image_path)
indx = 0
for obj in localized_object_annotations:
    r, g, b = random.randint(150, 255), random.randint(150, 255), random.randint(150, 255)
    draw_borders(pillow_image, obj.bounding_poly, (r, g, b), pillow_image.size, obj.name, obj.score)
    # Insert to database all founded objects. Float and round is to have a right type for mysql
    mycursor.execute("INSERT INTO Object (name, score) VALUES (%s, %s)", (df.name[indx], float(round(df.score[indx], 2))))
    db.commit()
    indx = indx + 1

pillow_image.show()

# Show Table's objects
# mycursor.execute("SELECT * FROM Object")
# for x in mycursor:
#     print(x)

