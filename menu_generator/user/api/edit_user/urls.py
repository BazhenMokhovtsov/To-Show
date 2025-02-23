from django.urls import path

from .views import *

urlpatterns = [
    path(
        "change-email/first-step/",
        ChangeEmailFirstStep.as_view(),
        name="change_email_first_step",
    ),
    path(
        "change-email/second-step/",
        ChangeEmailSecondStep.as_view(),
        name="change_email_second_step",
    ),
    path("change-password/", ChangePassword.as_view(), name="change_password"),
    path("delete-account/", DeleteAccount.as_view(), name="delete_account"),
    path("edit-user/", EditUser.as_view(), name="edit_user"),
]
