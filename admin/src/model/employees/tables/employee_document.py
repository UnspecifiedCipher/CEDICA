
from src.model.database import db

class EmployeeDocument(db.Model):
    __tablename__ = 'employee_documents'
    employee_id = db.Column(db.BigInteger, db.ForeignKey('employees.id'), primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), primary_key=True)
    employee = db.relationship("Employee", back_populates="employee_documents")
    document = db.relationship("Document", backref="employee_documents")

    def __init__(self, employee, document):
        self.employee = employee
        self.document = document
