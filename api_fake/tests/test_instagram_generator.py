from generators.instagram_generator import InstagramDataGenerator


def test_generate_post():
    """
    Testa a geração de um post do Instagram.
    GIVEN: Uma instância do InstagramDataGenerator.
    WHEN: O método generate_post é chamado.
    THEN: O dicionário resultante deve conter todas as chaves esperadas e tipos corretos.
    """
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