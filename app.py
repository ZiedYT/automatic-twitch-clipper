from flask import Flask
from main import mainApp


content="""
<html>
<head>
    <meta http-equiv="Refresh" content="1">
    <meta charset="UTF-8">
    <style> 
    .styled-table {border-collapse: collapse;margin: 25px 0;font-size: 0.9em;font-family: sans-serif;
    min-width: 400px;box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);}
    .styled-table thead tr {background-color: #009879;color: #ffffff;text-align: left;}
    .styled-table th,.styled-table td {padding: 12px 15px;}
    .styled-table tbody tr {border-bottom: 1px solid #dddddd;}
    .styled-table tbody tr:nth-of-type(even) {background-color: #f3f3f3;}
    .styled-table tbody tr:last-of-type {border-bottom: 2px solid #009879;}
    .button {width:80px;padding:.5em;background-color:#32CD32;color:#fff;border-radius:4px;box-shadow:0 4px 6px rgba(50,50,93,.11), 0 1px 3px rgba(0,0,0,.08);text-decoration:none}
    .buttonFail {width:80px;padding:.5em;background-color:#AA4A44;color:#fff;border-radius:4px;box-shadow:0 4px 6px rgba(50,50,93,.11), 0 1px 3px rgba(0,0,0,.08);text-decoration:none} 
    </style>
    <table class="styled-table">
    [[SUMMARY]]
    </table>
</head>
<body>
</body>
</html>
"""

def htmlBuilder(summary):
    summaryBody=""
    for clipper in summary:
        stream=clipper["stream"]
        chat=clipper["chat"]
        status=clipper["status"]
        on="Offline"
        if(status):
            on="Online"
        summaryBody+="<thead><tr><td>Clipper</td><td>stream: {}</td><td>status:  {}</td><td>chat:  {}</thead>".format(stream,on,chat)
        for detector in clipper["detectors"]:
            detectorname = detector["name"].encode('ascii', 'xmlcharrefreplace')
            # msg= detector["msg"].encode('ascii', 'xmlcharrefreplace')
            summaryBody+="<tr><th>Detector</th><th>Name: {}</th><th>Uplaoding: {}</th><th></th></tr>".format(detectorname,detector["uplaoding"])
            for scenario in detector["scenarios"]:
                index= scenario["index"]
                summaryBody+="<tr><td>Scenario {}</td><td>----</td><td></td><td></td></tr>".format(index)
                for counter in scenario["counters"]:
                    summaryBody+="<tr><td></td><td>Counter: {}</td><td>Count: {}</td><td>Last: {}</td></tr>".format(counter["name"],counter["count"],counter["last"])

    # with open("index.html","w") as file:
    #     print("saving")
    #     file.write(content.replace("[[SUMMARY]]", summaryBody))
    #     file.close()
    return content.replace("[[SUMMARY]]", summaryBody)

app = Flask(__name__)
@app.route('/')
def hello():
    summary=mainapp.summary()
    page=htmlBuilder(summary)
    return page

import flask.cli    
flask.cli.show_server_banner = lambda *args: None

import logging
logging.getLogger("werkzeug").disabled = True


if __name__ == '__main__':
    mainapp=mainApp()
    app.run( host="localhost", port=8080,debug=True,use_reloader=False)