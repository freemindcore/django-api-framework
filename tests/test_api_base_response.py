import json

import pytest

from easy.response import BaseApiResponse


def test_base_api_result_base():

    assert BaseApiResponse("").json_data["data"] == ""

    assert BaseApiResponse("1").json_data["data"] == "1"

    assert BaseApiResponse("0").json_data["data"] == "0"
    assert BaseApiResponse().json_data["data"] == {}
    assert BaseApiResponse([]).json_data["data"] == []
    assert BaseApiResponse(True).json_data["data"] is True
    assert BaseApiResponse(False).json_data["data"] is False
    assert BaseApiResponse([1, 2, 3]).json_data["data"] == [1, 2, 3]


def test_base_api_result_dict():

    assert BaseApiResponse({"a": 1, "b": 2}).json_data["data"] == {
        "a": 1,
        "b": 2,
    }

    assert (BaseApiResponse({"code": 2, "im": 14})).json_data["data"]["im"] == 14
    assert (BaseApiResponse({"code": 2, "im": 14})).json_data["data"]["code"] == 2


def test_base_api_result_message():
    assert (
        BaseApiResponse(code=-1, message="error test").json_data["message"]
        == "error test"
    )
    assert BaseApiResponse().json_data["message"]


def test_base_api_edit():
    orig_resp = BaseApiResponse(
        {"item_id": 2, "im": 14},
        code=0,
    )

    with pytest.raises(KeyError):
        print(orig_resp.json_data["detail"])

    data = orig_resp.json_data

    data["detail"] = "Edited!!!"
    orig_resp.content = json.dumps(data)

    assert orig_resp.json_data["detail"] == "Edited!!!"

    data = orig_resp.json_data
    assert data["code"] == 0

    data["code"] = 401
    orig_resp.update_content(data)
    assert orig_resp.json_data["code"] == 401
    assert orig_resp.json_data["data"]["im"] == 14

    data["data"]["im"] = 8888
    orig_resp.update_content(data)
    assert orig_resp.json_data["data"]["im"] == 8888
