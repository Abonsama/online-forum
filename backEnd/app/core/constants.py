class FieldSizes:
    # Common string lengths
    TINY = 20
    SHORT = 50
    MEDIUM = 100
    LARGE = 255
    LONG = 1000
    VERY_LONG = 2000
    EXTRA_LONG = 5000

    # User fields
    EMAIL = LARGE
    USERNAME = SHORT
    PASSWORD = SHORT
    PASSWORD_HASH = LONG
    USER_ROLE = TINY

    # Topic fields
    TOPIC_NAME = MEDIUM
    TOPIC_SLUG = MEDIUM

    # Post fields
    POST_TITLE = LARGE

    # Report fields
    REPORT_TYPE = TINY
    REPORT_REASON = SHORT
    REPORT_STATUS = TINY
