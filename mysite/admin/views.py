from mysite.database.models import UserProfile, RefreshToken
from sqladmin import ModelView


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [UserProfile.id, UserProfile.first_name, UserProfile.last_name, UserProfile.username, UserProfile.status]


class UserTokenAdmin(ModelView, model=RefreshToken):
    column_list = [RefreshToken.id, RefreshToken.user_id]
