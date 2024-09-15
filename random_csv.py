import csv
import datetime
import random


def generate_random_data(num_rows):
    data = []
    for _ in range(num_rows):
        name = random.choice(["Alice", "Bob", "Charlie", "David", "Eve"])
        age = random.randint(18, 65)
        city = random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])
        salary = round(random.uniform(30000, 100000), 2)
        date = datetime.datetime.now() + datetime.timedelta(days=random.randint(-365, 365))
        years_experience = random.randint(1, 15)
        iq = random.randint(80, 140)
        height = round(random.uniform(60, 75), 1)
        weight = round(random.uniform(100, 250), 1)
        income = round(random.uniform(20000, 100000), 2)

        row = {
            "ID": random.randint(1, 1000),
            "Name": name,
            "Age": age,
            "City": city,
            "Salary": salary,
            "Date": date.strftime("%Y-%m-%d %H:%M:%S"),
            "YearsExperience": years_experience,
            "IQ": iq,
            "Height": height,
            "Weight": weight,
            "Income": income,
        }
        data.append(row)
    return data


def write_csv(data, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = [
            "ID",
            "Name",
            "Age",
            "City",
            "Salary",
            "Date",
            "YearsExperience",
            "IQ",
            "Height",
            "Weight",
            "Income",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    num_rows = 100
    data = generate_random_data(num_rows)
    filename = "random_data.csv"
    write_csv(data, filename)
    print(f"CSV file created: {filename}")
