
import requests, json, sys, re, time, os, warnings, argparse

from datetime import datetime

warnings.filterwarnings("ignore")

parser=argparse.ArgumentParser(description="Python script using Redfish API to get all BIOS attributes or get current value for one specific attribute")
#parser.add_argument('-ip',help='iDRAC IP address', required=True)
parser.add_argument('-u', help='username', required=False, default='root')
parser.add_argument('-p', help='password', required=False, default='password')
parser.add_argument('-a', help='Pass in the attribute name you want to get the current value, Note: make sure to type the attribute name exactly due to case sensitive. Example: MemTest will work but memtest will fail', required=False)
parser.add_argument("ip",type=str,help='iDRAC/iLO/BMC IP address')

                    
args=vars(parser.parse_args())

ip=args["ip"]
username=args["u"]
password=args["p"]

try:
    os.remove("bios_attributes.txt")
except:
    pass

def get_response(url):
    response = requests.get(url,verify=False,auth=(username, password))
    
    try:
        data = response.json()
        return data
        
    except ValueError:
        if response.status_code != 200:
            print('Received ' + str(response.status_code) + ' from ' + url)
            sys.exit()
        
  # handle 401 unauthorized and 404 page not found


def get_bios_attributes():
    f=open("bios_attributes.txt","a")
    #response = requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/Bios' % idrac_ip,verify=False,auth=(idrac_username,idrac_password))
    response = requests.get('https://%s/redfish/v1/Systems/1/Bios' % ip,verify=False,auth=(username, password))
    data = response.json()
    d=datetime.now()
    current_date_time="- Data collection timestamp: %s-%s-%s  %s:%s:%s\n" % (d.year,d.month,d.day, d.hour,d.minute,d.second)
    f.writelines(current_date_time)
    a="\n--- BIOS Attributes ---\n"
    print(a)
    f.writelines(a)
    for i in data[u'Attributes'].items():
        attribute_name = "Attribute Name: %s\t" % (i[0])
        f.writelines(attribute_name)
        attribute_value = "Attribute Value: %s\n" % (i[1])
        f.writelines(attribute_value)
        print("Attribute Name: %s\t Attribute Value: %s" % (i[0],i[1]))
        
    print("\n- Attributes are also captured in \"bios_attributes.txt\" file")
    f.close()

def get_specific_bios_attribute():
    #response = requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/Bios' % idrac_ip,verify=False,auth=(idrac_username,idrac_password))
    response = requests.get('https://%s/redfish/v1/Systems/1/Bios' % ip,verify=False,auth=(username, password))
    data = response.json()
    for i in data[u'Attributes'].items():
        if i[0] == args["a"]:
            print("\n- Current value for attribute \"%s\" is \"%s\"\n" % (args["a"], i[1]))
            sys.exit()
    print("\n- FAIL, unable to get attribute current value. Either attribute doesn't exist for this BIOS version, typo in attribute name or case incorrect")
    sys.exit()
    
    
def write_json(file,data):
    valid_file_name = re.sub('[^\w_.)( -]', '', file)
    f=open(f'{valid_file_name}',"a")
    
    d=datetime.now()
    current_date_time="- Data collection timestamp: %s-%s-%s  %s:%s:%s\n" % (d.year,d.month,d.day, d.hour,d.minute,d.second)
    f.writelines(current_date_time)        
    f.writelines(json.dumps(data, sort_keys=True, indent=4))

    print(f"\n- Attributes are also captured in {valid_file_name}")
    f.close()


if __name__ == "__main__":

    #data=get_response(f"https://192.168.200")
    #print (data)
    #dell https://{ip}/redfish/v1
    data=get_response(f"https://{ip}/rest/v1")
    systems=data["Systems"]["@odata.id"]
    write_json("/rest/v1",data)

    data=get_response(f"https://{ip}{systems}")
    members=data["Members"]
    write_json(systems,data)
    
    for member in members:
        memberEnum=member["@odata.id"]
        data=get_response(f'https://{ip}{memberEnum}')
        write_json(memberEnum,data)
        
        memberBios=data["Bios"]["@odata.id"]
        data=get_response(f'https://{ip}{memberBios}')
        #print(data)
        write_json(memberBios,data)
    #if args["a"]:
       #get_specific_bios_attribute()
    #else:
        #get_bios_attributes()
    
