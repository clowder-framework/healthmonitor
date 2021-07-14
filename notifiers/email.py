
import ruamel.yaml

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

import utils

mail_server = ""
servertype = ""
requesttimeout = 5
processingtimeout = 300


def report_email(host, test_groups, elapsed_time, log, mongoid):
    if mail_server:
        with open("test_extraction_data.yml", 'r') as f:
            recipients = ruamel.yaml.load(f, ruamel.yaml.RoundTripLoader)['watchers']
            msg = MIMEMultipart('alternative')

            msg['From'] = '"%s" <devnull@ncsa.illinois.edu>' % host

            if len(log['failures']) > 0 or len(log['errors']) > 0 or len(log['timeouts']) > 0:
                email_addresses = [r['address'] for r in recipients if r['get_failure'] is True]
                msg['Subject'] = "[%s] Clowder Tests Failures" % servertype
            elif len(log['skipped']) > 0:
                email_addresses = [r['address'] for r in recipients if r['get_success'] is True]
                msg['Subject'] = "[%s] Clowder Tests Skipped" % servertype
            else:
                email_addresses = [r['address'] for r in recipients if r['get_success'] is True]
                msg['Subject'] = "[%s] Clowder Tests Success" % servertype

            msg['To'] = ', '.join(email_addresses)

            # Plain Text version of the email message
            text = ""
            if args.url and mongoid:
                text += "Report          : %s/report.html?id=%s\n" % (args.url, mongoid)
            text += "Host            : %s\n" % host
            text += "Total Tests     : %d\n" % test_groups['total']
            text += "Failures        : %d\n" % len(log['failures'])
            text += "Errors          : %d\n" % len(log['errors'])
            text += "Timeouts        : %d\n" % len(log['timeouts'])
            text += "Skipped         : %d\n" % len(log['skipped'])
            text += "Success         : %d\n" % len(log['success'])
            text += "Clowder Broken  : %d\n" % test_groups['clowder']
            text += "Elapsed time    : %5.2f seconds\n" % elapsed_time
            if len(log['failures']) > 0:
                text += '++++++++++++++++++++++++++++ FAILURES ++++++++++++++++++++++++++++++++\n'
                for logmsg in log['failures']:
                    text += logmsg_str(logmsg)
            if len(log['errors']) > 0:
                text += '++++++++++++++++++++++++++++ ERRORS ++++++++++++++++++++++++++++++++++\n'
                for logmsg in log['errors']:
                    text += logmsg_str(logmsg)
            if len(log['timeouts']) > 0:
                text += '++++++++++++++++++++++++++++ TIMEOUTS ++++++++++++++++++++++++++++++++\n'
                for logmsg in log['timeouts']:
                    text += logmsg_str(logmsg)
            if len(log['skipped']) > 0:
                text += '++++++++++++++++++++++++++++ SKIPPED +++++++++++++++++++++++++++++++++\n'
                for logmsg in log['skipped']:
                    text += logmsg_str(logmsg)
            # if len(log['success']) > 0:
            #    body += '++++++++++++++++++++++++++++ SUCCESS +++++++++++++++++++++++++++++++++\n'
            #    for logmsg in log['success']:
            #        body += logmsg_str(logmsg)
            msg.attach(MIMEText(text, 'plain'))

            # HTML version of the email message
            text = "<html><head></head><body>\n"
            text += "<table border=0>\n"
            if args.url and mongoid:
                text += "<tr><th align='left'>Report</th><td><a href='%s/report.html?id=%s'>%s</a></td></tr>\n" % \
                        (args.url, mongoid, mongoid)
            text += "<tr><th align='left'>Host</th><td>%s</td></tr>\n" % host
            text += "<tr><th align='left'>Total Tests</th><td>%d</td></tr>\n" % test_groups['total']
            text += "<tr><th align='left'>Failures</th><td>%d</td></tr>\n" % len(log['failures'])
            text += "<tr><th align='left'>Errors</th><td>%d</td></tr>\n" % len(log['errors'])
            text += "<tr><th align='left'>Timeouts</th><td>%d</td></tr>\n" % len(log['timeouts'])
            text += "<tr><th align='left'>Skipped</th><td>%d</td></tr>\n" % len(log['skipped'])
            text += "<tr><th align='left'>Success</th><td>%d</td></tr>\n" % len(log['success'])
            text += "<tr><th align='left'>Clowder Tests Broken</th><td>%d</td></tr>\n" % test_groups['clowder']
            text += "<tr><th align='left'>Elapsed time</th><td>%5.2f seconds</td></tr>\n" % elapsed_time
            text += "</table>\n"
            if len(log['failures']) > 0:
                text += '<h2>FAILURES</h2>\n'
                for logmsg in log['failures']:
                    text += utils.logmsg_html(logmsg)
            if len(log['errors']) > 0:
                text += '<h2>ERRORS</h2>\n'
                for logmsg in log['errors']:
                    text += utils.logmsg_html(logmsg)
            if len(log['timeouts']) > 0:
                text += '<h2>TIMEOUTS</h2>\n'
                for logmsg in log['timeouts']:
                    text += utils.logmsg_html(logmsg)
            if len(log['skipped']) > 0:
                text += '<h2>SKIPPED</h2>\n'
                for logmsg in log['skipped']:
                    text += utils.logmsg_html(logmsg)
            text += "</body></html>"
            msg.attach(MIMEText(text, 'html'))

            # send the actual message
            mailserver = SMTP(mail_server)
            mailserver.sendmail(msg['From'], email_addresses, msg.as_string())
            mailserver.quit()
