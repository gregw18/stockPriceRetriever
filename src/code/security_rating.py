"""
Class to add rating property to a security.
V0.01, October 21, 2020
"""


class security_rating:
    """
    Add rating to security, where rating is a numeric measure used to rank a security
    within a group.
    """

    def set_rating(self, mySecurity, myRating):
        """
        Add rating to given security
        given list of security.
        """

        self.security = mySecurity
        self.rating = myRating
