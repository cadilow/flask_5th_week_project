import csv

from models import db, Dish


with open('csv/meals.csv') as f:
    i = 0
    reader = csv.reader(f)
    for row in reader:
        if i == 0:
            i += 1
            continue
        print(row)
        dish = Dish(
            title=row[1],
            price=row[2],
            description=row[3],
            picture=row[4],
            category=row[5]
        )
        db.session.add(dish)
    db.session.commit()