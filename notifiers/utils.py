import logging
import json


def logmsg_str(logmsg):
    result = "Name       : %s\n" % logmsg['name']
    result += "Classname  : %s\n" % logmsg['classname']
    result += "time       : %5.2f seconds\n" % logmsg['time']
    if 'message' in logmsg:
        result += "Message    : %s\n" % logmsg['message']
    if 'system-out' in logmsg:
        result += "system out :\n%s\n" % logmsg['system-out']
    if 'system-err' in logmsg:
        result += "system err :\n%s\n" % logmsg['system-err']
    result += "----------------------------------------------------------------------\n"
    return result


def logmsg_html(logmsg):
    result = "<table border=0>\n"
    result += "<tr><th align='left'>Name</th><td>%s</td></tr>\n" % logmsg['name']
    result += "<tr><th align='left'>Classname</th><td>%s</td></tr>\n" % logmsg['classname']
    result += "<tr><th align='left'>Time</th><td>%5.2f seconds</td></tr>\n" % logmsg['time']
    if 'message' in logmsg:
        text = logmsg['message'].replace("\n", "<br/>\n")
        result += "<tr><th align='left' valign='top'>Message</th><td>%s</td></tr>\n" % text
    if 'system-out' in logmsg:
        text = logmsg['system-out'].replace("\n", "<br/>\n")
        result += "<tr><th align='left' valign='top'>System Out</th><td>%s</td></tr>\n" % text
    if 'system-err' in logmsg:
        text = logmsg['system-err'].replace("\n", "<br/>\n")
        result += "<tr><th align='left' valign='top'>System Err</th><td>%s</td></tr>\n" % text
    result += "</table>\n"
    result += "<hr/>"
    return result


