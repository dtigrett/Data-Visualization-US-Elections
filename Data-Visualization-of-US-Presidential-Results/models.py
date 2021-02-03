#def create_classes(db):
#    class us_election_result(db.Model):
#        __tablename__ = 'us_election_results'
#        id = db.Column(db.Float, primary_key=True)
#        year = db.Column(db.Integer)
#        state_name = db.Column(db.String(255))
#        state_abbr = db.Column(db.String(255))
#        combined_fips = db.Column(db.Integer)
#        county_name = db.Column(db.String(255))
#        county_fips = db.Column(db.Integer)
#        votes_dem = db.Column(db.Integer)
#        votes_gop = db.Column(db.Integer)
#        total_votes = db.Column(db.Integer)
#        diff = db.Column(db.Integer)
#        per_dem = db.Column(db.Float)
#        per_gop = db.Column(db.Float)
#        per_point_diff = db.Column(db.Float)

#        def __repr__(self):
#            return '<us_election_result %r>' % (self.name)

#    return us_election_result

#    class Pet(db.Model):
#        __tablename__ = 'pets'
#
#        id = db.Column(db.Integer, primary_key=True)
#        name = db.Column(db.String(64))
#        lat = db.Column(db.Float)
#        lon = db.Column(db.Float)

#        def __repr__(self):
#            return '<Pet %r>' % (self.name)

    # Creates Classes which will serve as the anchor points for our Tables
#    class Dog(Base):
#        __tablename__ = 'dog'
#        id = Column(Integer, primary_key=True)
#        name = Column(String(255))
#        color = Column(String(255))
#        age = Column(Integer)

#        def __repr__(self):
#            return '<Dog %r>' % (self.name)

#    class Cat(Base):
#        __tablename__ = 'cat'
#        id = Column(Integer, primary_key=True)
#        name = Column(String(255))
#        color = Column(String(255))
#        age = Column(Integer)
        
#        def __repr__(self):
#            return '<Cat %r>' % (self.name)
    
