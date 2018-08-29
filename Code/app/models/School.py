from app import db
import re
import mpu
from ..models.User_operation import Compare, Follow


class School(db.Model):
    _tablename_ = 'school'
    place_id = db.Column(db.String(50), primary_key=True)
    roll_number = db.Column(db.String(50))
    official_school_name = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(255))
    address1 = db.Column(db.String(50))
    address2 = db.Column(db.String(50))
    address3 = db.Column(db.String(50))
    address4 = db.Column(db.String(50))
    address = db.Column(db.String(255))
    county = db.Column(db.String(50))
    eircode = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(50))
    principal_name = db.Column(db.String(50))
    deis = db.Column(db.String(50))
    school_gender = db.Column(db.String(50))
    pupil_attendance_type = db.Column(db.String(50))
    irish_classification = db.Column(db.String(50))
    gaeltacht_area_location = db.Column(db.String(50))
    fee = db.Column(db.String(50))
    religion = db.Column(db.String(50))
    open_close_status = db.Column(db.String(50))
    total_girl = db.Column(db.Integer)
    total_boy = db.Column(db.Integer)
    total_pupil = db.Column(db.Integer)
    lat = db.Column(db.Float(10))
    lng = db.Column(db.Float(10))
    # coordinate = db.Column(db.String(50))
    photo_ref1 = db.Column(db.String(255))
    photo_ref2 = db.Column(db.String(255))
    photo_ref3 = db.Column(db.String(255))
    photo_ref4 = db.Column(db.String(255))
    photo_ref5 = db.Column(db.String(255))
    distance = db.Column(db.Float(50))
