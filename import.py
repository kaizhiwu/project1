import csv, os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    # Open a file using Python's CSV reader.
    f = open("zips.csv")
    reader = csv.reader(f)

    # Iterate over the rows of the opened CSV file.
    for row in reader:

        # Execute database queries, one per row; then print out confirmation.
        db.execute("INSERT INTO zip_codes (zipcode, city, state, lat, long, population) VALUES (:x, :y, :z, :a, :b, :c)",
                    {"x": row[0], "y": row[1], "z": row[2], "a": row[3], "b": row[4], "c": row[5]})

    # Technically this is when all of the queries we've made happen!
    db.commit()

if __name__ == "__main__":
    main()
