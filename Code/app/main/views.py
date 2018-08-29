from .. import db
from . import main
from ..models.School import School
from ..models.Pro2015 import Pro2015
from ..models.Pro2016 import Pro2016
from ..models.Pro2017 import Pro2017
from ..models.Rank import Rank
from ..models.User import User
from flask import (render_template,
                   abort,
                   request, redirect,
                   url_for,
                   jsonify,)  # json conversion
from flask_login import current_user
from .forms import SearchForm
from ..models.User_operation import Comment

current_location = None
user_db = None


@main.route('/distance_computing/<geolocation>/<city>', methods=['GET', 'POST'])
def distance_computing(geolocation, city):
    """
    This function is used for distance computing and sorting
    :param geolocation: the coordinate of the place
    :param city: The city where the place is located
    :return: Sorted school list (JSON)
    """
    # process geolocation data
    geo_split = geolocation.split(',')
    global current_location
    current_location = geo_split

    if city == 'Ireland':
        school_list = db.session.query(School, Pro2017, Rank).outerjoin(Pro2017) \
            .outerjoin(Rank).all()
    else:
        school_list = db.session.query(School, Pro2017, Rank).outerjoin(Pro2017) \
            .outerjoin(Rank).filter(School.county == city)

    page_count = school_list.count() // 6

    # restrict the page number
    if page_count > 5:
        page_count = 5

    schools = school_list.all()
    schools_list = list(schools)

    # compute distance for each school
    for school in schools_list:
        distance_computing = School.distance_calculator(float(school[0].lat), float(school[0].lng),
                                                        float(geo_split[0]), float(geo_split[1]))
        school = list(school)
        school[0].distance = distance_computing

    # sort the data by distance
    schools_list.sort(key=lambda x: x[0].distance)

    # convert data to JSON format
    data = School.make_json(schools_list)
    if len(data) > 30:
        json_list_limitation = data[0:30]
    else:
        json_list_limitation = data

    return jsonify({'result': json_list_limitation, 'page_count': page_count})


@main.route('/', methods=['GET', 'POST'])
def index():
    """
    This function is for main page, this page includes search box(Web Form) and school information display
    :return: render the main page first, when user click submit button, redirect to the result page
    """
    global user_db
    global current_location
    user_db = db.session.query(School, Rank, Pro2017).outerjoin(Rank).outerjoin(Pro2017)

    # create the account for anonymous user
    if User.current_anonymous_user():
        pass
    else:
        User.create_anonymous()

    # search engine
    form = SearchForm()
    if form.validate_on_submit():
        # get the user input place's latitude and longitude
        if form.lat.data == '' and form.lng.data == '':
            if 'ireland' not in form.search.data.lower():
                keyword = form.search.data + ' ' + 'Ireland'
            else:
                keyword = form.search.data

            # get the coordination of the place from google maps
            # sometimes, it cannot get the result due to network issue, so try to get it five time
            signal = True
            count = 0
            while signal:
                input_coordination = User.get_coordination(keyword)
                count = count + 1
                if len(input_coordination) != 0 or count == 5:
                    signal = False
                    break
            if len(input_coordination) == 0:
                input_coordination = 'unknown'

        elif form.lat.data != '' and form.lng.data != '':
            input_coordination = [form.lat.data, form.lng.data]
        else:
            input_coordination = 'unknown'
        # process input_coodination
        if input_coordination != 'unknown':
            geolocation = str(input_coordination[0]) + "," + str(input_coordination[1])
        else:
            geolocation = "search_location"

        # GET THE NUMBER IN STRING, process input keyword like Dublin1 and Dublin 1(has space and no space)
        user_input = form.search.data
        input_processed = School.process_city_plus_area(user_input)

        # process dublin 1-24 in address, like Enniskerry Road, Sandyford, Dublin 18
        area_address = School.process_dublin_with_region_number(input_processed)
        input = area_address[1]

        #  process punctuation ，.
        input_split = School.process_punctuation(input)

        # make fuzzy query statement
        like = School.make_query_statement(input_split, area_address[0])

        return redirect(url_for('.result', like=like, coordination = geolocation))

    return render_template('main/home.html', form=form, current_location = current_location)


@main.route('/search/<input_keyword>', methods=['GET', 'POST'])
def search(input_keyword):
    """
    This function is used to convert the user input keyword to fuzzy query statement which is used to query database
    :param input_keyword: the keyword user input to search box
    :return: redirect to search result page
    """

    if not 'ireland' in input_keyword.lower():
        keyword = input_keyword + ' '+ 'Ireland'
    else:
        keyword = input_keyword

    # get input place's latitude and longitude
    signal = True
    count = 0
    while signal:
        input_coordination = User.get_coordination(keyword)
        count = count + 1
        if len(input_coordination) != 0 or count == 5:
            signal = False
            break
    if input_coordination != 'unknown' and len(input_coordination) != 0:
        geolocation = str(input_coordination[0]) + "," + str(input_coordination[1])
    else:
        geolocation = "search_location"

    # GET THE NUMBER IN STRING, process input keyword like Dublin1 and Dublin 1(has space and no space)
    # Fuzzy Query Statement should be like '%dublin% 1' which can match all schools in Dublin 1.
    user_input = input_keyword
    input_processed = School.process_city_plus_area(user_input)

    # process dublin 1-24 in address, like Enniskerry Road, Sandyford, Dublin 18
    area_address = School.process_dublin_with_region_number(input_processed)
    input = area_address[1]

    #  process punctuation ，.
    input_split = School.process_punctuation(input)

    # make fuzzy query statement
    like = School.make_query_statement(input_split, area_address[0])

    return redirect(url_for('.result', like=like, coordination = geolocation))


