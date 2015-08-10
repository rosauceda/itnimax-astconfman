from datetime import datetime
from flask.ext.babelex import gettext, lazy_gettext
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
import asterisk
from app import db


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(128), index=True)
    phone = db.Column(db.String(32))

    def __unicode__(self):
        if self.name:
            return '%s <%s>' % (self.name, self.phone)
        else:
            return self.phone


class Conference(db.Model):
    """Conference is an event held in in a Room"""
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(16), unique=True)
    name = db.Column(db.Unicode(128))
    is_public = db.Column(db.Boolean)
    conference_profile_id = db.Column(db.Integer,
                                      db.ForeignKey('conference_profile.id'))
    conference_profile = db.relationship('ConferenceProfile')
    public_participant_profile_id = db.Column(
        db.Integer,
        db.ForeignKey('participant_profile.id'))
    public_participant_profile = db.relationship('ParticipantProfile')

    def __unicode__(self):
        return '%s <%s>' % (self.number, self.name)


    def _online_participant_count(self):
        return asterisk.confbridge_get_user_count(self.number) or 0
    online_participant_count = property(_online_participant_count)


    def _participant_count(self):
        return len(self.participants)
    participant_count = property(_participant_count)


    def _is_locked(self):
        return asterisk.confbridge_is_locked(self.number)
    is_locked = property(_is_locked)


    def log(self, message):
        post = ConferenceLog(conference=self, message=message)
        db.session.add(post)
        db.session.commit()


class ConferenceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added = db.Column(db.DateTime, default=datetime.now)
    message = db.Column(db.Unicode(1024))
    conference_id = db.Column(db.Integer, db.ForeignKey('conference.id'))
    conference = db.relationship('Conference', backref='logs')

    def __unicode__(self):
        return '%s: %s' % (self.added, self.message)


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(32), index=True)
    name = db.Column(db.Unicode(128))
    conference_id = db.Column(db.Integer, db.ForeignKey('conference.id'))
    conference = db.relationship('Conference', backref='participants')
    profile_id = db.Column(db.Integer, db.ForeignKey('participant_profile.id'))
    profile = db.relationship('ParticipantProfile')
    __table_args__ = (db.UniqueConstraint('conference_id', 'phone',
                                          name='uniq_phone'),)

    def __unicode__(self):
        if self.name:
            return '%s <%s>' % (self.name, self.phone)
        else:
            return self.phone


class ConferenceProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(128))
    max_members = db.Column(db.Integer, default=50)
    record_conference = db.Column(db.Boolean)
    internal_sample_rate = db.Column(db.String(8))
    mixing_interval = db.Column(db.String(2), default='20')
    video_mode = db.Column(db.String(16))

    def __unicode__(self):
        return self.name

    def get_confbridge_options(self):
        options = []
        if self.max_members:
            options.append('max_members=%s' % self.max_members)
        if self.record_conference:
            options.append('record_conference=yes')
        if self.internal_sample_rate:
            options.append(
                'internal_sample_rate=%s' % self.internal_sample_rate)
        if self.mixing_interval:
            options.append('mixing_interval=%s' % self.mixing_interval)
        if self.video_mode:
            options.append('video_mode=%s' % self.video_mode)

        return options


class ParticipantProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(128))
    admin = db.Column(db.Boolean, index=True)
    marked = db.Column(db.Boolean, index=True)
    startmuted = db.Column(db.Boolean)
    music_on_hold_when_empty = db.Column(db.Boolean)
    music_on_hold_class = db.Column(db.String(64), default='default')
    quiet = db.Column(db.Boolean)
    announce_user_count = db.Column(db.Boolean)
    announce_user_count_all = db.Column(db.String(4))
    announce_only_user = db.Column(db.Boolean)
    announcement = db.Column(db.String(128))
    wait_marked = db.Column(db.Boolean)
    end_marked = db.Column(db.Boolean)
    dsp_drop_silence = db.Column(db.Boolean)
    dsp_talking_threshold = db.Column(db.Integer, default=160)
    dsp_silence_threshold = db.Column(db.Integer, default=2500)
    talk_detection_events = db.Column(db.Boolean)
    denoise = db.Column(db.Boolean)
    jitterbuffer = db.Column(db.Boolean)
    pin = db.Column(db.String, index=True)
    announce_join_leave = db.Column(db.Boolean)
    dtmf_passthrough = db.Column(db.Boolean)

    def __unicode__(self):
        return self.name

    def get_confbridge_options(self):
        options = []
        if self.admin:
            options.append('admin=yes')
        if self.marked:
            options.append('marked=yes')
        if self.startmuted:
            options.append('startmuted=yes')
        if self.music_on_hold_when_empty:
            options.append('music_on_hold_when_empty=yes')
        if self.music_on_hold_class:
            options.append('music_on_hold_class=%s' % self.music_on_hold_class)
        if self.quiet:
            options.append('quiet=yes')
        if self.announce_user_count:
            options.append('announce_user_count=yes')
        if self.announce_user_count_all:
            options.append(
                'announce_user_count_all=%s' % self.announce_user_count_all)
        if self.announce_only_user:
            options.append('announce_only_user=yes')
        if self.announcement:
            options.append('announcement=%s' % self.announcement)
        if self.wait_marked:
            options.append('wait_marked=yes')
        if self.end_marked:
            options.append('end_marked=yes')
        if self.dsp_drop_silence:
            options.append('dsp_drop_silence=yes')
        if self.dsp_talking_threshold:
            options.append(
                'dsp_talking_threshold=%s' % self.dsp_talking_threshold)
        if self.dsp_silence_threshold:
            options.append(
                'dsp_silence_threshold=%s' % self.dsp_silence_threshold)
        if self.talk_detection_events:
            options.append('talk_detection_events=yes')
        if self.denoise:
            options.append('denoise=yes')
        if self.jitterbuffer:
            options.append('jitterbuffer=yes')
        if self.pin:
            options.append('pin=%s' % self.pin)
        if self.announce_join_leave:
            options.append('announce_join_leave=yes')
        if self.dtmf_passthrough:
            options.append('dtmf_passthrough=yes')

        return options
