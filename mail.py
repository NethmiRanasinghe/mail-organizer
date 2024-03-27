class Mail:
    def __init__(self):
        self.sender_name = None
        self.sender_mail = None
        self.receiver = None
        self.time_received = None
        self.date_received = None
        self.subject = None
        self.summary = None
        self.read = None
        self.in_thread = None
        self.has_attachment = None
        self.no_attachments = 0
        self.attachment_types = None
        self.starred = None
        self.forwarded = None
        self.size = None
        self.subscription = None
        self.type = None
        self.labels = None

    # Setters
    def set_sender_name(self, sender_name):
        self.sender_name = sender_name

    def set_sender_mail(self, sender_mail):
        self.sender_mail = sender_mail

    def set_receiver(self, receiver):
        self.receiver = receiver

    def set_time_received(self, time_received):
        self.time_received = time_received

    def set_date_received(self, date_received):
        self.date_received = date_received

    def set_subject(self, subject):
        self.subject = subject

    def set_summary(self, summary):
        self.summary = summary

    def set_read(self, read):
        self.read = read

    def set_in_thread(self, in_thread):
        self.in_thread = in_thread

    def set_has_attachment(self, has_attachment):
        self.has_attachment = has_attachment

    def set_no_attachments(self, no_attachments):
        self.no_attachments = no_attachments

    def set_attachment_types(self, attachment_types):
        self.attachment_types = attachment_types

    def set_starred(self, starred):
        self.starred = starred

    def set_forwarded(self, forwarded):
        self.forwarded = forwarded

    def set_size(self, size):
        self.size = size

    def set_subscription(self, subscription):
        self.subscription = subscription

    def set_type(self, type):
        self.type = type

    def set_labels(self, labels):
        self.labels = labels

    # Getters
    # def get_sender_name(self):
    #     return self.sender_name

    # def get_sender_mail(self):
    #     return self.sender_mail

    # def get_receiver(self):
    #     return self.receiver

    # def get_time_received(self):
    #     return self.time_received

    # def get_subject(self):
    #     return self.subject

    # def get_summary(self):
    #     return self.summary

    # def get_read(self):
    #     return self.read

    # def get_in_thread(self):
    #     return self.in_thread

    # def get_has_attachment(self):
    #     return self.has_attachment

    # def get_starred(self):
    #     return self.starred

    # def get_size(self):
    #     return self.size

    # def get_subscription(self):
    #     return self.subscription

    # def get_type(self):
    #     return self.type

    # def get_labels(self):
    #     return self.labels