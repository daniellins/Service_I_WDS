import requests
import untangle
import numpy
from geojson import Point
import json
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS, cross_origin
from flask import request



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\sqlitedbs\\wds.db'
db = SQLAlchemy(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projid = db.Column(db.String)
    nbc = db.Column(db.Numeric)
    sbc = db.Column(db.Numeric)
    ebc = db.Column(db.Numeric)
    wbc = db.Column(db.Numeric)
    centerx = db.Column(db.Numeric)
    centery = db.Column(db.Numeric)
    title = db.Column(db.String)
    author = db.Column(db.String)
    abstract = db.Column(db.String)
    update_data = db.Column(db.String)
    network_url  = db.Column(db.String)
    data_url = db.Column(db.String)

    def __init__(self, projid, nbc, sbc, ebc, wbc, centerx, centery, title, author, abstract, update_data, network_url, data_url):
        self.projid = projid
        self.nbc = nbc
        self.sbc = sbc
        self.ebc = ebc
        self.wbc = wbc
        self.centerx = centerx
        self.centery = centery
        self.title = title
        self.author = author
        self.abstract = abstract
        self.update_data = update_data
        self.network_url = network_url
        self.data_url = data_url

    def __repr__(self, projid, nbc, sbc, ebc, wbc, centerx, centery, title, author, abstract, update_data, network_url, data_url):

        return '<Project %r>' % self.projid
        return '<Project %r>' % self.nbc
        return '<Project %r>' % self.sbc
        return '<Project %r>' % self.ebc
        return '<Project %r>' % self.wbc
        return '<Project %r>' % self.centerx
        return '<Project %r>' % self.centery
        return '<Project %r>' % self.title
        return '<Project %r>' % self.author
        return '<Project %r>' % self.abstract
        return '<Project %r>' % self.update_data
        return '<Project %r>' % self.network_url
        return '<Project %r>' % self.data_url


@app.route('/drop-db')
def drop_db_sql():
    db.drop_all()
    db.session.commit()
    return "dropped"


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route("/usgs/metadata/")
@cross_origin()
def test():
    query = request.args.get('q')
    result = []
    result_map  = []
    url = "http://mercury-ops2.ornl.gov/usgssolr4/core1/select/"

    param2 = "geo:\"intersects(" + query + ")\""
    param3 = "*:*"
    payload = {"fq": param2, "q": param3, "start": 0,  "rows": 1000}
    r = requests.get(url, params=payload)

    # faz o parsing do XML
    obj = untangle.parse(r.content)

    for doc in obj.response.result.doc:
        missing_bboxinfo = doc.str[7].cdata # Does not the file contain bounding box info?

        if unicode.lower(missing_bboxinfo) == "false":
            projid = doc.str[0].cdata  # id
            nbc = float(doc.float[0].cdata)  # northBoundCoord //latitude
            sbc = float(doc.float[1].cdata)  # southBoundCoord //latitude
            ebc = float(doc.float[2].cdata)  # eastBoundCoord //longitude
            wbc = float(doc.float[3].cdata)  # westBoundCoord //longitude
            title = doc.str[12].cdata
            author = doc.arr[16].cdata
            abstract = doc.str[11].cdata
            update_data = doc.str[0].cdata
            network_url = doc.arr[9].cdata
            data_url = doc.arr[10].cdata

            ## obtain the centroid (based on http://gis.stackexchange.com/questions/64119/center-of-a-bounding-box_
            coords = (wbc, ebc, sbc, nbc)
            centerx,centery = (numpy.average(coords[:2]),numpy.average(coords[2:]))

            db.create_all()

            projectitr = Project(projid, nbc, sbc, ebc, wbc, centerx, centery, title, author, abstract, update_data, network_url, data_url)

            db.session.add(projectitr)
            db.session.commit()

            #result_map.append({"properties": {"id": projid}, "geometry": Point((centery, centerx))})

            result_map.append({"properties": {"id": id}, "geometry": Point((centery, centerx))})
    print json.dumps(result_map)
    return json.dumps(result_map)



@app.route('/usgs/metadata/get-details/<id>')
def get_details(id):
    from ws import Project
    details = Project.query.filter_by(projid=id).first()

    result = {}
    result["projid"] = details.projid
    result["nbc"] = str(details.nbc)
    result["sbc"] = str(details.sbc)
    result["ebc"] = str(details.ebc)
    result["wbc"] = str(details.wbc)
    result["title"] = details.title
    result["author"] = details.author
    result["abstract"] = details.abstract
    result["update_data"] = details.update_data
    result["network_url"] = details.network_url
    result["data_url"] = details.data_url

    return json.dumps(result)


if __name__ == '__main__':
    app.run()