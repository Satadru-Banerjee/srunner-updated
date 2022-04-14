  1 from imp import reload
  2 from weakref import ProxyType
  3 import uvicorn
  4 from fastapi import FastAPI, Request
  5 from pydantic import BaseModel
  6 import xml.etree.ElementTree as ET
  7 import simplejson as json
  8 from subprocess import call
  9 import time
 10 import glob
 11 import os
 12 import subprocess
 13 from subprocess import Popen, PIPE
 14 from typing import Dict, Any
 15 import _thread
 16
 17 #dir = "./scenario_output"
 18 #for f in os.listdir(dir):
 19  #   os.remove(os.path.join(dir, f))
 20
 21
 22 app =FastAPI()
 23
 24 def editXosc(sc_name, params, output_file_name):
 25     fileName = sc_name
 26     xmlTree = ET.parse(fileName)
 27     rootElement = xmlTree.getroot()
 28     #print(rootElement)
 29     xosc_tags = ["Weather","Sun","Fog","Precipitation","RoadCondition"]
 30     for xml_scenarios in rootElement.iter():
 31         param_tag=xml_scenarios.tag
 32         #cloudy_val = "free"
 33         #print(xml_scenarios.attrib)
 34         if xml_scenarios.tag == "RoadCondition":
 35             xml_scenarios.attrib["frictionScaleFactor"]=str(1-params['wetness']/100)
 36             #print(xml_scenarios.attrib)
 37         if xml_scenarios.tag == "Sun":
 38             val = params['sun_altitude_angle']
 39             xml_scenarios.attrib["azimuth"]=str(val)
 40
 41         if param_tag == "Fog":
 42             if params['fog_falloff '] == 0:
 43                 val = 100000.0
 44             elif params['fog_falloff '] in range(1,6):
 45                 val = 100-(params['fog_falloff ']*10)
 46             else:
 47                 val = 0
 48             xml_scenarios.attrib["visualRange"]=str(val)
 49
 50
 51         if param_tag == "Precipitation":
 52             if params['precipitation'] == 0:
 53                 p_type = "dry"
 54                 p_val = 0.0
 55             else:
 56                 p_type = "rain"
 57                 p_val = params['precipitation']
 58                 # cloudy_val = "rainy"
 59             xml_scenarios.attrib["precipitationType"]= p_type
 60             xml_scenarios.attrib["intensity"]= str(p_val)
 61
 62         if param_tag == "Weather":
 63             if params['precipitation']>0:
 64                 cloudy_val="rainy"
 65             elif params["cloudiness"]==0:
 66                 cloudy_val = "free"
 67             elif params["cloudiness"] in range(10,41):
 68                 cloudy_val = "cloudy"
 69             elif params["cloudiness"] in range(70,101):
 70                 cloudy_val = "overcast"
 71             xml_scenarios.attrib["cloudState"]=str(cloudy_val)
 72
 73     xmlTree.write("./outfiles/"+output_file_name+".xosc",encoding='UTF-8',xml_declaration=True)
 74
 75 @app.post("/executeScenario")
 76 def execution(request: Dict[Any,Any]):
 77     filepath = "FollowLeadingVehicle.xosc"
 78     scenario_details = request['scenario_details']
 79     test_id = []
 80
 81     param_dict = {}
 82     xosc_param = ["cloudiness","precipitation","sun_altitude_angle","wetness","fog_falloff "]
 83     for scenario in scenario_details:
 84         #print(scenario)
 85         if len(test_id) <= 1 :test_id.append(scenario['testcase_id'])
 86        # test_id = scenario['testcase_id']
 87         #print(test_id)
 88         param_dict = {}
 89         jsondata = scenario['parameters']
 90         for k in range(len(jsondata)):
 91             var = jsondata[k]["parameterPath"]
 92             #print(var)
 93                 #print("!!!!",k['parameterName'])
 94             varname = var.split("/")
 95             param = varname[len(varname)-1]
 96             numvar = jsondata[k]["value"]
 97             num = numvar[0]['numberValue']
 98             if param in xosc_param:
 99                 param_dict[param]=num
100
101         editXosc(filepath, param_dict, scenario['testcase_id'])
102     print(test_id)
103
104     #fileName = str(test_id)+".xosc"
105     #pythonFile = "outfiles\\"+str(fileName)
106     #pythonFile = pythonFile_1
107     #print(type(pythonFile))
108
109     time.sleep(15)
110     result = []
111     processes = []
112     for i in test_id:
113         print(i)
114         fileName = str(i)+".xosc"
115         print ("fileName"+fileName)
116         print("Test cases are generated now running a scenario")
117     #_thread.start_new_thread(os.system, ('sudo python3 scenario_runner.py --openscenario ./outfiles/b3e114f8b4df11ec91789138d96941ad.xosc --reloadWorld --output --json',))
118         _thread.start_new_thread(os.system, ('python3 manual_control.py -a',))
119         proc = subprocess.Popen(["sudo python3 scenario_runner.py --openscenario ./outfiles/"+fileName+" --reload --json --outputDir ./scenario_output"], stdout=subprocess.PIPE, shell=True)
120         proc.wait()
121     #cmd_list = ['python3','scenario_runner.py', '--openscenario',pythonFile, '--reloadWorld', '--output']
122     #proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
123     #proc = subprocess.Popen(["sudo python3 scenario_runner.py --openscenario"] + pythonFile, stdout=subprocess.PIPE)
124     #stdout = proc.stdout.read()
125        # (out, err) = proc.communicate()
126     #stdout = proc.stdout.read()
127         print("=============================")
128         #processes.append(proc)
129     #for p in processes:
130         (out, err) = proc.communicate()
131      #   if p.wait() != 0:
132
133       #      print("there was an error")
134         result.append(out)
135
136
137
138     return result
139
140 if __name__ == '__main__':
141         uvicorn.run("new_mutator_api:app", host="0.0.0.0", port=8001, log_level="info", reload=True)
~
~