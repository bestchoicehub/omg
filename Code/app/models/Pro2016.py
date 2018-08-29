from app import db


class Pro2016(db.Model):
    __tablename__ = 'pro2016'
    place_id = db.Column(db.String(50), db.ForeignKey('school.place_id'), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    name2 = db.Column(db.String(255))
    Number_who_sat_Leaving_Cert_2015 = db.Column(db.Integer)
    UCD = db.Column(db.Integer)
    TCD = db.Column(db.Integer)
    DCU = db.Column(db.Integer)
    UL = db.Column(db.Integer)
    Maynooth_University = db.Column(db.Integer)
    NUIG = db.Column(db.Integer)
    UCC = db.Column(db.Integer)
    St_Angela = db.Column(db.Integer)
    QUB = db.Column(db.Integer)
    UU = db.Column(db.Integer)
    Blanch_IT = db.Column(db.Integer)
    Nat_Col_of_Irl = db.Column(db.Integer)
    DIT = db.Column(db.Integer)
    Tallaght_IT = db.Column(db.Integer)
    Athlone_IT = db.Column(db.Integer)
    Cork_IT = db.Column(db.Integer)
    Dundalk_IT = db.Column(db.Integer)
    GMIT = db.Column(db.Integer)
    IADT = db.Column(db.Integer)
    IT_Carlow = db.Column(db.Integer)
    IT_Sligo = db.Column(db.Integer)
    IT_Tralee = db.Column(db.Integer)
    IT_Letter_kenny = db.Column(db.Integer)
    IT_Limerick = db.Column(db.Integer)
    WIT = db.Column(db.Integer)
    Marino_Instit_of_Ed = db.Column(db.Integer)
    Mary_Immac = db.Column(db.Integer)
    NCAD = db.Column(db.Integer)
    RCSI = db.Column(db.Integer)
    Total_who_accepted_CAOplace = db.Column(db.Integer)
    Total_progression = db.Column(db.Float(10))  # ?

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Model Pro2016 `{}`>".format(self.name)