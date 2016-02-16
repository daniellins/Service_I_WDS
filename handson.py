from flask import Flask
from flask import request
import requests
import untangle
import numpy
from geojson import Point
import json
from flask.ext.cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/usgs/metadata/")
@cross_origin()
def test():
    query = request.args.get('q')
    result = []
    result_map = []
    url = "http://mercury-ops2.ornl.gov/usgssolr4/core1/select/"

    param2 = "geo:\"intersects(" + query + ")\""
    param3 = "*:*"
    payload = {"fq": param2, "q": param3, "start": 500,  "rows": 1000}
    r = requests.get(url, params=payload)
    print r.url
    # faz o parsing do XML
    obj = untangle.parse(r.content)
    print len(obj.response.result.doc)

    for doc in obj.response.result.doc:

        missing_bboxinfo = doc.str[7].cdata # Does not the file contain bounding box info?

        if unicode.lower(missing_bboxinfo) == "false":
            id = doc.str[0].cdata  # id
            nbc = float(doc.float[0].cdata)  # northBoundCoord //latitude
            sbc = float(doc.float[1].cdata)  # southBoundCoord //latitude
            ebc = float(doc.float[2].cdata)  # eastBoundCoord //longitude
            wbc = float(doc.float[3].cdata)  # westBoundCoord //longitude

        # obtain the centroid
        # (based on http://gis.stackexchange.com/questions/64119/center-of-a-bounding-box_

            coords = (wbc, ebc, sbc, nbc)
            centerx,centery = (numpy.average(coords[:2]),numpy.average(coords[2:]))

            result.append({"lon": centery, "lat": centerx, "id": id})
            result_map.append({"properties": {"id": id}, "geometry": Point((centery, centerx))})

    return json.dumps(result_map)

if __name__ == '__main__':
    app.run()

#
# def calculate_polygon_area(polygon, signed=False):
#     """Calculate the signed area of non-self-intersecting polygon
#     Input
#         polygon: Numeric array of points (longitude, latitude). It is assumed
#                  to be closed, i.e. first and last points are identical
#         signed: Optional flag deciding whether returned area retains its sign:
#                 If points are ordered counter clockwise, the signed area
#                 will be positive.
#                 If points are ordered clockwise, it will be negative
#                 Default is False which means that the area is always positive.
#     Output
#         area: Area of polygon (subject to the value of argument signed)
#     """
#
#     # Make sure it is numeric
#     P = numpy.array(polygon)
#
#     # Check input
#     msg = ('Polygon is assumed to consist of coordinate pairs. '
#            'I got second dimension %i instead of 2' % P.shape[1])
#     assert P.shape[1] == 2, msg
#
#     msg = ('Polygon is assumed to be closed. '
#            'However first and last coordinates are different: '
#            '(%f, %f) and (%f, %f)' % (P[0, 0], P[0, 1], P[-1, 0], P[-1, 1]))
#     assert numpy.allclose(P[0, :], P[-1, :]), msg
#
#     # Extract x and y coordinates
#     x = P[:, 0]
#     y = P[:, 1]
#
#     # Area calculation
#     a = x[:-1] * y[1:]
#     b = y[:-1] * x[1:]
#     A = numpy.sum(a - b) / 2.
#
#     # Return signed or unsigned area
#     if signed:
#         return A
#     else:
#         return abs(A)
#
#
# def calculate_polygon_centroid(polygon):
#     """Calculate the centroid of non-self-intersecting polygon
#     Input
#         polygon: Numeric array of points (longitude, latitude). It is assumed
#                  to be closed, i.e. first and last points are identical
#     Output
#         Numeric (1 x 2) array of points representing the centroid
#     """
#
#     # Make sure it is numeric
#     P = numpy.array(polygon)
#
#     # Get area - needed to compute centroid
#     A = calculate_polygon_area(P, signed=True)
#
#     # Extract x and y coordinates
#     x = P[:, 0]
#     y = P[:, 1]
#
#     # Exercise: Compute C as shown in http://paulbourke.net/geometry/polyarea
#     a = x[:-1] * y[1:]
#     b = y[:-1] * x[1:]
#
#     cx = x[:-1] + x[1:]
#     cy = y[:-1] + y[1:]
#
#     Cx = numpy.sum(cx * (a - b)) / (6. * A)
#     Cy = numpy.sum(cy * (a - b)) / (6. * A)
#
#     # Create Nx2 array and return
#     C = numpy.array([Cx, Cy])
#     return C
