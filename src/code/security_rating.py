"""
Class to add rating property to a security.
V0.01, October 21, 2020
"""


class SecurityRating:
    """
    Add rating to security, where rating is a numeric measure used to rank a security
    within a group.
    """
    def __init__(self):
        self.security = None
        self.rating = None

    def set_rating(self, mySecurity, myRating):
        """
        Add rating to given security
        given list of security.
        """

        self.security = mySecurity
        self.rating = myRating
