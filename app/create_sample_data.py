import pandas as pd
from pathlib import Path

data = [
    {
        "employee_id": 101,
        "name": "Avichal",
        "department": "Development",
        "designation": "Magento Developer",
        "salary": 50000,
        "joining_date": "2023-05-10"
    },
    {
        "employee_id": 102,
        "name": "Rahul",
        "department": "Marketing",
        "designation": "Marketing Executive",
        "salary": 40000,
        "joining_date": "2024-01-15"
    },
    {
        "employee_id": 103,
        "name": "Priya",
        "department": "HR",
        "designation": "HR Executive",
        "salary": 45000,
        "joining_date": "2022-08-20"
    }
]

df = pd.DataFrame(data)

folder = Path("data/sample_employees")
folder.mkdir(parents=True, exist_ok=True)

file_path = folder / "employees.xlsx"

df.to_excel(file_path, index=False)

print(f"Employee data created: {file_path}")
