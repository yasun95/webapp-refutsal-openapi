from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class REFUTSAL_COURT_TABLE(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    COURT_UUID = db.Column(db.String(16), nullable=False)
    COURT_NAME = db.Column(db.String(64), nullable=False)
    COURT_NO = db.Column(db.Integer, nullable=True, default=None)
    COURT_ADDRESS = db.Column(db.String(64), nullable=False)
    COURT_CONTACT = db.Column(db.String(64), nullable=False)
    COURT_AUX_INFO = db.Column(db.Text, nullable=False, default='')

class REFUTSAL_MATCH_TABLE(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    MATCH_UUID = db.Column(db.String(10), nullable=False)
    MATCH_COURT_UUID = db.Column(db.String(10), nullable=False)
    MATCH_COURT_NAME = db.Column(db.String(10), nullable=True, default=None)
    MATCH_COURT_NO = db.Column(db.String(10), nullable=False)
    MATCH_BEGIN = db.Column(db.String(10), nullable=False)
    MATCH_UNTIL = db.Column(db.String(10), nullable=False, default='')

class REFUTSAL_REPORT_TABLE(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    MATCH_UUID = db.Column(db.String(10), nullable=False)
    CREATED_AT = db.Column(db.String(10), nullable=False)
    LAST_EDITED_AT = db.Column(db.String(10), nullable=True, default=None)
    IS_DELETE = db.Column(db.String(10), nullable=False, default=0)
    LEFT_COLUMN_TEAM_COLOR = db.Column(db.String(10), nullable=False)
    RIGHT_COLUMN_TEAM_COLOR = db.Column(db.String(10), nullable=False)
    LEFT_COLUMN_TEAM_SCORE = db.Column(db.Integer, nullable=False)
    RIGHT_COLUMN_TEAM_SCORE = db.Column(db.Integer, nullable=False)
    REPORT_AUX_INFO = db.Column(db.String(100), nullable=False)

class REFUTSAL_TAG_TABLE(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    MATCH_UUID = db.Column(db.String(10), nullable=False)
    CREATED_AT = db.Column(db.String(10), nullable=False, default=False)
    LAST_EDITED_AT = db.Column(db.String(10), nullable=True, default=False)
    IS_DELETE = db.Column(db.String(10), nullable=False, default=0)
    GOAL_TAG = db.Column(db.String(10), nullable=False, default='') 