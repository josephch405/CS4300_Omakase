from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Omakase"
net_ids = [
    "Ryan Curtis: rec284",
    "Danyal Motiwalla: djm453",
    "Jessica Wu: jlw377",
    "Tyler Ishikawa: tyi3",
    "Joseph Chuang: jcc436"]


@irsystem.route('/', methods=['GET'])
def search():
    query = request.args.get('search')
    if not query:
        data = []
        output_message = ''
    else:
        output_message = "Your search: " + query
        data = range(5)
    return render_template('search.html', name=project_name, netids=net_ids, output_message=output_message, data=data)
