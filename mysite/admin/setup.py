from .views import UserProfileAdmin, UserTokenAdmin
from fastapi import FastAPI
from sqladmin import Admin
from mysite.database.database import engine


def setup_admin(app: FastAPI):
    admin = Admin(app, engine)
    admin.add_view(UserProfileAdmin)
    admin.add_view(UserTokenAdmin)
