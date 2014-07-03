#from datetime import datetime
from flask_login import make_secure_token, UserMixin
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from tap.database import Base
from uuid import uuid4

# association table(s)
opportunity_provider = Table('opportunity_provider', Base.metadata,
    Column('opportunity_id', Integer, ForeignKey('opportunity.id'), nullable=False),
    Column('provider_id', Integer, ForeignKey('provider.id'), nullable=False))

# ORM classes

# upon creation, contributor gets an 'associated' row here (unless contributor opts for earned/applied)
# bulk creation should give the option to set association, or null
# we should present provider associations programmatically, rather than in-SQL, like a tag
class Association(Base):
    __tablename__ = 'association'
    opportunity_id = Column(Integer, ForeignKey('opportunity.id'), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, primary_key=True)
    type = Column(Enum('associated', 'applied', 'earned'), nullable=False)

# class Note(Base) # or something like it
# class Tag(Base) # or something like it
# class Flag(Base) # or something like it
#    type = Column(Enum('inappropriate', 'needs attention'), nullable=False)
# class Interest(Base) # or something like it for tracking what each user is interested in

# include user data in response
class Opportunity(Base):
    __tablename__ = 'opportunity'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(Enum('current', 'archive', 'deleted'), nullable=False, default='current')
    contributor = Column(Integer, ForeignKey('user.id'), nullable=False)
    trail = Column(String(50), nullable=False, default=func.uuid())
    url = Column(String(200), nullable=True)
    # will always second order sort by amount
    amount = Column(Float, nullable=True)
    amount_per = Column(Enum('onetime', 'degree', 'year', 'semester', 'season', 'month', 'week', 'day', 'hour', 'other'), nullable=False)
    note = Column(Text, nullable=True)
    providers = relationship('Provider', secondary=opportunity_provider, backref='opportunities')
    associations = relationship('Association', backref='opportunities')
    created_at = Column(DateTime, nullable=False, default=func.now())
    modified_at = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self):
        return '<Opportunity %r>' % (self.id)

class Provider(Base):
    __tablename__ = 'provider'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(Enum('current', 'archive', 'deleted'), nullable=False, default='current')
    contributor = Column(Integer, ForeignKey('user.id'), nullable=False)
    trail = Column(String(50), nullable=False, default=func.uuid())
    url = Column(String(200), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    modified_at = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self):
        return '<Provider %r>' % (self.id)

class Session(Base, UserMixin):
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    #expires_at = Column(DateTime, nullable=False)
    token = Column(String(50), nullable=False, unique=True, default=uuid4())
    created_at = Column(DateTime, nullable=False, default=func.now())
    modified_at = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self):
        return '<Session %r>' % (self.id)

# include opportunity associations in response
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(30), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    # admin: can edit/delete all opportunities
    # contributor: can create opportunities, and edit own opportunities
    # possibly add guest: can view only
    type = Column(Enum('admin', 'contributor'), nullable=False)
    password = Column(String(100), nullable=False)
    # what about affiliation: staff/student/alumni/faculty, and grad year
    sessions = relationship('Session', backref='user')
    created_at = Column(DateTime, nullable=False, default=func.now())
    modified_at = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self):
        return '<User %r>' % (self.id)

    def is_active(self):
        return self.enabled

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        if self.username == None:
            return False
        else:
            return True

    def get_id(self):
        return unicode(self.id)
    
#     def get_auth_token(self):
#         return unicode(make_secure_token(self.id, self.username, self.password))
