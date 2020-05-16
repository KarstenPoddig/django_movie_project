import json

from django.http import HttpResponse


class OutputObject:
    """This is the central class """
    def __init__(self, status=None, message=None, data=None,
                 dict_additional_meta_data={}):
        self.status = status
        self.message = message
        self.data = data
        self.additional_meta_data = dict_additional_meta_data

    def build_meta_data(self, standard_dict):
        self.additional_meta_data.update(standard_dict)

    def build_output_dict(self):
        self.build_meta_data(standard_dict={'status': self.status,
                                            'message': self.message})
        self.output_dict = {'meta': self.additional_meta_data,
                            'data': self.data}

    def get_http_response(self):
        self.build_output_dict()
        return HttpResponse(json.dumps(self.output_dict),
                            'application/json')