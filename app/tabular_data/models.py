import os

from sqlalchemy.event import listens_for

from app import db
from app.base_abstracts import ParentAbstract

"""
    This is the models.py file for the tabular_data blueprint.
    it contains the following tables:
    - TabularDataFile: This table stores the information about the tabular data files uploaded by the user.
    - TabularDataFileHeader: This table stores the information about the headers
        of the tabular data files uploaded by the user.
    - TabularDataFileRow: This table stores the information about the rows of the
        tabular data files uploaded by the user.
"""


class TabularDataFile(ParentAbstract):
    """
    This table stores the information about the tabular data files uploaded by the user.
    """

    __tablename__ = "tabular_data_files"

    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    statistics = db.Column(db.JSON)

    headers = db.relationship(
        "TabularDataFileHeader", backref=db.backref("tabular_data_file", lazy=True), cascade="all, delete"
    )
    rows = db.relationship(
        "TabularDataFileRow", backref=db.backref("tabular_data_file", lazy=True), cascade="all, delete"
    )

    def __repr__(self):
        return f"<TabularDataFile {self.id} {self.name}>"


class TabularDataFileHeader(ParentAbstract):
    """
    This table stores the information about the headers of the tabular data files uploaded by the user.
    """

    __tablename__ = "tabular_data_file_headers"

    tabular_data_file_id = db.Column(db.Integer, db.ForeignKey("tabular_data_files.id"), nullable=False)
    header = db.Column(db.String(255))
    index = db.Column(db.Integer)

    # tabular_data_file = db.relationship('TabularDataFile', backref=db.backref('headers', lazy=True))

    def __repr__(self):
        return f"<TabularDataFileHeader {self.id} {self.header} - {self.tabular_data_file}>"


class TabularDataFileRow(ParentAbstract):
    """
    This table stores the information about the rows of the tabular data files uploaded by the user.

        will store the row data as a JSON object key-value pair.
        the key will be the header id and the value will be the row value.
    """

    __tablename__ = "tabular_data_file_rows"

    tabular_data_file_id = db.Column(db.Integer, db.ForeignKey("tabular_data_files.id"), nullable=False)
    row_data = db.Column(db.JSON)
    index = db.Column(db.Integer)

    # tabular_data_file = db.relationship('TabularDataFile', backref=db.backref('rows', lazy=True))

    def __repr__(self):
        return f"<TabularDataFileRow {self.id} - size: {len(self.row_data)} - {self.tabular_data_file}>"


@listens_for(TabularDataFile, "after_delete")
def delete_tabular_data_file(mapper, connection, target):

    if os.path.exists(target.path):
        os.remove(target.path)
