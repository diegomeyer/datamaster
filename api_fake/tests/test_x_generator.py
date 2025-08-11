from generators.x_generator import XDataGenerator


def test_generate_post():
    """
    Testa a geração de um post do X/Twitter.
    GIVEN: Uma instância do XDataGenerator.
    WHEN: O método generate_post é chamado.
    THEN: O dicionário resultante deve conter todas as chaves esperadas e tipos corretos.
    """
    generator = XDataGenerator()
    post = generator.generate_post()

    assert "username" in post
    assert "display_name" in post
    assert "tweet" in post
    assert "likes" in post
    assert "retweets" in post
    assert "created_at" in post
    assert isinstance(post["replies"], list)