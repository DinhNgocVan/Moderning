"""this file include:
    login,
    sign up,
    logout,
    reset password,
    validate email of users"""
import os
import re
import smtplib

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer

"""setting-----------------------------------------------------------------------------------------------------------"""
VIEW_ROOT = os.path.dirname(os.path.abspath(__file__)) # phuc vu cho upload anh


"""test validation---------------------------------------------------------------------------------------------------"""
# contains alphabets, digits and dash, from 3 to 16 characters
USERNAME_PATTERN = '^[a-z0-9_-]{3,16}$'
EMAIL_PATTERN = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
# a digit must occur at least , a lower case letter must occur at least once,
# no whitespace allowed in the entire string, from 6-10 characters
PASSWORD_PATTERN = "^(?=.*[a-z])(?=.*\d)[A-Za-z\d@$!#%*?&]{6,10}$"

"""server send email to users----------------------------------------------------------------------------------------"""
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
EMAIL_ADDRESS = 'modernjura0503@gmail.com'
EMAIL_PASSWORD = 'modernjura03052021'
# EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
# EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

s = URLSafeTimedSerializer('Thisisasecret!')

# -----------------------------------------------------------------------------------------------------------------------

auth = Blueprint('auth', __name__)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('views.homePage'))

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.homePage'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login2.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.homePage'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('views.home'))

        email = request.form.get('email')
        userName = request.form.get('userName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif User.query.filter_by(userName=userName).first():
            flash('This user name is already exists. Please choose another name.', category='error')
        elif re.search(EMAIL_PATTERN, email) is None:
            flash('Email is invalid.', category='error')
        elif re.search(USERNAME_PATTERN, userName) is None:
            flash('First name must contain alphabets, digits and dash, from 3 to 16 characters.', category='error')
        elif re.search(PASSWORD_PATTERN, password1) is None:
            flash('Password must be from 6-10 characters, have a digit must occur at least , '
                  'a lower case letter must occur at least once, no whitespace allowed in the entire string.',
                  category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        else:
            """hash - tạo hash password chỉ có thể kiểm tra password đúng bằng cách chuyển pass-> hashpass?? for what"""
            new_user = User(email=email, userName=userName,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('account created', category='success')
            return redirect(url_for('auth.login'))

    return render_template("sign-up.html")


@auth.route('/getEmail', methods=['GET', 'POST'])
def getEmail():
    if request.method == 'POST':
        email = request.form.get('email')
        if re.search(EMAIL_PATTERN, email) is None:
            print("email is invalid.")
        else:
            user = User.query.filter_by(email=email).first()
            # print(user)
            if user:
                # gửi email xác nhận đến người dùng-----------------------------------------------------------------------------
                # verify_code = random.randint(100001, 999999)
                # print(str(verify_code))

                token = s.dumps(email, salt='email-confirm')
                print("this is the token: " + token)
                confirm_address = "http://127.0.0.1:5000/reset_password/" + token

                message = EmailMessage()
                message['Subject'] = 'Welcome to Modern Jura!'
                message['From'] = EMAIL_ADDRESS
                message['To'] = email
                message.set_content('Please confirm your email by following links')
                message.add_alternative("""\
                        <!DOCTYPE html>
                        <html>
                            <p>
                                <a href=""" + confirm_address + """> Click here </a> to reset your password 
                            </p>
                        </html>
                        """, subtype='html')

                # message.set_content('This is your verify code.\n' + str(verify_code))

                with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.send_message(message)
                flash("We've send you a link to reset your password."
                      " This link is only active in 5 minutes. Please check your email.", category="success")
        # user = User.query.filter_by(email=email).first()
        # print(user)
        # print(email)
    return render_template("getEmail.html")


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """ this function to reset password for user when user forgot """
    # this token just active in 300s
    if request.method == "POST":
        email = s.loads(token, salt='email-confirm', max_age=300)
        print(email)
        user = User.query.filter_by(email=email).first()

        newPassword1 = request.form.get('newPassword1')
        newPassword2 = request.form.get('newPassword2')

        print(user)
        if user:
            """kiểm tra password hợp lệ-chỗ này cần chỉnh thêm file html-----------------------------------------------------"""
            if re.search(PASSWORD_PATTERN, newPassword1) is None:
                flash('Password must be from 6-10 characters, have a digit must occur at least , '
                      'a lower case letter must occur at least once, no whitespace allowed in the entire string.',
                      category='error')
            elif newPassword1 != newPassword2:
                flash('Passwords don\'t match.', category='success')
            else:
                user.password = generate_password_hash(newPassword1, method='sha256')
                db.session.commit()
                print(user.password)
                print("đang thay đổi đây.............")
                flash('Change password successfully!.', category='success')
            return redirect(url_for('auth.login'))
    # ------------------------------------------------------------------------------------------------------------------
    return render_template("forgotPass.html")


@auth.route('/settings/<id>', methods=['GET', 'POST'])
def settings(id):
    # user = User.query.get(id)
    if request.method == 'POST':
        avatar = request.files.get('avatar')
        userName = request.form.get('userName')
        dateOfBirth = request.form.get('dateOfBirth')
        sex = request.form.get('sex')
        country = request.form.get('country')
        bio = request.form.get('bio')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        # userName, date of birth, email, password, password 2
        duplicateUsername = User.query.filter_by(userName=userName).first()
        duplicateEmail = User.query.filter_by(email=email).first()
        # if duplicateUsername and (duplicateUsername != userName):
        #     print("duplicateUsername")
        #     #flash('This user name is already exists. Please choose another name.', category='error')
        # elif duplicateEmail and (duplicateEmail != email):
        #     print("duplicateEmail")
        #     flash('Email already exists.', category='error')
        # elif re.search(EMAIL_PATTERN, email) is None:
        #     print("email none")
        #     flash('Email is invalid.', category='error')
        # elif re.search(PASSWORD_PATTERN, password) is None:
        #     print("password")
        #     flash('Password must be from 6-10 characters, have a digit must occur at least , '
        #           'a lower case letter must occur at least once, no whitespace allowed in the entire string.',
        #           category='error')
        # elif password != password2:
        #     print("not match")
        #     flash('Passwords don\'t match.', category='error')
        # else:
        #     current_user.email = email
        #     current_user.password = generate_password_hash(password, method='sha256')
        # if re.search(USERNAME_PATTERN, userName) is None:
        #     print("user is none")
        #     flash('First name must contain alphabets, digits and dash, from 3 to 16 characters.', category='error')
        # else:
        #     current_user.userName = userName

        current_user.sex = sex
        print("avatar",avatar)
        if avatar:
            upload_avatar(current_user, avatar)
            print("not null avatar")
        if dateOfBirth:
            #print("kiểu của dữ liệu truyền vào ô date of birth:", dateOfBirth.content_type)
            #user.dateOfBirth = dateOfBirth
            print(10)
        if country:
            current_user.country = country
            print(11)
        if bio:
            current_user.bio = bio
            print(12)
        db.session.commit()
        print(13)
    return render_template("settings.html", user=current_user)


def upload_avatar(currentUser, upload_a):
    target = os.path.join(VIEW_ROOT, 'static\\images\\user_avatars')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    else:
        print('couldn\'t create upload directory: {}'.format(target))
    # upload_a = request.files.get('file')
    print("{} is the file name".format(upload_a.filename))
    # match dùng để kiểm tra tệp có hợp lệ không
    match = ["image/jpeg", "image/png", "image/jpg", "image/gif"]
    filetype = upload_a.content_type
    # print("Đây là loại của tệp nhaaaaaaaaaaaaaaaaaaaaaaaaa: ", filetype)
    if not ((filetype == match[0]) or (filetype == match[1]) or (filetype == match[2]) or (filetype == match[3])):
        print("------------------wrong type----------------")
    else:
        avt_name = "user" + str(currentUser.id) + ".jpg"
        destination = "/".join([target, avt_name])
        # lưu ảnh vào folder đã chọn
        upload_a.save(destination)
        # lưu ảnh vào cơ sở dữ liệu
        currentUser.avatar = "../static/images/user_avatars/"+avt_name
        db.session.commit()
        print("this file upload successfully!")
