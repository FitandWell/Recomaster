import requests
import json
import streamlit as st

class Generator:
    def __init__(self, nutrition_input: list, diet_preference: str, ingredients: list = [], params: dict = {'n_neighbors': 5, 'return_distance': False}, token: str = None):
        self.nutrition_input = nutrition_input
        self.diet_preference = diet_preference
        self.ingredients = ingredients
        self.params = params
        self.token = token  # Add token to the class

    def set_request(self, nutrition_input: list, diet_preference: str, ingredients: list, params: dict):
        self.nutrition_input = nutrition_input
        self.diet_preference = diet_preference
        self.ingredients = ingredients
        self.params = params

    def filter_recipes_by_diet(self, recipes):
        non_veg_keywords = [
            'meat', 'beef', 'chicken', 'lamb', 'pork', 'turkey', 'goat',
            'duck', 'veal', 'bacon', 'sausages', 'fish', 'shellfish',
            'clams', 'oysters', 'mussels', 'squid', 'calamari', 'octopus',
            'scallops', 'egg', 'rabbit', 'venison', 'quail', 'cod', 'salmon fillets'
        ]
        filtered_recipes = []

        for recipe in recipes:
            is_non_veg = any(keyword in ' '.join(recipe['RecipeIngredientParts']).lower() for keyword in non_veg_keywords)

            if self.diet_preference == 'Vegetarian' and not is_non_veg:
                filtered_recipes.append(recipe)
            elif self.diet_preference == 'Non Vegetarian' and is_non_veg:
                filtered_recipes.append(recipe)

        return filtered_recipes

    def generate(self):
        request = {
            'nutrition_input': self.nutrition_input,
            'ingredients': self.ingredients,
            'params': self.params
        }        

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {st.session_state["access_token"]}'  # Use double quotes around the key

        }

        response = requests.post(url='https://recommend-meal.osc-fr1.scalingo.io/predict/', headers=headers, data=json.dumps(request))        

        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

        recipes = response.json().get('output', [])
        filtered_recipes = self.filter_recipes_by_diet(recipes)
        return filtered_recipes
