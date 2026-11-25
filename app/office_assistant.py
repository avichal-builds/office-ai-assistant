from app.readers.excel_reader import read_employee_data
from app.services.ai_service import ask_ai
from app.readers.excel_reader import find_employee_by_name

EMPLOYEE_FILE = "data/sample_employees/employees.xlsx"


def extract_employee_name(question: str, employees: list):
    question = question.lower()

    for employee in employees:
        employee_name = employee["name"].strip().lower()

        if employee_name in question:
            return employee["name"]

    return None


def ask_office_assistant(question: str):

    employees = read_employee_data(EMPLOYEE_FILE)

    employee_context = ""

    for employee in employees:
        employee_context += (
            f"Employee: {employee['name']}\n"
            f"Department: {employee['department']}\n"
            f"Designation: {employee['designation']}\n"
            f"Salary: {employee['salary']}\n"
            f"Joining Date: {employee['joining_date']}\n\n"
        )

    prompt = f"""
    You are a company Office AI Assistant.

    Answer questions using ONLY the employee data below.

    If information is unavailable, clearly say so.
    Never invent employee information.

    EMPLOYEE DATA:
    {employee_context}

    USER QUESTION:
    {question}
    """

    return ask_ai(prompt)


if __name__ == "__main__":

    question = input("Ask Office AI: ")

    answer = ask_office_assistant(question)

    print("\nOffice AI Answer:")
    print(answer)
