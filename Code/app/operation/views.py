from .. import db
from . import operation
from ..models.User import User
from ..models.Roleomg import Role
from ..models.School import School
from ..models.Pro2015 import Pro2015
from ..models.Pro2016 import Pro2016
from ..models.Pro2017 import Pro2017
from ..models.Rank import Rank
from flask import (render_template,
                   abort,
                   current_app,
                   request, redirect,
                   url_for,
                   flash,
                   jsonify,
                    )  # json conversion
from flask_login import (login_required,
                         current_user, )
from .forms import (EditForm,
                    ChangePasswordForm,
                    ChangeAvatars,
                    EditProfileAdminForm,
                    )
from ..decorators import admin_required
from ..models.Permission import Permission
from ..models.User_operation import Comment


@operation.route('/user/<username>')
def user(username):
    """
    This function is used to show the user profile
    :param username: username
    :return: remder user profile page
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    follows = [{'school': School.query.filter_by(place_id=item.followed_id).first(), 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('/user/user.html', user=user, title='',
                           endpoint='.following', pagination=pagination,
                           follows=follows)


@operation.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    This function allows user to change his/her profile
    :return: render edit_profile page first, if the user updates his/her profile, refresh the user profile page
    """
    form = EditForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()

        if user is None:
            current_user.username = form.name.data
        else:
            # flash("This name has existed")
            pass

        current_user.location = form.location.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))

    form.name.data = current_user.username
    form.location.data = current_user.location
    return render_template('user/edit_profile.html', form=form)


@operation.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    """
    The function is used for admin to manage users' information
    :param id: user id
    :return: render edit_profile page first, if the admin updates his/her profile, refresh the user profile page
    """
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.location = form.location.data
        db.session.add(user)
        db.session.commit()
        # flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.location.data = user.location
    return render_template('user/edit_profile.html', form=form, user=user)


