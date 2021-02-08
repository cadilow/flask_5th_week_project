import csv

from app import db, Dish, Category


with open('csv/meals.csv') as f:
    i = 0
    reader = csv.reader(f)
    for row in reader:
        if i == 0:
            i += 1
            continue
        category = db.session.query(Category).filter(Category.category_id == row[5]).first()
        dish = Dish(
            title=row[1],
            price=row[2],
            description=row[3],
            picture=row[4],
            category=category
        )
        db.session.add(dish)
    db.session.commit()