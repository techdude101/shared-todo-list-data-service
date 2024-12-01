class TestIndex:

    def test_get_index(self, client):

        response = client.get("/")
        assert response.status_code == 200