@main.route('/click_on_map/<coordination>/<city>', methods=['GET', 'POST'])
def click_on_map(coordination, city):

    """
    This route function is used for when users click on the map to relocate the position and compute the distance between map marker and schools
    :param coordination: the coordination of the place users click on the map
    :param city: the city of the place users click on the map
    :return: nearby school list(JSON)
    """
    join_search = db.session.query(School, Rank, Pro2017).outerjoin(Rank).outerjoin(Pro2017)

    lat = coordination.split(',')[0]
    lng = coordination.split(',')[1]

    school_list = join_search.filter(School.county == city)
    result_list = []
    for school in school_list:
        distance_computing1 = School.distance_calculator(float(school[0].lat), float(school[0].lng),
                                                         float(lat), float(lng))
        if distance_computing1 < 20:
            school = list(school)
            school[0].distance = round(distance_computing1, 2)
            result_list.append(school)
    result_list.sort(key=lambda x: x[0].distance)

    data = School.make_json(result_list)

    return jsonify({'result': data})


@main.route('/result/<like>/<coordination>')
def result(like, coordination):
    """
    The functions is used to query database
    :param like: fuzzy query statement
    :param coordination: the coordination of the place user input
    :return: render the search result page
    """

    keyword = like.replace('%', ' ')

    # generate the url
    url = url_for('auth.login', type='result' + ',' + like)
    like = like.lower()

    global current_location
    if current_location is None:
        current_location = [53.3083, -6.2236]

    global user_db
    if user_db is None:
        join_search = db.session.query(School, Rank, Pro2017).outerjoin(Rank).outerjoin(Pro2017)
    else:
        join_search = user_db

    counties = ['antrim', 'armagh', 'carlow', 'cavan', 'clare', 'cork', 'derry', 'donegal', 'down', 'dublin',
                'fermanagh', 'galway', 'kerry', 'kildare', 'kilkenny', 'laois', 'leitrim', 'limerick',
                'Longford', 'Louth', 'Mayo', 'Meath', 'Monaghan', 'Offaly', 'Roscommon',
                'sligo', 'tipperary', 'tyrone', 'waterford', 'westmeath', 'wexford', 'wicklow']

    # check whether input_keyword includes above conties
    intersection_with_counties = list(set(like.split('%')) & set(counties))

    # try to match the record in database - match with address and school name
    # records can be matched in database
    if len(intersection_with_counties) != 0:
        new_like2 = like.replace('%' + intersection_with_counties[0] + '%', '')
        result1 = join_search.filter(School.address.ilike('%' + intersection_with_counties[0] + '%' + new_like2)).all()
        if len(result1) == 0:
            result1 = join_search.filter(School.address.ilike(new_like2 + '%' + intersection_with_counties[0] + '%')).all()
        if len(result1) == 0:
            result1 = join_search.filter(School.address.ilike(new_like2)).all()
        result2 = join_search.filter(School.official_school_name.ilike(new_like2),
                                     School.county.like('%' + intersection_with_counties[0] + '%')).all()
    else:
        # Dublin 4
        result1 = join_search.filter(School.address.ilike(like)).all()
        result2 = join_search.filter(School.official_school_name.ilike(like)).all()

    # combine the query result
    result1_set = set(result1)
    result2_set = set(result2)
    results = result1_set | result2_set
    result_list = list(results)

    # distance computing ~ process the latitude and longitude and get current city
    # two cases: no record can be matched and record can be matched

    if len(intersection_with_counties) != 0:
        current_city = intersection_with_counties[0]
        lat = coordination.split(",")[0]
        lng = coordination.split(",")[1]

    # input is not using google search box
    elif coordination != "search_location":
        lat = coordination.split(",")[0]
        lng = coordination.split(",")[1]
        signal = True
        count = 0
        while signal:
            current_city = User.get_city(lat, lng)
            count = count + 1
            if len(current_city) != 0 or count == 5:
                signal = False
                break
    else:
        current_city = 'unknown'

    # query statement cannot be matched
    # get the input place's latitude and longitude from google maps search box
    # computing them with schools' latitude and longitude to get distance
    if len(result_list) == 0:
        school_city_list = join_search.filter(School.county == current_city).all()
        result_list = []
        if coordination != 'search_location':
            for school in school_city_list:
                distance_computing1 = School.distance_calculator(float(school[0].lat), float(school[0].lng),
                                                            float(lat), float(lng))
                if distance_computing1 < 10:
                    school = list(school)
                    school[0].distance = round(distance_computing1, 2)
                    result_list.append(school)
        result_list.sort(key=lambda x: x[0].distance)

    # if input keyword is school name
    # distance is computing by user current location and schools
    else:
        for school in result_list:
            distance_computing = School.distance_calculator(float(school[0].lat), float(school[0].lng),
                                                            float(current_location[0]), float(current_location[1]))
            school = list(school)
            school[0].distance = round(distance_computing, 2)
            coordination = (current_location[0], current_location[1])

        # sort the data by distance
        result_list.sort(key=lambda x: x[0].distance)

    return render_template('/main/filter.html', school_result=result_list, url=url,
                           keyword=keyword, input_location=coordination)


