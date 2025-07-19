from api_fake.generators.facebook_generator import FacebookDataGenerator

def test_generate_post():
    """Testa se o gerador de dados do Facebook cria um post válido."""
    generator = FacebookDataGenerator()
    post = generator.generate_post()
    
    assert "id" in post
    assert "user_name" in post
    assert "post_content" in post
    assert "created_at" in post
    assert "likes" in post
    assert "shares" in post
    assert isinstance(post["comments"], list)