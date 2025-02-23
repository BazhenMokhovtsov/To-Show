# 📌 Meal Plan Generator

Welcome to everyone interested in our project!
Let us introduce:

- What we do.
- Why we do it.
- What we aim to achieve.

## 📋 Project Overview

### Project Name: Meal Plan Generator

**Description:**
Our website helps users automatically generate meal plans based on their individual preferences. Users can add their own recipes, browse existing ones, and generate meal plans for a specific period (e.g., a week). All data is stored in the user's personal account.

### Target Audience:
- People striving for healthy eating.
- Users looking to optimize the meal planning process.
- Culinary enthusiasts who want to share their recipes.
- Families looking to simplify their daily routine.

## 🔧 Functional Sections

### 1. Home Page
**Description:**
Provides information about the project, its features, and advantages. It contains buttons for registration and login, access to the recipe list, and the meal plan generator. For unregistered users, filtering does not consider preferences.

**Features:**
- Brief site description.
- Registration, login, recipe list, and meal generator buttons.
- Sections overview: “Meal Plan Generator,” “Personal Account,” “Add a Recipe.”

### 2. Personal Account
**Description:**
Allows users to manage preferences, add and edit recipes, update personal details, and view the history of generated meal plans.

**Features:**
- Adding and saving recipes.
- Setting preferences (e.g., calorie intake, food types).
- Viewing generated meal plan history and saving templates.
- Editing personal details (email, password).

### 3. Add a Recipe
**Description:**
Registered users can add their own recipes to the database. Recipes are available to other users only if the corresponding setting is enabled.

**Features:**
- Recipe submission form (title, ingredients, preparation steps).
- Option to upload an image of the dish.

### 4. Recipe List
**Description:**
A page displaying recipes added by users or available in the database.

**Features:**
- Filtering by category (e.g., breakfast, lunch, dinner).
- Searching for recipes by ingredients or name.
- Ability to rate and comment on recipes.

### 5. Meal Plan Generator
**Description:**
The system automatically creates a meal plan based on user preferences and the selected time period.

**Features:**
- Meal generation based on preferences (e.g., gluten-free, vegetarian).
- Period customization (default: one week).
- Saving generated meal plans in the personal account.

## 💡 Future Ideas
- **Meal Cost Calculation**: Allow users to estimate the approximate cost of a meal plan based on product prices.
- **Diet Menu Calculator**: Help users create meal plans according to dietary preferences and restrictions (caloric intake, macronutrients, etc.).

## 🛠 Technologies Used
### Backend:
- Python
- Django
- Django Rest Framework (DRF) — for creating REST APIs
- Redis — for caching data and handling task queues
- Celery — for background tasks (e.g., meal cost calculations)
- PostgreSQL — relational database for storing data

