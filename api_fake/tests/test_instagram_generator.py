from generators.instagram_generator import InstagramDataGenerator

def test_generate_post():
    """Testa se o gerador de dados do Instagram cria um post válido."""
    generator = InstagramDataGenerator()
    post = generator.generate_post()
    
    assert "id" in post
    assert "user_handle" in post
    assert "caption" in post
    assert "image_url" in post
    assert "posted_at" in post
    assert "likes" in post
    assert isinstance(post["hashtags"], list)
    assert isinstance(post["comments"], list)