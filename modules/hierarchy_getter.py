import json

object_list = []
topic_list = []


class MyObject(object):
    name = ""
    size = 0

    def __init__(self, name, size):
        self.name = name
        self.size = size


class MyTopic(object):
    name = ""
    children = []

    def __init__(self, name):
        self.name = name


def parse_data(data):
    global object_list
    try:
        children = data['children']
        topic = MyTopic(data['name'])
        for child in children:
            parse_data(child)
        topic.children = object_list
        topic_list.append(topic)
        object_list = []
    except KeyError:
        a = MyObject(data['name'], data['size'])
        object_list.append(a)


def get_all_classes():
    name = []
    with open('bbox_hierarchy.json') as json_file:
        data = json.load(json_file)
        data = data['children']

        for topic in data:
            parse_data(topic)

        for topic in topic_list:
            for object in topic.children:
                name.append(object.name)
    return name
