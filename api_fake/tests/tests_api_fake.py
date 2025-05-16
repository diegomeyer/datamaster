import pytest
from unittest.mock import MagicMock
from datetime import datetime
from ..fake_api import FakeAPI

@pytest.fixture
def fake_api():
    api = FakeAPI(kafka_broker='127.0.0.1:9092')
    api.producer = MagicMock()  # Evita envio real ao Kafka
    return api

def test_generate_facebook_post(fake_api):
    post = fake_api.generate_facebook_post()
    assert "id" in post
    assert "user_name" in post
    assert "post_content" in post
    assert "created_at" in post
    assert isinstance(post["likes"], int)
    assert isinstance(post["shares"], int)
    assert isinstance(post["comments"], list)
    for comment in post["comments"]:
        assert "user" in comment
        assert "comment" in comment
        assert "timestamp" in comment

def test_generate_instagram_post(fake_api):
    post = fake_api.generate_instagram_post()
    assert "id" in post
    assert post["user_handle"].startswith("@")
    assert "caption" in post
    assert "image_url" in post
    assert "posted_at" in post
    assert isinstance(post["likes"], int)
    assert isinstance(post["hashtags"], list)
    for comment in post["comments"]:
        assert "user" in comment
        assert "comment" in comment
        assert "timestamp" in comment

def test_generate_x_post(fake_api):
    post = fake_api.generate_x_post()
    assert "username" in post
    assert "display_name" in post
    assert "tweet" in post
    assert "likes" in post
    assert "retweets" in post
    assert "created_at" in post
    assert isinstance(post["verified"], bool)
    for reply in post["replies"]:
        assert "username" in reply
        assert "tweet" in reply
        assert "created_at" in reply

def test_generate_data_dispatch_facebook(fake_api):
    fake_api.generate_data("facebook", count=2)
    assert fake_api.producer.send.call_count == 2

def test_generate_data_dispatch_instagram(fake_api):
    fake_api.generate_data("instagram", count=2)
    assert fake_api.producer.send.call_count == 2

def test_generate_data_dispatch_x(fake_api):
    fake_api.generate_data("x", count=2)
    assert fake_api.producer.send.call_count == 2

def test_generate_data_invalid_platform(fake_api):
    with pytest.raises(ValueError):
        fake_api.generate_data("linkedin")