@operation.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    """
    This function allows user to update a new avatar
    :return: render change avatar page first, if the user updates his/her avatar, refresh the user profile page
    """
    form = ChangeAvatars()
    if form.validate_on_submit():
        # file object
        avatar = request.files['avatar']
        file_name = avatar.filename
        upload_folder = current_app.config['UPLOAD_FOLDER']
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif']
        file_type = file_name.rsplit('.', 1)[-1] if '.' in file_name else ''

        if file_type not in allowed_extensions:
            flash('File error.')
            return redirect(url_for('.user', username=current_user.username))

        # save in the database
        target = '{}{}.{}'.format(upload_folder, current_user.username, file_type)
        avatar.save(target)
        current_user.photo = '../../static/avatars/{}.{}'.format(current_user.username, file_type)
        db.session.add(current_user)
        db.session.commit()
        flash('Your avatar has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    return render_template('user/change_avatar.html', form=form)


@operation.route('/change_password', methods=['GET', 'POST'])
@login_required  # only login user can change password
def change_password():
    """
    This function allows user to change his/her password
    :return: render change password page first, if the user updates his/her password successfully, redirect to main page
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password2.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("user/change_password.html", form=form)


# Add following function
@operation.route('/follow/<place_id>', methods=['GET', 'POST'])
@login_required
def follow(place_id):
    """
    This fuction allows users to save the school to their watching list
    :param place_id: school's place_id
    :return: watching list data, school followers data (JSON)
    """
    school = School.query.filter_by(place_id=place_id).first()
    if school is None:
        # flash('Invalid school name.')
        return redirect(url_for('main.index'))
    if current_user.is_following(school):
        flash('You have already followed this school.')
        return redirect(url_for('main.school_detail', official_school_name=school.official_school_name,
                                place_id=school.place_id))
    if current_user.can(Permission.FOLLOW):
        current_user.follow(school)
    # flash('You are now following %s.' % official_school_name)

    return jsonify({'result': 'success', 'school_followers': school.followers.count()})


@operation.route('/unfollow/<place_id>', methods=['GET', 'POST'])
@login_required
def unfollow(place_id):
    """
    This function allows users to remove the school from their watching list
    :param place_id: school's place_id
    :return: watching list data, school followers data (JSON)
    """
    school = School.query.filter_by(place_id=place_id).first()
    if school is None:
        # flash('Invalid school name.')
        return redirect(url_for('main.index'))
    if not current_user.is_following(school):
        flash('You have not followed this school.')
        return redirect(url_for('main.school_detail', official_school_name=school.official_school_name,
                                place_id=school.place_id))
    current_user.unfollow(school)
    return jsonify({'result': 'success', 'school_followers': school.followers.count()})


@operation.route('/add_comparison/<place_id>', methods=['GET', 'POST'])
def add_to_comparison_list(place_id):
    """
    This function allows user to add school to comparision list
    :param place_id: school place_id
    :return: comparison list data
    """
    school = School.query.filter_by(place_id=place_id).first()
    anonymous_user = User.current_anonymous_user()

    if school is None:
        # flash('Invalid school name.')
        return redirect(url_for('main.index'))

    # users can only add 4 school to comparision list once
    diverse = 'True'
    increasable = 'True'
    if current_user.is_anonymous:
        if anonymous_user.is_comparing(school):
            diverse = 'False'
        else:
            if anonymous_user.compared.count() < 4:
                anonymous_user.comparison(school)
            else:
                increasable = 'False'
    else:
        if current_user.is_comparing(school):
            diverse = 'False'
        else:
            if current_user.compared.count() < 4:
                current_user.comparison(school)
            else:
                increasable = 'False'

    if current_user.is_anonymous:
        comparison_list = anonymous_user.compared.all()
    else:
        comparison_list = current_user.compared.all()

    # generate comparision list
    name_list = []
    for school_ in comparison_list:
        comparison_school = School.query.filter_by(place_id=school_.compared_id).first()
        name_list.append(comparison_school.official_school_name)

    return jsonify({'result': 'success', 'comparison_list': name_list, 'increasable': increasable, 'diverse': diverse})


@operation.route('/remove_comparison/<place_id>', methods=['GET', 'POST'])
def remove_from_comparison_list(place_id):
    """
        This function allows user to remove school from comparision list
        :param place_id: school place_id
        :return: comparison list data
        """
    school = School.query.filter_by(place_id=place_id).first()
    anonymous_user = User.current_anonymous_user()
    if school is None:
        # flash('Invalid school name.')
        return redirect(url_for('main.index'))

    # check the status of the user(anonymous user and login user)
    if current_user.is_anonymous:
        if not anonymous_user.is_comparing(school):
            # flash('You have not followed this school.')
            return redirect(url_for('main.school_detail', official_school_name=school.official_school_name,
                                    place_id=school.place_id))
        anonymous_user.remove_comparison(school)
        comparison_list = anonymous_user.compared.all()
    else:
        if not current_user.is_comparing(school):
            # flash('You have not followed this school.')
            return redirect(url_for('main.school_detail', official_school_name=school.official_school_name,
                                    place_id=school.place_id))
        current_user.remove_comparison(school)
        comparison_list = current_user.compared.all()

    # generate comparison list
    name_list1 = []
    for school_ in comparison_list:
        comparison_school = School.query.filter_by(place_id=school_.compared_id).first()
        name_list1.append(comparison_school.official_school_name)

    return jsonify({'result': 'success', 'comparison_list': name_list1})


@operation.route('/compare/clear_all', methods=['GET', 'POST'])
def remove_all():
    """
    This function is used to clear all school in the comparison list
    :return: status of removal
    """
    anonymous_user = User.current_anonymous_user()
    if current_user.is_anonymous:
        comparison_list = anonymous_user.compared.all()
    else:
        comparison_list = current_user.compared.all()
    if len(comparison_list) != 0:
        for school_ in comparison_list:
            db.session.delete(school_)
            db.session.commit()
    return jsonify({'result': 'success'})


@operation.route('/comparing/<username>', methods=['GET', 'POST'])
def in_comparison_list(username):
    """
    This function allows user to check whether the school in comparison list
    :param username: username
    :return: render comparing page
    """
    user_ = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = user_.compared.paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    # school = School.query.filter_by(place_id=item.followed_id).first()
    comparisons = [{'school': School.query.filter_by(place_id=item.compared_id).first(), 'timestamp': item.timestamp}
                   for item in pagination.items]
    # school = School.query.filter_by(place_id=user.followed).first()
    return render_template('user/comparing.html', user=user_, title='',
                           endpoint='.comparing', pagination=pagination,
                           follows=comparisons)


@operation.route('/compare', methods=['GET', 'POST'])
def compare():
    """
    This functions is used to get the information of compared school
    :return: compared school data(JSON)
    """
    comparison_school_collection = []
    rank_collection = []
    progression2015_collection = []
    progression2016_collection = []
    progression2017_collection = []

    anonymous_user = User.current_anonymous_user()
    if current_user.is_anonymous:
        comparison_list = anonymous_user.compared.all()
    else:
        comparison_list = current_user.compared.all()

    # process compared school data
    for school_ in comparison_list:
        comparison_school = School.query.filter_by(place_id=school_.compared_id).first()
        school_rank = Rank.query.filter_by(place_id=school_.compared_id).first()
        rank_collection.append(school_rank)
        if school_rank:
            comparison_school.ST_ratio = school_rank.stu_tea_ratio
            comparison_school.rank2017 = school_rank.rank
            comparison_school.rank2016 = school_rank.p_rank

        else:
            comparison_school.ST_ratio = ""
            comparison_school.rank2017 = "No Data"
            comparison_school.rank2016 = "No Data"

        progression2015 = Pro2015.query.filter_by(place_id=school_.compared_id).first()
        progression2015_collection.append(progression2015)
        if progression2015 :
            comparison_school.progression2015 = progression2015.Total_progression
        else:
            comparison_school.progression2015 = "No Data"

        progression2016 = Pro2016.query.filter_by(place_id=school_.compared_id).first()
        progression2016_collection.append(progression2016)
        if progression2016 :
            comparison_school.progression2016 = progression2016.Total_progression
        else:
            comparison_school.progression2016 = "No Data"

        progression2017 = Pro2017.query.filter_by(place_id=school_.compared_id).first()
        progression2017_collection.append(progression2017)
        if progression2017 :
            comparison_school.progression2017 = progression2017.Total_progression
        else:
            comparison_school.progression2017 = "No Data"

        comparison_school_collection.append(comparison_school)

    return render_template('user/compare.html', schools=comparison_school_collection, ranks=rank_collection,
                           pro2015=progression2015_collection, pro2016=progression2016_collection,
                           pro2017=progression2017_collection)


@operation.route('/add_comment/<place_id>', methods=['GET', 'POST'])
@login_required
def comment(place_id):
    """
    This function allows user to add comment to a specific school
    :param place_id: school place_id
    :return: comment list, over_rate (JSON)
    """
    school = School.query.filter_by(place_id=place_id).first()
    current_user_info = current_user._get_current_object()
    # get user input
    json = request.get_json()

    # check whether users has commented the school
    has_commented = False
    if current_user.has_commented(school):
        has_commented = True
    else:
        # remove tap <> to ensure the security of comment function
        user_review = json['comment_content']
        if '<' or '>' in user_review:
            user_review = user_review.replace('<', '')
            user_review = user_review.replace('>', '')
        comment = Comment(
            author = current_user_info,
            author_avatar=current_user_info.photo,
            user_review=json['comment_content'], user_rating=json['ranks'],
            commented_official_school_name=place_id,
            school_id=school.place_id,
            author_name=current_user_info.username
        )
        db.session.add(comment)
        db.session.commit()

    if school is None:
        # flash('Invalid school name.')
        return redirect(url_for('main.index'))
    comments = Comment.query.filter_by(school_id=place_id) \
        .order_by(Comment.time.desc())

    # generate comment_list
    comment_list = []
    rate_list = []
    for comment in comments:
        rate_list.append(comment.user_rating)
        single_comment = comment.__dict__
        single_comment.pop('_sa_instance_state')
        single_comment.pop('author')
        single_comment['time'] = str(single_comment['time'])
        comment_list.append(single_comment)

    # compute the overll_rate
    overall_rate = Comment.compute_overall_rate(rate_list)
    overall_rate = round(overall_rate,2)

    return jsonify({'has_commented': has_commented, 'comment_list': comment_list, 'overall_rate':overall_rate})


@operation.route('/remove_comment/<place_id>', methods=['GET', 'POST'])
@login_required
def remove_comment(place_id):
    """
    This function allows users to remove their comment
    :param place_id: school place id
    :return: comment list, overall_rate, comment status (JSON)
    """
    school = School.query.filter_by(place_id=place_id).first()
    if school is None:
        # flash('Invalid school name.')
        return redirect(url_for('main.index'))

    # check the status of comment and remove the comment
    has_commented = True
    has_removed = False
    if not current_user.has_commented(school):
        has_commented = False
    else:
        current_user.remove_comment(school)
        has_removed = True

    # sort the comments by post time
    comments = Comment.query.filter_by(school_id=place_id) \
        .order_by(Comment.time.desc())

    # generate comment list
    comment_list = []
    rate_list = []
    for comment_ in comments:
        rate_list.append(comment_.user_rating)
        single_comment = comment_.__dict__
        single_comment.pop('_sa_instance_state')
        single_comment.pop('author')
        comment_list.append(single_comment)

    # compute the overll_rate
    overall_rate = Comment.compute_overall_rate(rate_list)
    overall_rate = round(overall_rate,2)

    return jsonify({'has_commented': has_commented, 'has_remove': has_removed,  'comments': comment_list, 'overall_rate':overall_rate})
