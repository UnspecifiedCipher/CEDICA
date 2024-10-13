from src.model.database import db
from src.model.auth.tables.user import User
from src.model.employees.tables.employee import Employee
from src.model.auth.tables.role import Role
from sqlalchemy.orm  import Query
from typing import List, Optional


def create_employee(name: str, surname: str, dni: int, address: str, email: str, locality: str, phone: str, profession_id: int, job_position_id: int, emergency_contact_name: str, emergency_contact_phone: str, obra_social: str, affiliate_number: str, is_volunteer: bool, enabled: bool = True) -> Employee:
    employee = Employee(name, surname, dni, address, email, locality, phone, profession_id, job_position_id, emergency_contact_name, emergency_contact_phone, obra_social, affiliate_number, is_volunteer, enabled)
    db.session.add(employee)
    db.session.commit()
    db.session.expunge(employee)
    return employee

def list_employees():   # lista TODOS los employees (solo usar cuando sea estrictamente necesario)
    employees = Employee.query.all()
    [db.session.expunge(employee) for employee in employees.items]
    return employees # puede devolver una lista vacia

def get_employee(id: int):      #devuelve un employee dado un id
    employee = Employee.query.get(id)
    db.session.expunge(employee)
    return employee # si no encuentra nada devuelve None

def get_employee_by_email(email: str):      #devuelve un employee dado un email (el email es unico)
    employee = Employee.query.filter(Employee.email == email).first()
    db.session.expunge(Employee)
    return employee # si no encuentra nada devuelve None

def __update_employee__(to_update: Employee) -> Employee:
    employee = Employee.query.get(to_update.id)
    if employee is None:
        raise ValueError("No se encontro un empleado con ese ID")
    employee.name = to_update.name or employee.name
    employee.surname = to_update.surname or employee.surname
    employee.dni = to_update.dni or employee.dni
    employee.address = to_update.address or employee.address
    employee.email= to_update.email or employee.email
    employee.locality = to_update.locality or employee.locality
    employee.phone = to_update.phone or employee.phone
    employee.profession_id = to_update.profession_id or employee.profession_id
    employee.job_position_id = to_update.job_position_id or employee.job_position_id
    employee.emergency_contact_name = to_update.emergency_contact_name or employee.emergency_contact_name
    employee.emergency_contact_phone = to_update.emergency_contact_phone or employee.emergency_contact_phone
    employee.obra_social = to_update.obra_social or employee.obra_social
    employee.affiliate_number = to_update.affiliate_number or employee.affiliate_number
    employee.is_volunteer = to_update.is_volunteer if to_update.is_volunteer is not None else employee.is_volunteer
    employee.enabled = to_update.enabled if to_update.enabled is not None else employee.enabled
    db.session.commit()
    db.session.expunge(employee)
    return employee

def delete_employee(id: int):   # creo que no hace falta excepcion aca
    employee = Employee.query.get(id)
    if employee is None:
        raise ValueError("No se encontro un emplead con ese ID")
    db.session.delete(employee)
    db.session.commit()

###INSTRUCCIONES DE UPDATE ESPECÍFICAS

def toggle_block(id: int) -> Employee:      # cambiar el estado de "enabled"
    employee = Employee.query.get(id)
    if employee is None:
        raise ValueError("No se encontro un empleado con ese ID") 
    employee.enabled = not employee.enabled
    db.session.commit()
    db.session.expunge(employee)
    return employee

def toggle_is_volunteer(id: int) -> Employee:       # cambiar el estado de "is_volunteer"
    employee = Employee.query.get(id)
    if employee is None:
        raise ValueError("No se encontro un empleado con ese ID")
    employee.is_volunteer = not employee.is_volunteer
    db.session.commit()
    db.session.expunge(employee)
    return employee

###INSTRUCCIONES DE LISTADO ESPECÍFICAS

# Ordena por un atributo específico (email por defecto)
def sorted_by_attribute(employees: Query, attribute: str = "email", ascending: bool = True) -> Query:
    return employees.order_by(getattr(Employee, attribute).asc() if ascending else getattr(Employee, attribute).desc())

# Filtra empleados activos/inactivos
def filter_active(employees: Query, show_enabled: bool = True, show_disabled: bool = True) -> Query:
    # Si ambos son True, no aplica filtro, muestra todos
    if show_enabled and show_disabled:
        return employees
    # Filtra solo empleados habilitados o deshabilitados
    return employees.filter(Employee.activo == show_enabled)

# Búsqueda por email
def search_by_mail(employees: Query, email: str = "") -> Query:
    if email:
        return employees.filter(Employee.email.ilike(f"%{email}%"))
    return employees

# Búsqueda por nombre
def search_by_name(employees: Query, name: str = "") -> Query:
    if name:
        return employees.filter(Employee.nombre.ilike(f"%{name}%"))
    return employees

# Búsqueda por apellido
def search_by_surname(employees: Query, surname: str = "") -> Query:
    if surname:
        return employees.filter(Employee.apellido.ilike(f"%{surname}%"))
    return employees

# Búsqueda por profesión
def search_by_profession(employees: Query, profession: str = "") -> Query:
    if profession:
        return employees.filter(Employee.profession.name.ilike(f"%{profession}%"))
    return employees

# Función final que combina los filtros y búsquedas
def get_employees_filtered_list(page: int,
                                limit: int = 25,
                                show_enabled: bool = True,
                                show_disabled: bool = True,
                                sort_attr: str = "email",
                                ascending: bool = True,
                                search_mail: str = "",
                                search_name: str = "",
                                search_surname: str = "",
                                search_profession: str = "") -> Query:
    # Inicia la consulta con Employee
    employees = Employee.query
    
    # Aplica los filtros y búsquedas
    employees = filter_active(employees, show_enabled, show_disabled)
    employees = search_by_mail(employees, search_mail)
    employees = search_by_name(employees, search_name)
    employees = search_by_surname(employees, search_surname)
    employees = search_by_profession(employees, search_profession)
    
    # Ordena los resultados
    employees = sorted_by_attribute(employees, sort_attr, ascending)
    
    # Pagina los resultados
    employee_list = employees.paginate(page=page, per_page=limit, error_out=False)
    
    # Expulsa los objetos de la sesión
    [db.session.expunge(employee) for employee in employee_list.items]
    
    return employee_list