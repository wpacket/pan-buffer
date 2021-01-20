#!/usr/bin/env python
import ssl
import time
import datetime
import urllib3
import requests
import sys
import xml.etree.ElementTree as ET

if __name__ == "__main__":
  
  #---------------------------------------------------------------------------------------------------------------------------------------------------
  # Mandatory : Put your API_KEY , FIREWALL IP. 
  # Optional  : Change  the sleep_delay between each API request ( in sec ) and the minimum Buffer/CPU threshold to trigger the  event ( in % )

  api_key                 = "PUT_YOUR_API_KEY_HERE"
  fw_ip_address           = "PUT_YOUR_FIREWALL_IP_HERE"
  sleep_delay             = 5
  cpu_low_limit           = 50
  log_file                = "./pan_buffer.log"
  get_backlog_xml         = "<show><running><resource-monitor><ingress-backlogs/></resource-monitor></running></show>"
  get_session_xml         = "<show><session><id>%s</id></session></show>"
  
  session_id              = None  
  #---------------------------------------------------------------------------------------------------------------------------------------------------

  while 1>0:
  
    try:
      
      urllib3.disable_warnings()

      api_url_cpu               = "https://"+fw_ip_address+"/api/?type=op&cmd="+get_backlog_xml+"&key="+api_key
      api_request_cpu           = requests.get(url=api_url_cpu,verify=False)
      api_response_cpu          = api_request_cpu.text
      xml_tree_root_cpu         = ET.fromstring(api_response_cpu)

      for top_sessions in xml_tree_root_cpu.findall("./result/entry/TOP-SESSION/entry"):	

        session_id              = None

        for sess_attributes in top_sessions.findall("./"):

          if sess_attributes.tag == "SESS-ID":

            session_id          = sess_attributes.text
            api_url_session     = "https://"+fw_ip_address+"/api/?type=op&cmd="+get_session_xml % (session_id)+"&key="+api_key
            api_request_sess    = requests.get(url=api_url_session,verify=False)
            api_response_sess   = api_request_sess.text
            xml_tree_root_sess  = ET.fromstring(api_response_sess)

            session_src         = xml_tree_root_sess.findall("./result/c2s/source")[0].text
            session_dst         = xml_tree_root_sess.findall("./result/c2s/dst")[0].text
            session_port        = xml_tree_root_sess.findall("./result/c2s/dport")[0].text
            session_sz          = xml_tree_root_sess.findall("./result/c2s/source-zone")[0].text
            session_dz          = xml_tree_root_sess.findall("./result/s2c/source-zone")[0].text
            session_app         = xml_tree_root_sess.findall("./result/application")[0].text

          if sess_attributes.tag == "PCT":
            cpu_usage = sess_attributes.text

          if session_id != None:
            if int(cpu_usage) > cpu_low_limit:
              f = open(log_file, "a")
              f.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M')) + ": "+ "Session ID ="+session_id+"  ("+session_sz+")"+ session_src +" -> "+"("+session_dz+")"+session_dst+":"+session_port+" APP="+session_app+"\n")
              f.write("Packet Buffer Usage: "+cpu_usage+"%\n\n")
              f.close()

      time.sleep(sleep_delay)

    except:
      f = open(log_file, "a")
      f.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M')) +" Connection Error.\n")
      f.close()

