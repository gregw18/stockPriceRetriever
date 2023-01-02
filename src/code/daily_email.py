"""
Function to create and send email summarizing the prices that were just downloaded.
Runs automatically from lambda, after downloading.
Creates string containing summary of downloaded prices, publishes to an SNS topic as
an email.
V0.01, October 13, 2020
"""

#from memory_profiler import profile
#from guppy import hpy
#import sys

import notification_interface
from securities import Securities
import security_groups
import sprEnums


code_display_names = {sprEnums.GroupCodes.buy: "Buy",
                      sprEnums.GroupCodes.near_buy: "Near buy",
                      sprEnums.GroupCodes.middle: "Middle",
                      sprEnums.GroupCodes.near_sell: "Near sell",
                      sprEnums.GroupCodes.sell: "Sell"
                      }

#@profile
def send_from_db(resultsTopicName):
    """
    Create and send email summarizing price data from db, after first checking
    that have most recent prices downloaded. 
    Usually runs once a day, called by the lambda.
    """
    #h = hpy()
    #print(f"send_from_db hpy 1: {h.heap()}")
    sent = False
    print("Starting daily_email.send_from_db")

    mySecurities = Securities()
    #print(f"send_from_db hpy 2: {h.heap()}")
    #print(f"Initial size of securities: {sys.getsizeof(mySecurities)}")
    mySecurities.do_daily_updates()
    #print(f"send_from_db hpy 3: {h.heap()}")
    #print(f"After update size of securities: {sys.getsizeof(mySecurities)}")
    securitiesList = mySecurities.retrieve_email_info()
    #print(f"send_from_db hpy 4: {h.heap()}")
    #print(f"After email size of securities: {sys.getsizeof(mySecurities)}")
    if len(securitiesList) > 0:
        _generate_and_send(securitiesList, resultsTopicName)
        sent = True
    else:
        print("Didn't find any securities to send an email regarding.")
    #print(f"send_from_db hpy 5: {h.heap()}")
    print("finished deaily_email.send_from_db")
    
    return sent

def send_from_file(myResultsFile, resFile, resultsTopicName):
    """
    Create and send email summarizing price data from given results file. Usually runs once
    a day, after retrieving prices, called by the lambda.
    Receives resultsFile class, name of results file to work with, name of topic to send
    results to.
    """
    print("Starting daily_email.send_from_file")

    securitiesList = myResultsFile.read_results_file_s3(resFile)
    _generate_and_send(securitiesList, resultsTopicName)

def _generate_and_send(securitiesList, resultsTopicName):
    """
    Receives list of security, uses that to generate and send email.
    """
    print(f"starting daily_email._generate_and_send, len={len(securitiesList)}")
    myGroups = security_groups.security_groups()
    myGroups.populate(securitiesList)

    emailSubject, emailBody = get_email(myGroups)
    print(f"finished get_email")

    if emailSubject:
        myNotifier = notification_interface.notification_interface()
        if myNotifier.findArnForTopicName(resultsTopicName):
            myNotifier.sendEmail(emailSubject, emailBody)
            print("sent email.")

    print("Finished daily_email._generate_and_send")

def get_email(myGroups):
    """
    Create email message (subject and body) summarizing price data from
    given grouped lists of security.
    """

    max_wid = 45
    mySubj = ""
    # Subtracting 2 for width because of removing b' from security.name (see longer comment below.)
    myBody = "symbol.name: ".ljust(max_wid - 2) + \
             "   rating, current,     buy,    sell,   %52wk,    %chg"

    for groupCode in sprEnums.GroupCodes:
        myList = myGroups.get_results_for_group(groupCode)
        if myList:
            mySubj += str(len(myList)) + " " + code_display_names[groupCode] + ", "
            myBody += "\n" + code_display_names[groupCode] + "\n"
            for rating in myList:
                myBody += (rating.security.symbol + '.' + rating.security.name +
                           ": ").ljust(max_wid)
                myBody += "%7.2f%%, %7.2f, " % (rating.rating * 100, rating.security.currentPrice)
                myBody += "%7.2f, %7.2f, " % (rating.security.buyPrice, rating.security.sellPrice)
                myBody += "%7.2f%%, " % (rating.security.get_percent_52_week_high())
                myBody += "%7.2f%%\n" % (rating.security.get_percent_change_today())

    # If no securities provided, return empties.
    if not mySubj:
        myBody = ""
    else:
        # Remove trailing comma, space from subject.
        mySubj = mySubj[:-2]
        # Couldn't figure this out - for some reason security.name is behaving like a byte string,
        # in that b' is appearing in front of it when generate body in the lambda, but not when
        # running locally. Used type() to confirm that it is a string, both locally and under
        # lambda, tried str()to force it to be a string, but b' remained. Only way I could find to
        # remove these unwanted b's is this mass replace on the final email body.
        myBody = myBody.replace("b'", "")

    return mySubj, myBody
