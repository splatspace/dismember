from dismember.models.credential import Credential
from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.sql.schema import ForeignKey


class ProxCredential(Credential):
    """A HID Prox key fob"""
    __tablename__ = 'prox_credentials'

    id = Column(Integer, ForeignKey('credentials.id', onupdate='cascade', ondelete='cascade'), primary_key=True)

    number = Column(Integer, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)

    __mapper_args__ = {
        'polymorphic_identity': 'prox_credential'
    }

    def __str__(self):
        return '%d' % self.number

    @property
    def details(self):
        ret = super(ProxCredential, self).details
        if not self.enabled:
            ret.append('disabled')
        return ret
