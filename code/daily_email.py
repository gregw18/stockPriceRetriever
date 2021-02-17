"""
Function to create and send email summarizing the prices that were just downloaded.
Runs automatically from lambda, after downloading.
Creates string containing summary of downloaded prices, publishes to an SNS topic as
an email.
V0.01, October 13, 2020
"""

import notification_interface
import security_groups
import sprEnums


code_display_names = {sprEnums.GroupCodes.buy: "Buy",
                      sprEnums.GroupCodes.near_buy: "Near buy",
                      sprEnums.GroupCodes.middle: "Middle",
                      sprEnums.GroupCodes.near_sell: "Near sell",
                      sprEnums.GroupCodes.sell: "Sell"
                      }


def send(myResultsFile, resFile, resultsTopicName):
    """
    Create and send email summarizing price data from given results file. Usually runs once
    a day, after retrieving prices, called by the lambda.
    Receives resultsFile class, name of results file to work with, name of topic to send
    results to.
    """
    print("Starting daily_email.create")

    securitiesList = myResultsFile.read_results_file_s3(resFile)
    myGroups = security_groups.security_groups()
    myGroups.populate(securitiesList)

    emailSubject, emailBody = get_email(myGroups)

    if emailSubject:
        myNotifier = notification_interface.notification_interface()
        if myNotifier.findArnForTopicName(resultsTopicName):
            myNotifier.sendEmail(emailSubject, emailBody)

    print("Finished daily_email.create")


def get_email(myGroups):
    """
    Create email message (subject and body) summarizing price data from
    given grouped lists of security.
    """

    max_wid = 45
    mySubj = ""
    # Subtracting 2 for width because of removing b' from security.name (see longer comment below.)
    myBody = "symbol.name: ".ljust(max_wid - 2) + "rating, current, buy, sell"

    for groupCode in sprEnums.GroupCodes:
        myList = myGroups.get_results_for_group(groupCode)
        if myList:
            mySubj += str(len(myList)) + " " + code_display_names[groupCode] + ", "
            myBody += "\n" + code_display_names[groupCode] + "\n"
            for rating in myList:
                myBody += (rating.security.symbol + '.' + rating.security.name + ": ").ljust(max_wid)
                myBody += "%.2f%%, %.2f, " % (rating.rating * 100, rating.security.currPrice)
                myBody += "%.2f, %.2f\n" % (rating.security.buyPrice, rating.security.sellPrice)

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
