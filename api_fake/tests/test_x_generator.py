from api_fake.generators.x_generator import XDataGenerator

def test_generate_post():
    """Testa se o gerador de dados do X cria um post válido."""
    generator = XDataGenerator()
    post = generator.generate_post()
    
    assert "username" in post
    assert "display_name" in post
    assert "tweet" in post
    assert "likes" in post
    assert "retweets" in post
    assert "created_at" in post
    assert isinstance(post["replies"], list)