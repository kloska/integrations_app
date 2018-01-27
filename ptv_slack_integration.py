from hashlib import sha1
from secrets import PTV_DEVID, PTV_KEY, SLACK_TOKEN # secrets module not under git control
import hmac
import requests
import json

def ptv_queryDisruptions(route_id):
 base_url = 'https://timetableapi.ptv.vic.gov.au'
 api_request = '/v3/disruptions/route/{}'.format(route_id) 
 
 ptv_query_string = '{}?devid={}'.format(api_request, PTV_DEVID)
 ptv_query_string_encoded = ptv_query_string.encode('utf-8')

 signature = hmac.new(PTV_KEY, ptv_query_string_encoded, sha1)

 ptv_api_request = '{}{}&signature={}'.format(base_url, ptv_query_string, signature.hexdigest())

 r = requests.get(ptv_api_request)
 print('Requested API URL: ', ptv_api_request)
 print('Status Code: ', r.status_code)

 return r

def slack_postMessage(attachments):
 method_url = 'https://slack.com/api/chat.postMessage?'
 token_parameter = 'token={}'.format(SLACK_TOKEN)
 channel_parameter = '&channel={}'.format(slack_user_id) 
 attachments_parameter = '&attachments={}'.format(json.dumps([attachments]))
 pretty_parameter = '&pretty=1'

 slack_post_url = method_url + token_parameter + channel_parameter + attachments_parameter + pretty_parameter

 r = requests.post(slack_post_url)
 
 return r.json()

def slack_disruptionAlertFormatted(disruptions_count, disruptions_title, route_id, user_id):
 fields = []
 
 # attachments dictionary will be returned and incldues formatted Slack alert
 attachments = {'fallback': 'PTV Disruptions Alert'}

 # Construct Slack Notification
 if disruptions_count == 0:
  attachments["color"] = "good"
  fields.append( {"title": "Hurray, no disruptions on the Metro line!" })
  attachments["fields"] = fields
 else:
  for disruption in disruptions_title:
   fields.append({ 'title': disruption })
  
  attachments["color"] = "danger"
  attachments["pretext"] = "We detected {} disruption(s) on the Metro line".format(disruptions_count)
  attachments["fields"] = fields

  return attachments


##################################
#
# Main Script
#
##################################

route_id = 11 			# 11 = Pakenham Line
slack_user_id = 'C8FLDM7FZ' 	#Slack Channel / User ID to be alerted

r = ptv_queryDisruptions(route_id)
 
if r.status_code == 200:
 # Convert JSON response to Python dictionary and access values
 metro_train_disruptions = r.json()['disruptions']['metro_train'] 
 print('There are currently {} disruptions'.format(len(metro_train_disruptions)))
 
 #Loop through disruptions list and print disruptions title
 disruption_titles = []
 for disruption in metro_train_disruptions:
  print('* {}'.format(disruption['title']))
  disruption_titles.append(disruption['title'])

 disruptions_alert = slack_disruptionAlertFormatted(len(metro_train_disruptions), disruption_titles, route_id, slack_user_id)
 slack_status = slack_postMessage(disruptions_alert)

 if slack_status['ok'] == True:
  print('PTV alert sent to Slack user.')
 else:
  print('Slack error while send message: ', slack_status['error'])

else:
 print('PTV GET request not successful.')
