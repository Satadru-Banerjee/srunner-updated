ssm-user@ip-10-0-0-51:/var/snap/amazon-ssm-agent/5163/scenario_runner$ cat mutator_api.py
from imp import reload
from weakref import ProxyType
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
import xml.etree.ElementTree as ET
import simplejson as json
from subprocess import call
import time
import glob
import os
import subprocess
from subprocess import Popen, PIPE
from typing import Dict, Any
import _thread

app =FastAPI()

def editXosc(sc_name, params, output_file_name):
    fileName = sc_name
    xmlTree = ET.parse(fileName)
    rootElement = xmlTree.getroot()
    #print(rootElement)
    xosc_tags = ["Weather","Sun","Fog","Precipitation","RoadCondition"]
    for xml_scenarios in rootElement.iter():
        param_tag=xml_scenarios.tag
        #cloudy_val = "free"
        #print(xml_scenarios.attrib)
        if xml_scenarios.tag == "RoadCondition":
            xml_scenarios.attrib["frictionScaleFactor"]=str(1-params['wetness']/100)
            #print(xml_scenarios.attrib)
        if xml_scenarios.tag == "Sun":
            val = params['sun_altitude_angle']
            xml_scenarios.attrib["azimuth"]=str(val)

        if param_tag == "Fog":
            if params['fog_falloff '] == 0:
                val = 100000.0
            elif params['fog_falloff '] in range(1,6):
                val = 100-(params['fog_falloff ']*10)
            else:
                val = 0
            xml_scenarios.attrib["visualRange"]=str(val)


        if param_tag == "Precipitation":
            if params['precipitation'] == 0:
                p_type = "dry"
                p_val = 0.0
            else:
                p_type = "rain"
                p_val = params['precipitation']
                # cloudy_val = "rainy"
            xml_scenarios.attrib["precipitationType"]= p_type
            xml_scenarios.attrib["intensity"]= str(p_val)

        if param_tag == "Weather":
            if params['precipitation']>0:
                cloudy_val="rainy"
            elif params["cloudiness"]==0:
                cloudy_val = "free"
            elif params["cloudiness"] in range(10,41):
                cloudy_val = "cloudy"
            elif params["cloudiness"] in range(70,101):
                cloudy_val = "overcast"
            xml_scenarios.attrib["cloudState"]=str(cloudy_val)

    xmlTree.write("./outfiles/"+output_file_name+".xosc",encoding='UTF-8',xml_declaration=True)

@app.post("/executeScenario")
def execution(request: Dict[Any,Any]):
    filepath = "FollowLeadingVehicle.xosc"
    scenario_details = request['scenario_details']
    test_id = []

    param_dict = {}
    xosc_param = ["cloudiness","precipitation","sun_altitude_angle","wetness","fog_falloff "]
    for scenario in scenario_details:
        #if len(test_id) < 5 :
         #   test_id.append(scenario['testcase_id'])
        test_id = scenario['testcase_id']
        #print(test_id)
        param_dict = {}
        jsondata = scenario['parameters']
        for k in range(len(jsondata)):
            var = jsondata[k]["parameterPath"]
            #print(var)
                #print("!!!!",k['parameterName'])
            varname = var.split("/")
            param = varname[len(varname)-1]
            numvar = jsondata[k]["value"]
            num = numvar[0]['numberValue']
            if param in xosc_param:
                param_dict[param]=num

        editXosc(filepath, param_dict, scenario['testcase_id'])
    print(test_id)

    fileName = str(test_id)+".xosc"
    #pythonFile = "outfiles\\"+str(fileName)
    #pythonFile = pythonFile_1
    #print(type(pythonFile))

    time.sleep(15)
    #result = []
    #for i in test_id:
     #   fileName = str(test_id)+".xosc"
    print("Test cases are generated now running a scenario")
    #_thread.start_new_thread(os.system, ('sudo python3 scenario_runner.py --openscenario ./outfiles/b3e114f8b4df11ec91789138d96941ad.xosc --reloadWorld --output --json',))
    _thread.start_new_thread(os.system, ('python3 manual_control.py -a',))
    proc = subprocess.Popen(["sudo python3 scenario_runner.py --openscenario ./outfiles/"+fileName+" --reload --json --output"], stdout=subprocess.PIPE, shell=True)
    #cmd_list = ['python3','scenario_runner.py', '--openscenario',pythonFile, '--reloadWorld', '--output']
    #proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
    #proc = subprocess.Popen(["sudo python3 scenario_runner.py --openscenario"] + pythonFile, stdout=subprocess.PIPE)
    #stdout = proc.stdout.read()
    (out, err) = proc.communicate()
    #stdout = proc.stdout.read()
    print("=============================")
    #result.append(out)



    return out

if __name__ == '__main__':
        uvicorn.run("mutator_api:app", host="0.0.0.0", port=8001, log_level="info", reload=True)