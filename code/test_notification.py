"""
Simple manual test for notification_interface.
Sends message via defined topic name, user has to check email to confirm that
message was received.
V0.01, October 13, 2020
"""

import boto3
from moto import mock_sns

import notification_interface

my_bucket = "fake_bucket"
my_prefix = "fake_prefix"
fake_accessKey = "TESTING"
fake_secretKey = "TESTING"

myTopicName = "StockRetrieverResultsTopic"


def tst_notification():
    """
    Send message via hard-coded topic name.
    """
    myNotifier = notification_interface.notification_interface()
    if myNotifier.findArnForTopicName(myTopicName):
        myNotifier.sendEmail("notification test subject", "notification test body\n body line 1")
        assert True
    else:
        assert False


@mock_sns
class TestNotifications():
    def setup(self):
        self.client = boto3.client("sns", aws_access_key_id=fake_accessKey,
                                   aws_secret_access_key=fake_secretKey)
        self.topics = []
        self.good_name = "TopicExists"
        self.bad_name = "doesNotExist"

    def teardown(self):
        """
        Remove all topics so won't exist for next test. Note that, for moto at least,
        if delete elements of first batch when receive it, rather than first getting
        results of all subsequent batches, won't actually delete everything, as it appears
        that you can't delete items while traversing the collection. Instead, first get
        all batches of items, then delete all of them.
        """
        nextToken = ""
        arn_list = []
        while True:
            # Get next batch of arns, add to list.
            if nextToken:
                response = self.client.list_topics(NextToken=nextToken)
            else:
                response = self.client.list_topics()
            print("response=", response, "\nlen=", len(response['Topics']))
            arn_list.extend(response['Topics'])

            # Check if there are more batches to look through
            if 'NextToken' in response.keys():
                nextToken = response['NextToken']
            else:
                break

        # Delete all of them.
        for arn in arn_list:
            self.client.delete_topic(TopicArn=arn['TopicArn'])

        response = self.client.list_topics()
        print("response=", response, "\nlen=", len(response['Topics']))

    def _add_topic(self, topicName):
        """
        Add a topic with given name
        """
        result = self.client.create_topic(Name=topicName)
        if 'TopicArn' in result:
            self.topics.append(result['TopicArn'])

    def _add_n_topics(self, start, num):
        """
        Add n topics, with names topic1-topicn.
        """
        for num in range(start, start + num):
            nextName = "topic" + str(num)
            self._add_topic(nextName)

    def test_no_topics_no_match(self):
        """
        No topics, so no match
        """
        my_notifier = notification_interface.notification_interface()
        topic_exists = my_notifier.findArnForTopicName(self.bad_name)
        assert topic_exists == False

    def test_one_topic_no_match(self):
        """
        One topics, no match
        """
        my_notifier = notification_interface.notification_interface()
        self._add_topic(self.good_name)
        topic_exists = my_notifier.findArnForTopicName(self.bad_name)
        assert topic_exists == False

    def test_one_topic_match(self):
        """
        One topic, match
        """
        my_notifier = notification_interface.notification_interface()
        self._add_topic(self.good_name)
        topic_exists = my_notifier.findArnForTopicName(self.good_name)
        assert topic_exists == True

    def test_5_topics_no_match(self):
        """
        Five topics, no match
        """
        my_notifier = notification_interface.notification_interface()
        self._add_n_topics(1, 5)
        topic_exists = my_notifier.findArnForTopicName(self.bad_name)
        assert topic_exists == False

    def test_5_topics_first_match(self):
        """
        Five topics, first matches
        """
        my_notifier = notification_interface.notification_interface()
        self._add_topic(self.good_name)
        self._add_n_topics(1, 5)
        topic_exists = my_notifier.findArnForTopicName(self.good_name)
        assert topic_exists == True

    def test_5_topics_last_match(self):
        """
        Five topics, last matches
        """
        my_notifier = notification_interface.notification_interface()
        self._add_topic(self.good_name)
        self._add_n_topics(1, 5)
        self._add_topic(self.good_name)
        topic_exists = my_notifier.findArnForTopicName(self.good_name)
        assert topic_exists == True

    def test_5_topics_middle_match(self):
        """
        Five topics, matches in middle
        """
        my_notifier = notification_interface.notification_interface()
        self._add_n_topics(1, 3)
        self._add_topic(self.good_name)
        self._add_n_topics(4, 2)
        topic_exists = my_notifier.findArnForTopicName(self.good_name)
        assert topic_exists == True

    def test_350_topics_first_group_match(self):
        """
        350 topics, matches in middle of first group
        """
        my_notifier = notification_interface.notification_interface()
        self._add_n_topics(1, 45)
        self._add_topic(self.good_name)
        self._add_n_topics(46, 305)
        topic_exists = my_notifier.findArnForTopicName(self.good_name)
        assert topic_exists == True

    def test_350_topics_third_group_match(self):
        """
        350 topics, matches in middle of third group (assumes groups of 100)
        """
        my_notifier = notification_interface.notification_interface()
        self._add_n_topics(1, 245)
        self._add_topic(self.good_name)
        self._add_n_topics(246, 105)
        topic_exists = my_notifier.findArnForTopicName(self.good_name)
        assert topic_exists == True

    def test_350_topics_last_item_match(self):
        """
        350 topics, match is last.
        """
        my_notifier = notification_interface.notification_interface()
        self._add_n_topics(1, 350)
        self._add_topic(self.good_name)
        topic_exists = my_notifier.findArnForTopicName(self.good_name)
        assert topic_exists == True

    def test_350_topics_no_match(self):
        """
        350 topics, match is last.
        """
        my_notifier = notification_interface.notification_interface()
        self._add_n_topics(1, 350)
        self._add_topic(self.good_name)
        topic_exists = my_notifier.findArnForTopicName(self.bad_name)
        assert topic_exists == False
