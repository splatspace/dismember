from dismember.models.user import User


class MemberService(object):
    """
    Provides high-level methods for managing membership properties of users.
    """

    def get_members(self):
        """
        Get all the users who are members (member type is set).
        """
        query = User.query.filter(User.member_type_id.isnot(None))
        members = query.all()
        return members


member_service = MemberService()