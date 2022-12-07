from comment.models import *
from utils.Redis_utils import cache_get_by_id


def get_all_comments_by_comment_id(comment_id):
    # 获取当前评论下的所有子级评论。
    all_comments = []

    # 获得当前评论的详细内容
    comment_key, comment_dic = cache_get_by_id('comment', 'comment', comment_id)

    # 获得当前评论所有子评论的id
    try:
        comment_of_comment_key, comment_of_comment_dic = cache_get_by_id('comment', 'commentofcomments', comment_id)
        comment_id_list = comment_of_comment_dic['comment_id_list']
    except:
        comment_id_list = []

    # 对每一个子评论的id进行递归查找
    for comment_id in comment_id_list:
        all_comments.append(get_all_comments_by_comment_id(comment_id))

    comment_dic['son_comments'] = all_comments

    # 获取当前评论的用户信息。
    user_id = comment_dic['user_id']
    user_key, user_dic = cache_get_by_id('user', 'user', user_id)
    comment_dic['user_information'] = user_dic

    # 获取当前评论回复的评论的用户信息。
    reply_user_id = comment_dic['reply_user_id']
    reply_user_dic = {}

    if reply_user_id != 0:
        reply_user_key, reply_user_dic = cache_get_by_id('user', 'user', reply_user_id)

    comment_dic['reply_user_information'] = reply_user_dic

    return comment_dic


def get_all_comments_by_work_id(work_id):
    # 获取当前论文下的所有评论。
    all_comments = []

    try:
        key, comment_of_work_dic = cache_get_by_id('comment', 'commentofworks', work_id)
    except:
        return all_comments
    # 获得当前论文的所有评论
    comment_id_list = comment_of_work_dic['comment_id_list']

    # 对每一个评论的id进行递归查找
    for comment_id in comment_id_list:
        all_comments.append(get_all_comments_by_comment_id(comment_id))

    return all_comments
