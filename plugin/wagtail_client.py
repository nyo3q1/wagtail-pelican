import urllib.parse
import logging

import requests


logger = logging.getLogger()


class WagtailClient():
    def __init__(self, url: str):
        self.url = url

        self.HEADER_JSON = {'content-type': 'application/json'}

    def get(self, param: dict=None) -> dict:
        response = requests.get(self.url, params=param, headers=self.HEADER_JSON)
        logger.debug(response.url)
        response_dict = response.json()
        response_dict['meta'].update(**self._is_next(response_dict, param))

        for index, item in enumerate(response_dict['items']):
            item_detail = requests.get(self.url + str(item['id']) + "/", headers=self.HEADER_JSON)
            item_detail = item_detail.json()
            response_dict['items'][index].update(item_detail)

        return response_dict

    def _is_next(self, response: dict, param: dict=None) -> dict:
        total_count = response['meta'].get("total_count", 0)
        if total_count == 0:
            return {'has_next': False, 'has_previos': False}

        item_count = len(response["items"])
        if total_count == item_count:
            return {'has_next': False, 'has_previos': False}

        if param is None:
            if total_count > item_count:
                """
                total_count: 21
                item_count: 20
                """
                return {'has_next': True, 'has_previos': False}
        else:
            limit = param.get("limit")
            offset = param.get("offset")

            if offset is None:
                if total_count > item_count:
                    """
                    total_count: 5
                    item_count: 2
                    param: {
                        limit: 2
                    }
                    """
                    return {'has_next': True, 'has_previos': False}
            else:
                if offset == 0 and total_count > item_count:
                    """
                    total_count: 5
                    item_count: 2
                    param: {
                        offset: 0
                        limit: 2
                    }
                    """
                    return {'has_next': True, 'has_previos': False}
                elif total_count > (item_count + offset):
                    """
                    total_count: 5
                    item_count: 2
                    param: {
                        offset: 2
                        limit: 2
                    }
                    """
                    return {'has_next': True, 'has_previos': True}
                else:
                    """
                    total_count: 5
                    item_count: 2
                    param: {
                        offset: 4
                        limit: 2
                    }
                    """
                    return {'has_next': False, 'has_previos': True}


        return True
