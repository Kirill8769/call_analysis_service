import os

PATH_PROJECT = os.path.dirname(os.path.abspath(__file__))

LISTEN_USERS = ["118", "31017", "85", "4325", "3683", "177", "176", "55"]

USER_DATE = "2023-11-07T05:20:13+03:00"

EMPTY_DICT_ANSWER = {
    0: {"general_comment": None, "total_score": None},
    1: {"greeting": {"comment": None, "score": None}},
    2: {"speech": {"comment": None, "score": None}},
    3: {"initiative": {"comment": None, "score": None}},
    4: {"need": {"comment": None, "score": None}},
    5: {"offer": {"comment": None, "score": None}},
    6: {"objection": {"comment": None, "score": None}},
    7: {"perseverance": {"comment": None, "score": None}},
    8: {"advantages": {"comment": None, "score": None}},
    9: {"agreement": {"comment": None, "score": None}},
    10: {"resume_manager": []},
    11: {"recommendations": []},
}
