import csv


from app import db, Category

with open('csv/categories.csv') as f:
    i = 0
    reader = csv.reader(f)
    for row in reader:
        """if i == 0:
            i += 1
            continue"""
        category = Category(
            title=row[1],
            category_id=row[0]
        )
        db.session.add(category)
    db.session.commit()