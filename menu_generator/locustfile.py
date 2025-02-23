from locust import HttpUser, between, task

# locust -f locustfile.py


class WebUser(HttpUser):
    host = "quick-meals.ru"
    wait_time = between(1, 5)

    # @task
    # def view_all_open_recipes(self):
    #     response = self.client.get("/api/recipes/open-recipes/get-all-open-recipes/")
    #     task_id = response.json()["detail"]

    #     self.client.post(
    #         "/api/recipes/open-recipes/get-all-open-recipes/check/",
    #         {"task_id": task_id},
    #     )

    # @task
    # def get_open_recipe(self):
    #     self.client.post("/api/recipes/open-recipes/get-open-recipe/", {"open_recipe_pk": 1})

    @task
    def use_generator(self):
        #
        # response = self.client.post('/api/auth/login/', json={
        #                         "login_data": "admin",
        #                         "password": "Admin1234"
        #                       }
        #                             )
        #
        # token = response.json().get('access')
        #
        # self.client.headers = {
        #         "Authorization": f"Q {token}"
        #     }

        response = self.client.post(
            "/api/generator/generate/",
            {
                "days": [
                    "saturday",
                    "sunday",
                    "thursday",
                    "wednesday",
                    "tuesday",
                    "friday",
                    "monday",
                ],
                "one_day": "false",
                "meal_time": ["snack", "dinner", "after_tea", "breakfast", "lunch"],
                "db_choice": ["open_recipe", "user_recipe"],
                "no_repeat": "false",
                "exclude_products": [],
                "exclude_key_words": [],
                "include_products": [],
                "calories_min": 1,
                "calories_max": 11111,
                "time_cooking": 111111,
                "max_number_of_products": 111111,
            },
        )

        key = response.json()["result"]

        self.client.post("/api/generator/generate/check/", {"task_id": key})

    # @task
    # def search_field(self):
    #     self.client.post(
    #         "/api/recipes/search-field-helper/",
    #         {"user_input": "Кар", "search_method": "easy"},
    #     )

    # @task
    # def recipes_filter(self):
    #     response = self.client.post(
    #         "/api/recipes/recipes-filter/",
    #         json={
    #             "exclude_products": [{"result": {"product": "Молоко", "where": "product"}}],
    #             "include_products": [
    #                 {"result": {"product": "Яблоки", "where": "product"}},
    #                 {"result": {"product": "Фрукты", "where": "product_category"}},
    #             ],
    #             "max_products_quantity": 50,
    #             "recipe_category": "Другая Категория",
    #             "meal_time": ["lunch"],
    #             "type_recipe": ["hot"],
    #             "cooking_time": 1000,
    #             "max_cal_per_100_gram": 300,
    #         },
    #     )

    #     key = response.json()["detail"]
    #     self.client.post("/api/recipes/recipes-filter/check/", {"task_id": key})
