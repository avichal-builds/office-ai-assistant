
import pandas as pd


def read_employee_data(file_path: str):
    df = pd.read_excel(file_path)

    return df.to_dict(orient="records")


def find_employee_by_name(file_path: str, name: str):
    employees = read_employee_data(file_path)

    search_name = name.strip().lower()

    for employee in employees:
        employee_name = str(employee["name"]).strip().lower()

        if employee_name == search_name:
            return employee

    return None


if __name__ == "__main__":

    employees = read_employee_data(
        "data/sample_employees/employees.xlsx"
    )

    print("All Employees:")

    for employee in employees:
        print(employee)

    print("\nEmployee Search:")

    result = find_employee_by_name(
        "data/sample_employees/employees.xlsx",
        "Avichal"
    )

    print(result)