#award 1--13
    AwardTitle1 = db.Column(db.String(255))
    ProjectTitle1 = db.Column(db.String(255))
    ProjectCategory1 = db.Column(db.String(255))
    Student1 = db.Column(db.String(255))

    AwardTitle2 = db.Column(db.String(255))
    ProjectTitle2 = db.Column(db.String(255))
    ProjectCategory2 = db.Column(db.String(255))
    Student2 = db.Column(db.String(255))

    AwardTitle3 = db.Column(db.String(255))
    ProjectTitle3 = db.Column(db.String(255))
    ProjectCategory3 = db.Column(db.String(255))
    Student3 = db.Column(db.String(255))

    AwardTitle4 = db.Column(db.String(255))
    ProjectTitle4 = db.Column(db.String(255))
    ProjectCategory4 = db.Column(db.String(255))
    Student4 = db.Column(db.String(255))

    AwardTitle5 = db.Column(db.String(255))
    ProjectTitle5 = db.Column(db.String(255))
    ProjectCategory5 = db.Column(db.String(255))
    Student5 = db.Column(db.String(255))

    AwardTitle6 = db.Column(db.String(255))
    ProjectTitle6 = db.Column(db.String(255))
    ProjectCategory6 = db.Column(db.String(255))
    Student6 = db.Column(db.String(255))

    AwardTitle7 = db.Column(db.String(255))
    ProjectTitle7 = db.Column(db.String(255))
    ProjectCategory7 = db.Column(db.String(255))
    Student7 = db.Column(db.String(255))

    AwardTitle8 = db.Column(db.String(255))
    ProjectTitle8 = db.Column(db.String(255))
    ProjectCategory8 = db.Column(db.String(255))
    Student8 = db.Column(db.String(255))

    AwardTitle9 = db.Column(db.String(255))
    ProjectTitle9 = db.Column(db.String(255))
    ProjectCategory9 = db.Column(db.String(255))
    Student9 = db.Column(db.String(255))

    AwardTitle10 = db.Column(db.String(255))
    ProjectTitle10 = db.Column(db.String(255))
    ProjectCategory10 = db.Column(db.String(255))
    Student10 = db.Column(db.String(255))

    AwardTitle11 = db.Column(db.String(255))
    ProjectTitle11 = db.Column(db.String(255))
    ProjectCategory11 = db.Column(db.String(255))
    Student11 = db.Column(db.String(255))

    AwardTitle12 = db.Column(db.String(255))
    ProjectTitle12 = db.Column(db.String(255))
    ProjectCategory12 = db.Column(db.String(255))
    Student12 = db.Column(db.String(255))

    AwardTitle13 = db.Column(db.String(255))
    ProjectTitle13 = db.Column(db.String(255))
    ProjectCategory13 = db.Column(db.String(255))
    Student13 = db.Column(db.String(255))

    add = db.Column(db.Integer) #add school into own list, and the access+1
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed,lazy=joined'),  # corresponding followed_id
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    comparators = db.relationship('Compare', foreign_keys=[Compare.compared_id],
                               backref=db.backref('followed,lazy=joined'),  # corresponding followed_id
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref=db.backref('school, lazy=joined'), lazy='dynamic')

    # userlike = db.relationship('User_like', backref=db.backref('roll_number1'), lazy='dynamic')
    # history = db.relationship('History', backref=db.backref('roll_number2'), lazy='dynamic')
    # comments = db.relationship('Comments', backref=db.backref('roll_number3'), lazy='dynamic')
    pro2015 = db.relationship('Pro2015', backref=db.backref('roll_number4'), lazy=True, uselist=False)
    pro2016 = db.relationship('Pro2016', backref=db.backref('roll_number5'), lazy=True, uselist=False)
    pro2017 = db.relationship('Pro2017', backref=db.backref('roll_number6'), lazy=True, uselist=False)

    def __init__(self):
        self.add = 0

    @staticmethod
    def distance_calculator(school_lat1,school_lng1, user_lat2,user_lng2):
        distance = mpu.haversine_distance((school_lat1, school_lng1), (user_lat2, user_lng2))
        return distance

    @staticmethod
    def make_json(schools):
        json_list = []
        for school in schools:
            dict1 = {}
            dict2 = school[0].__dict__
            dict2.pop('_sa_instance_state')
            if school[1] is not None:
                dict3 = school[1].__dict__
                dict3.pop('_sa_instance_state')
            else:
                dict3 = {'Total_progression2': 'No Data', 'Total_progression': 'No data'}

            if school[2] is not None:
                dict4 = school[2].__dict__
                dict4.pop('_sa_instance_state')
            else:
                dict4 = {'rank': 'No Data', 'p_rank': 'No data'}

            dict1.update(dict2)
            dict1.update(dict3)
            dict1.update(dict4)
            json_list.append(dict1)

        return json_list

    @staticmethod
    def process_punctuation(input_keyword):
        if ',' in input_keyword:
            new_input = input_keyword.replace(',', ' ')
            input_split = new_input.split()
        elif '.' in input_keyword:
            new_input = input_keyword.replace('.', ' ')
            input_split = new_input.split()
        else:
            input_split = input_keyword.split()
        return input_split

    @staticmethod
    def make_query_statement(input, area):
        if len(input) > 1:
            print(1)
            like = ''
            for split in input:
                like += '%' + split + '%'
            like = like + area
        elif len(input) == 0:
            like = area
            print(2)
        else:
            print(3)
            like = '%' + input[0] + '%' + area
        return like

    @staticmethod
    def process_city_plus_area(user_input):
        print('input_', user_input)
        user_input1 = user_input.replace(' ', '')

        # GET THE NUMBER IN STRING, process input keyword like Dublin1 and Dublin 1(has space and no space)
        # Fuzzy Query Statement should be like '%dublin% 1' which can match all schools in Dublin 1.
        num = re.findall('\d+', user_input1)
        print('num', num)

        # change Dublin1 to Dublin 1(no space -> has space)
        if len(user_input) < 10:
            if len(num) >= 1:
                input_process = user_input1.split(num[0])
                print('process1', input_process)
                input_process1 = input_process[0] + num[0]
                input_process2 = input_process1.replace(num[0], (' ' + num[0]))
                print('1process2', input_process2)
            else:
                # NO NUMBER IN KEYWORD
                input_process2 = user_input
                print('input_process2', input_process2)
        else:
            input_process2 = user_input
        print('input_process2', input_process2)

        return input_process2

    @staticmethod
    def process_dublin_with_region_number(input):
        # process dublin 1-24 in address, like Enniskerry Road, Sandyford, Dublin 18
        input_processed_split = input.split()
        print("temp_split", input_processed_split)

        if len(input_processed_split) > 1:
            a = input_processed_split[-2] + ' ' + input_processed_split[-1]
        else:
            a = 'not in address'

        print('a', a)

        input = input
        area = ''
        for i in range(0, 24):
            if ("dublin " + str(i + 1)) == a:
                area += '%dublin% ' + str(i + 1)
                first = input.replace(('dublin ' + str(i + 1)), '')
                second = first.replace(('dublin  ' + str(i + 1)), '')
                input = second

        print('area', area)
        print('input', input)
        alist = []
        alist.append(area)
        alist.append(input)
        return alist


    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    # def is_commented_by(self, user):
    #     return self.comments.filter_by(
    #         author_id=user.id).first is not None

    def __repr__(self):
        return "<Model School `{}`>".format(self.official_school_name)




