"""
Interface to AWS' SNS service. Currently only supports email notification.
V0.01, October 13, 2020
"""

import boto3


class NotificationInterface:
    """
    Interface to SNS.
    """

    def __init__(self):
        self.client = boto3.client("sns")
        self.topic_arn = ""

    def findArnForTopicName(self, topicName):
        """
        Get list of topics, iterate through it to find one that contains requested topic name.
        (arn always contains the topic name in last section, though it may be decorated with
        the lambda name as a prefix and a random string as the suffix, depending on whether it
        was created via CloudFormation, the console, the cli, etc.)
        """
        topicExists = False

        try:
            self.topic_arn = ""
            nextToken = ""
            while self.topic_arn == "":
                # Get next batch of arns.
                if nextToken:
                    response = self.client.list_topics(NextToken=nextToken)
                else:
                    response = self.client.list_topics()

                # See if we have a match in this batch.
                for arn in response['Topics']:
                    if topicName in arn['TopicArn']:
                        self.topic_arn = arn['TopicArn']
                        topicExists = True
                        break

                # Check if there are more batches to look through.
                if "NextToken" in response.keys():
                    nextToken = response['NextToken']
                else:
                    break

        except Exception as ex:
            print("ex=", ex)
            self.topic_arn = ""
            topicExists = False

        print("topicExists=", topicExists)

        return topicExists

    def sendEmail(self, mySubj, myBody):
        """
        Send email message using given subject and body, to previously set topic.
        """

        print("Starting sendEmail")
        self.client.publish(TopicArn=self.topic_arn, Message=myBody, Subject=mySubj)
        print("Finished sendEmail")