@main.route('/school/<official_school_name>/<place_id>', methods=['POST', 'GET'])
def school_detail(place_id, official_school_name):
    """
    This function is for rendering school detail page
    :param place_id: the place_id of the school
    :param official_school_name: the official_school_name of the school
    :return: render the school detail page
    """
    # check user status
    if User.current_anonymous_user():
        pass
    else:
        User.create_anonymous()
    school = db.session.query(School, Rank, Pro2015, Pro2016, Pro2017).filter_by(place_id=place_id) \
        .outerjoin(Rank).outerjoin(Pro2015).outerjoin(Pro2016).outerjoin(Pro2017).first()

    if school is None:
        abort(404)

    # school sample
    # (< Model School `Blackrock College` >, < Rank ChIJUVrVbdAIZ0gRC3qozmRomPQ >,
    # < Model Pro2015 `Blackrock College, Blackrock, Co Dublin` >, None, < Model Pro2017 `Blackrock College` >)
    if school[0] is not None:
        school[0].add = school[0].add + 1
        db.session.commit()

    if not current_user.is_anonymous:
        comparison_list = current_user.compared.all()
    else:
        anonymous_user = User.current_anonymous_user()
        comparison_list = anonymous_user.compared.all()

    # get the school name in comparision list
    name_list = []
    for school_ in comparison_list:
        comparison_school = School.query.filter_by(place_id=school_.compared_id).first()
        name_list.append(comparison_school.official_school_name)

    universities = ['UCD', 'TCD', 'DCU', 'UCC', 'UL', 'Maynooth University', 'NUIG']

    # computing progression to university
    computing_rate_list = []
    for i in range(2,5):
        if school[i] is not None:
            computing_rate = (school[i].UCD + school[i].TCD + school[i].DCU + school[i].UL
                                  + school[i].Maynooth_University + school[i].NUIG
                                  + school[i].UCC) / school[i].Number_who_sat_Leaving_Cert_2015
        else:
            computing_rate = 0
        computing_rate_list.append(computing_rate)

    # get all comments of the school ordered by timestamp
    comments = Comment.query.filter_by(school_id=place_id) \
        .order_by(Comment.time.desc())

    page = request.args.get('page', 1, type=int)
    pagination = comments.paginate(
        page, per_page=6,
        error_out=False)
    comment_pagination = pagination.items

    for single_comment in comment_pagination:
        single_comment.user_review = single_comment.user_review.replace('\n', ' ')

    review_number = comments.count()

    rate_list = []
    for comment in comments:
        rate_list.append(comment.user_rating)

    #compute the overll_rate
    overall_rate = Comment.compute_overall_rate(rate_list)
    overall_rate = round(overall_rate, 2)
    url = url_for('auth.login', type='school_detail' + ',' + official_school_name + ',' + place_id)

    return render_template('main/school_detail.html', school=school[0], rank=school[1],
                           university_going=school[2], university_going1=school[3], university_going2=school[4],
                           universities=universities, school_names=name_list, university_going_a=0,
                           university_going_b=0, university_going_c=0, university_only_a=0,
                           university_only_b=0, university_only_c=0, comments=comment_pagination,
                           overall_rate=overall_rate, pagination=pagination,
                           count=review_number, school_name=official_school_name, place_id=place_id, url=url,
                           computing_rate2015=computing_rate_list[0], computing_rate2017=computing_rate_list[2],
                           computing_rate2016=computing_rate_list[1])


@main.route('/rank', methods=['GET', 'POST'])
def rank():
    """
    This route function is used for rendering the rank page
    :return: render the rank page
    """
    page = request.args.get('page', 1, type=int)
    schools = db.session.query(School.place_id, School.roll_number, School.official_school_name, School.address, School.fee,
                               School.photo_ref1, Rank.rank, Rank.name, Rank.official_school_name, Rank.p_rank,
                               Rank.boy, Rank.gender_type, Rank.girl, Rank.stu_tea_ratio, Rank.at_third_level,
                               Rank.at_university).join(Rank, School.place_id == Rank.place_id).order_by(Rank.rank)

    pagination = schools.paginate(
        page, per_page=6,
        error_out=False)
    schools_pagination = pagination.items
    return render_template('main/rank.html', pagination=pagination, schools=schools_pagination)
