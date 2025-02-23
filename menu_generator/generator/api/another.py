import random


def generate(
    meal_time,
    result,
    recipes_with_products,
    no_repeat,
    one_day,
    db_user_recipes,
    db_open_recipes,
    day=None,
):
    if meal_time == "lunch" or meal_time == "dinner":
        if meal_time == "lunch":
            default_types = ["soups", "hot", "salads"]
        elif meal_time == "dinner":
            default_types = ["hot", "salads"]
    else:
        if meal_time == "breakfast":
            default_types = ["hot", "salads", "snacks", "baking", "billets", "desserts"]
        elif meal_time == "after_tea":
            default_types = ["baking", "desserts"]
        elif meal_time == "snack":
            default_types = ["billets", "snacks"]
    if one_day:
        if meal_time == "breakfast" or meal_time == "after_tea" or meal_time == "snack":
            if recipes_with_products is not None:
                for recipe in recipes_with_products:
                    if (
                        recipe[0].type in default_types
                        and meal_time in recipe[0].meal_time
                        and result[meal_time] is None
                    ):
                        result[meal_time] = {
                            "recipe": recipe[0].title,
                            "find_by_products": True,
                        }
                        recipes_with_products.remove(recipe)

            if result[meal_time] is None:
                if db_user_recipes and db_open_recipes:
                    user_recipe = (
                        db_user_recipes.filter(
                            type__in=default_types, meal_time__contains=meal_time
                        )
                        .order_by("?")
                        .first()
                    )
                    open_recipe = (
                        db_open_recipes.filter(
                            type__in=default_types, meal_time__contains=meal_time
                        )
                        .order_by("?")
                        .first()
                    )
                    if user_recipe and open_recipe:
                        rand_recipe = random.choice(
                            [[user_recipe, "user_db"], [open_recipe, "open_db"]]
                        )
                        result[meal_time] = rand_recipe[0].title
                        if no_repeat:
                            if rand_recipe[1] == "user_db":
                                db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
                            else:
                                db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)

                    elif user_recipe:
                        result[meal_time] = user_recipe.title
                    elif open_recipe:
                        result[meal_time] = open_recipe.title

                elif db_user_recipes:
                    recipe = (
                        db_user_recipes.filter(
                            type__in=default_types, meal_time__contains=meal_time
                        )
                        .order_by("?")
                        .first()
                    )
                    if recipe:
                        result[meal_time] = recipe.title
                        if no_repeat:
                            db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
                elif db_open_recipes:
                    recipe = (
                        db_open_recipes.filter(
                            type__in=default_types, meal_time__contains=meal_time
                        )
                        .order_by("?")
                        .first()
                    )
                    if recipe:
                        result[meal_time] = recipe.title
                        if no_repeat:
                            db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)

            if result[meal_time] is None:
                result[meal_time] = "Нет рецептов"

        elif meal_time == "lunch" or meal_time == "dinner":
            for type in default_types:
                if recipes_with_products is not None:
                    if recipes_with_products is not None:
                        for recipe in recipes_with_products:
                            if (
                                recipe[0].type == type
                                and meal_time in recipe[0].meal_time
                                and result[meal_time][type] is None
                            ):
                                result[meal_time][type] = {
                                    "recipe": recipe[0].title,
                                    "find_by_products": True,
                                }
                                recipes_with_products.remove(recipe)

                    if result[meal_time][type] is None:
                        if db_user_recipes and db_open_recipes:
                            user_recipe = (
                                db_user_recipes.filter(type=type, meal_time__contains=meal_time)
                                .order_by("?")
                                .first()
                            )
                            open_recipe = (
                                db_open_recipes.filter(type=type, meal_time__contains=meal_time)
                                .order_by("?")
                                .first()
                            )
                            if user_recipe and open_recipe:
                                rand_recipe = random.choice(
                                    [[user_recipe, "user_db"], [open_recipe, "open_db"]]
                                )
                                result[meal_time][type] = rand_recipe[0].title
                                if no_repeat:
                                    if rand_recipe[1] == "user_db":
                                        db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
                                    else:
                                        db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
                            elif user_recipe:
                                result[meal_time][type] = user_recipe.title
                            elif open_recipe:
                                result[meal_time][type] = open_recipe.title

                        elif db_user_recipes:
                            recipe = (
                                db_user_recipes.filter(type=type, meal_time__contains=meal_time)
                                .order_by("?")
                                .first()
                            )
                            if recipe:
                                result[meal_time][type] = recipe.title
                                if no_repeat:
                                    db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
                        elif db_open_recipes:
                            recipe = (
                                db_open_recipes.filter(type=type, meal_time__contains=meal_time)
                                .order_by("?")
                                .first()
                            )
                            if recipe:
                                result[meal_time][type] = recipe.title
                                if no_repeat:
                                    db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
                        #
                        if result[meal_time][type] is None:
                            result[meal_time][type] = "Нет рецептов"
    else:
        if meal_time == "breakfast" or meal_time == "after_tea" or meal_time == "snack":
            for recipe in recipes_with_products:
                if (
                    recipe[0].type in default_types
                    and meal_time in recipe[0].meal_time
                    and result[day][meal_time] is None
                ):
                    result[day][meal_time] = {
                        "recipe": recipe[0].title,
                        "find_by_products": True,
                        "all_days": True,
                    }
                    if recipe[1] == True:
                        for _day in result:
                            for _meal_time in result[day]:
                                if _meal_time == meal_time:
                                    result[_day][_meal_time] = {
                                        "recipe": recipe[0].title,
                                        "find_by_products": True,
                                        "all_days": True,
                                    }
                    recipes_with_products.remove(recipe)

            if result[day][meal_time] is None:
                if db_user_recipes and db_open_recipes:
                    user_recipe = (
                        db_user_recipes.filter(
                            type__in=default_types, meal_time__contains=meal_time
                        )
                        .order_by("?")
                        .first()
                    )
                    open_recipe = (
                        db_open_recipes.filter(
                            type__in=default_types, meal_time__contains=meal_time
                        )
                        .order_by("?")
                        .first()
                    )
                    if user_recipe and open_recipe:
                        rand_recipe = random.choice(
                            [[user_recipe, "user_db"], [open_recipe, "open_db"]]
                        )
                        result[day][meal_time] = rand_recipe[0].title
                        if no_repeat:
                            if rand_recipe[1] == "user_db":
                                db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
                            elif rand_recipe[1] == "open_db":
                                db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
                    elif user_recipe:
                        result[day][meal_time] = user_recipe.title
                        if no_repeat:
                            db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
                    elif open_recipe:
                        result[day][meal_time] = open_recipe.title
                        if no_repeat:
                            db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
                elif db_user_recipes:
                    recipe = (
                        db_user_recipes.filter(
                            type__in=default_types, meal_time__contains=meal_time
                        )
                        .order_by("?")
                        .first()
                    )
                    if recipe:
                        result[day][meal_time] = recipe.title
                        if no_repeat:
                            db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
                elif db_open_recipes:
                    recipe = (
                        db_open_recipes.filter(
                            type__in=default_types, meal_time__contains=meal_time
                        )
                        .order_by("?")
                        .first()
                    )
                    if recipe:
                        result[day][meal_time] = recipe.title
                        if no_repeat:
                            db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)

                if result[day][meal_time] is None:
                    result[day][meal_time] = "Нет рецептов"
        elif meal_time == "lunch" or meal_time == "dinner":
            for type in default_types:
                for recipe in recipes_with_products:
                    if (
                        recipe[0].type == type
                        and meal_time in recipe[0].meal_time
                        and result[day][meal_time][type] is None
                    ):
                        result[day][meal_time][type] = {
                            "recipe": recipe[0].title,
                            "find_by_products": True,
                            "all_days": recipe[1],
                        }
                        if recipe[1] == True:
                            for _day in result:
                                for _meal_time in result[day]:
                                    if _meal_time == "lunch":
                                        result[_day][_meal_time][type] = {
                                            "recipe": recipe[0].title,
                                            "find_by_products": True,
                                            "all_days": True,
                                        }
                        recipes_with_products.remove(recipe)
                if result[day][meal_time][type] is None:
                    if db_user_recipes and db_open_recipes:
                        user_recipe = (
                            db_user_recipes.filter(type=type, meal_time__contains=meal_time)
                            .order_by("?")
                            .first()
                        )
                        open_recipe = (
                            db_open_recipes.filter(type=type, meal_time__contains=meal_time)
                            .order_by("?")
                            .first()
                        )
                        if user_recipe and open_recipe:
                            rand_recipe = random.choice(
                                [[user_recipe, "user_db"], [open_recipe, "open_db"]]
                            )
                            result[day][meal_time][type] = rand_recipe[0].title
                            if no_repeat:
                                if rand_recipe[1] == "user_db":
                                    db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
                                elif rand_recipe[1] == "open_db":
                                    db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
                        elif user_recipe:
                            result[day][meal_time][type] = user_recipe.title
                            if no_repeat:
                                db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
                        elif open_recipe:
                            result[day][meal_time][type] = open_recipe.title
                            if no_repeat:
                                db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
                    elif db_user_recipes:
                        recipe = (
                            db_user_recipes.filter(type=type, meal_time__contains=meal_time)
                            .order_by("?")
                            .first()
                        )
                        if recipe:
                            result[day][meal_time][type] = recipe.title
                            if no_repeat:
                                db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
                    elif db_open_recipes:
                        recipe = (
                            db_open_recipes.filter(type=type, meal_time__contains=meal_time)
                            .order_by("?")
                            .first()
                        )
                        if recipe:
                            result[day][meal_time][type] = recipe.title
                            if no_repeat:
                                db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
                    if result[day][meal_time][type] is None:
                        result[day][meal_time][type] = "Нет рецептов"

    return db_user_recipes, db_open_recipes, result

    # Копия старого результата в views

    # if one_day:
    # for meal_time in result:
    #     #
    #     if meal_time == 'breakfast':
    #         db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #                     db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #                     no_repeat=no_repeat, one_day=one_day)

    # default_types = ['hot', 'salads', 'snacks', 'baking', 'billets', 'desserts']
    # if recipes_with_products is not None:
    #     for recipe in recipes_with_products:
    #         #
    #         if recipe[0].type in default_types and meal_time in recipe[0].meal_time and result[meal_time] is None:
    #             result[meal_time] = {'recipe':recipe[0].title, 'find_by_products': True}
    #             recipes_with_products.remove(recipe)
    # #
    # if result[meal_time] is None:

    #     if db_user_recipes and db_open_recipes:
    #         user_recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         open_recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if user_recipe and open_recipe:
    #             rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #             result[meal_time] = rand_recipe[0].title
    #             if no_repeat:
    #                 if rand_recipe[1] == 'user_db':
    #                     db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                 else:
    #                     db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)

    #         elif user_recipe:
    #             result[meal_time] = user_recipe.title
    #         elif open_recipe:
    #             result[meal_time] = open_recipe.title

    #     elif db_user_recipes:
    #         recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[meal_time] = recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #     elif db_open_recipes:
    #         recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[meal_time] = recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
    # #
    # if result[meal_time] is None:
    #     result[meal_time] = 'Нет рецептов'

    # if meal_time == 'lunch':
    #     #
    #     db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #              db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #              no_repeat=no_repeat, one_day=one_day)
    # default_types = ['soups', 'hot', 'salads']
    # result[meal_time] = {}
    # #
    # for type in default_types:
    #     if recipes_with_products is not None:
    #         for recipe in recipes_with_products:
    #             #
    #             if recipe[0].type == type and meal_time in recipe[0].meal_time and type not in result[meal_time]:
    #                 result[meal_time].update({type: {'recipe': recipe[0].title, 'find_by_products': True}})
    #                 recipes_with_products.remove(recipe)
    #     #
    #     if type not in result[meal_time]:
    #         result[meal_time].update({type: None})
    #     #
    #     if result[meal_time][type] is None:
    #         if db_user_recipes and db_open_recipes:
    #             user_recipe = db_user_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             open_recipe = db_open_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if user_recipe and open_recipe:
    #                 rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #                 result[meal_time][type] = rand_recipe[0].title
    #                 if no_repeat:
    #                     if rand_recipe[1] == 'user_db':
    #                         db_user_recipes =db_user_recipes.exclude(pk=user_recipe.pk)
    #                     else:
    #                         db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #             elif user_recipe:
    #                 result[meal_time][type] = user_recipe.title
    #             elif open_recipe:
    #                 result[meal_time][type] = open_recipe.title

    #         elif db_user_recipes:
    #             recipe = db_user_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if recipe:
    #                 result[meal_time][type] = recipe.title
    #                 if no_repeat:
    #                     db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #         elif db_open_recipes:
    #             recipe = db_open_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if recipe:
    #                 result[meal_time][type] = recipe.title
    #                 if no_repeat:
    #                     db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)

    #         if result[meal_time][type] is None:
    #             result[meal_time][type] = 'Нет рецептов'

    # if meal_time == 'after_tea':
    #     db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #              db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #              no_repeat=no_repeat, one_day=one_day)
    # default_types = ['baking', 'desserts']
    # if recipes_with_products is not None:
    #     for recipe in recipes_with_products:
    #         if recipe[0].type in default_types and meal_time in recipe[0].meal_time and result[meal_time] is None:
    #             result[meal_time] = {'recipe': recipe[0].title, 'find_by_products': True}
    #             recipes_with_products.remove(recipe)

    # if result[meal_time] is None:
    #     if db_user_recipes and db_open_recipes:
    #         user_recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         open_recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if user_recipe and open_recipe:
    #             rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #             result[meal_time] = rand_recipe[0].title
    #             if no_repeat:
    #                 if rand_recipe[1] == 'user_db':
    #                     db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                 else:
    #                     db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #         elif user_recipe:
    #             result[meal_time] = user_recipe.title
    #         elif open_recipe:
    #             result[meal_time] = open_recipe.title

    #     elif db_user_recipes:
    #         recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[meal_time] = recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #     elif db_open_recipes:
    #         recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[meal_time] = recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
    #     #
    #     if result[meal_time] is None:
    #         result[meal_time] = 'Нет рецептов'

    # if meal_time == 'snack':
    #     db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #              db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #              no_repeat=no_repeat, one_day=one_day)
    # default_types = ['billets', 'snacks']
    # if recipes_with_products is not None:
    #     for recipe in recipes_with_products:
    #         if recipe[0].type in default_types and meal_time in recipe[0].meal_time and result[meal_time] is None:
    #             result[meal_time] = {'recipe': recipe[0].title, 'find_by_products': True}
    #             recipes_with_products.remove(recipe)

    # if result[meal_time] is None:
    #     if db_user_recipes and db_open_recipes:
    #         user_recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         open_recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if user_recipe and open_recipe:
    #             rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #             result[meal_time] = rand_recipe[0].title
    #             if no_repeat:
    #                 if rand_recipe[1] == 'user_db':
    #                     db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                 else:
    #                     db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #         elif user_recipe:
    #             result[meal_time] = user_recipe.title
    #         elif open_recipe:
    #             result[meal_time] = open_recipe.title

    #     elif db_user_recipes:
    #         recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[meal_time] = recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #     elif db_open_recipes:
    #         recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[meal_time] = recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
    #     #
    #     if result[meal_time] is None:
    #         result[meal_time] = 'Нет рецептов'

    # if meal_time == 'dinner':
    #     db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #              db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #              no_repeat=no_repeat, one_day=one_day)
    # default_types = ['hot', 'salads']
    # result[meal_time] = {}
    # for type in default_types:
    #     if recipes_with_products is not None:
    #         for recipe in recipes_with_products:
    #             if recipe[0].type == type and meal_time in recipe[0].meal_time and type not in result[meal_time]:
    #                 result[meal_time].update({type: {'recipe': recipe[0].title, 'find_by_products': True}})
    #                 recipes_with_products.remove(recipe)

    #     if type not in result[meal_time]:
    #         result[meal_time][type] = None

    #     if result[meal_time][type] is None:
    #         if db_user_recipes and db_open_recipes:
    #             user_recipe = db_user_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             open_recipe = db_open_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if user_recipe and open_recipe:
    #                 rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #                 result[meal_time][type] = rand_recipe[0].title
    #                 if no_repeat:
    #                     if rand_recipe[1] == 'user_db':
    #                         db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                     else:
    #                         db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #             elif user_recipe:
    #                 result[meal_time][type] = user_recipe.title
    #             elif open_recipe:
    #                 result[meal_time][type] = open_recipe.title

    #         elif db_user_recipes:
    #             recipe = db_user_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if recipe:
    #                 result[meal_time][type] = recipe.title
    #                 if no_repeat:
    #                     db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #         elif db_open_recipes:
    #             recipe = db_open_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if recipe:
    #                 result[meal_time][type] = recipe.title
    #                 if no_repeat:
    #                     db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
    #         #
    #         if result[meal_time][type] is None:
    #             result[meal_time][type] = 'Нет рецептов'
    ## TODO: На неделю
    # else:
    #     for day in result:
    #         for meal_time in result[day]:
    #             if meal_time == 'breakfast':
    #                 db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #                          db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #                          no_repeat=no_repeat, one_day=one_day, day=day)
    # default_types = ['hot', 'salads', 'snacks', 'baking', 'billets', 'desserts']
    # for recipe in recipes_with_products:
    #     if recipe[0].type in default_types and meal_time in recipe[0].meal_time and result[day][meal_time] is None:
    #         result[day][meal_time] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': True}
    #         if recipe[1] == True:
    #             for _day in result:
    #                 for _meal_time in result[day]:
    #                     if _meal_time == 'breakfast':
    #                         result[_day][_meal_time] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': True}
    #         recipes_with_products.remove(recipe)

    # if result[day][meal_time] is None:
    #     if db_user_recipes and db_open_recipes:
    #         user_recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         open_recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if user_recipe and open_recipe:
    #             rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #             result[day][meal_time] = rand_recipe[0].title
    #             if no_repeat:
    #                 if rand_recipe[1] == 'user_db':
    #                     db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                 elif rand_recipe[1] == 'open_db':
    #                     db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #         elif user_recipe:
    #             result[day][meal_time] = user_recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #         elif open_recipe:
    #             result[day][meal_time] = open_recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #     elif db_user_recipes:
    #         recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[day][meal_time] = recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #     elif db_open_recipes:
    #         recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[day][meal_time] = recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)

    #     if result[day][meal_time] is None:
    #         result[day][meal_time] = 'Нет рецептов'

    # if meal_time == 'lunch':
    #     db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #              db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #              no_repeat=no_repeat, one_day=one_day, day=day)
    # default_types = ['soups', 'hot', 'salads']
    # for type in default_types:
    #     for recipe in recipes_with_products:
    #         if recipe[0].type == type and meal_time in recipe[0].meal_time and result[day][meal_time][type] is None:
    #             result[day][meal_time][type] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': recipe[1]}
    #             if recipe[1] == True:
    #                 for _day in result:
    #                     for _meal_time in result[day]:
    #                         if _meal_time == 'lunch':
    #                             result[_day][_meal_time][type] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': True}
    #             recipes_with_products.remove(recipe)
    #     if result[day][meal_time][type] is None:
    #         if db_user_recipes and db_open_recipes:
    #             user_recipe = db_user_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             open_recipe = db_open_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if user_recipe and open_recipe:
    #                 rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #                 result[day][meal_time][type] = rand_recipe[0].title
    #                 if no_repeat:
    #                     if rand_recipe[1] == 'user_db':
    #                         db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                     elif rand_recipe[1] == 'open_db':
    #                         db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #             elif user_recipe:
    #                 result[day][meal_time][type] = user_recipe.title
    #                 if no_repeat:
    #                     db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #             elif open_recipe:
    #                 result[day][meal_time][type] = open_recipe.title
    #                 if no_repeat:
    #                     db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #         elif db_user_recipes:
    #             recipe = db_user_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if recipe:
    #                 result[day][meal_time][type] = recipe.title
    #                 if no_repeat:
    #                     db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #         elif db_open_recipes:
    #             recipe = db_open_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if recipe:
    #                 result[day][meal_time][type] = recipe.title
    #                 if no_repeat:
    #                     db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
    #         if result[day][meal_time][type] is None:
    #             result[day][meal_time][type] = 'Нет рецептов'

    # after_tea
    # if meal_time == 'after_tea':
    #     db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #              db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #              no_repeat=no_repeat, one_day=one_day, day=day)
    # default_types = ['baking', 'desserts']
    # for recipe in recipes_with_products:
    #     if recipe[0].type in default_types and meal_time in recipe[0].meal_time and result[day][meal_time] is None:
    #         result[day][meal_time] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': recipe[1]}
    #         if recipe[1] == True:
    #             for _day in result:
    #                 for _meal_time in result[day]:
    #                     if _meal_time == 'after_tea':
    #                         result[_day][_meal_time] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': True}
    #         recipes_with_products.remove(recipe)
    # if result[day][meal_time] is None:
    #     if db_user_recipes and db_open_recipes:
    #         user_recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         open_recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if user_recipe and open_recipe:
    #             rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #             result[day][meal_time] = rand_recipe[0].title
    #             if no_repeat:
    #                 if rand_recipe[1] == 'user_db':
    #                     db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                 elif rand_recipe[1] == 'open_db':
    #                     db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #         elif user_recipe:
    #             result[day][meal_time] = user_recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #         elif open_recipe:
    #             result[day][meal_time] = open_recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #     elif db_user_recipes:
    #         recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[day][meal_time] = recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #     elif db_open_recipes:
    #         recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[day][meal_time] = recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
    #     if result[day][meal_time] is None:
    #         result[day][meal_time] = 'Нет рецептов'

    # snack
    # if meal_time == 'snack':
    #     db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #              db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #              no_repeat=no_repeat, one_day=one_day, day=day)
    # default_types = ['snacks', 'baking']
    # for recipe in recipes_with_products:
    #     if recipe[0].type in default_types and meal_time in recipe[0].meal_time and result[day][meal_time] is None:
    #         result[day][meal_time] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': recipe[1]}
    #         if recipe[1] == True:
    #             for _day in result:
    #                 for _meal_time in result[day]:
    #                     if _meal_time == 'snack':
    #                         result[_day][_meal_time] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': True}
    #         recipes_with_products.remove(recipe)
    # if result[day][meal_time] is None:
    #     if db_user_recipes and db_open_recipes:
    #         user_recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         open_recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if user_recipe and open_recipe:
    #             rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #             result[day][meal_time] = rand_recipe[0].title
    #             if no_repeat:
    #                 if rand_recipe[1] == 'user_db':
    #                     db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                 elif rand_recipe[1] == 'open_db':
    #                     db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #         elif user_recipe:
    #             result[day][meal_time] = user_recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #         elif open_recipe:
    #             result[day][meal_time] = open_recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #     elif db_user_recipes:
    #         recipe = db_user_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[day][meal_time] = recipe.title
    #             if no_repeat:
    #                 db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #     elif db_open_recipes:
    #         recipe = db_open_recipes.filter(type__in=default_types, meal_time__contains=meal_time).order_by('?').first()
    #         if recipe:
    #             result[day][meal_time] = recipe.title
    #             if no_repeat:
    #                 db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
    #     if result[day][meal_time] is None:
    #         result[day][meal_time] = 'Нет рецептов'

    # dinner
    # if meal_time == 'dinner':
    #     db_user_recipes, db_open_recipes, result = generate(meal_time=meal_time, result=result, recipes_with_products=recipes_with_products,
    #              db_user_recipes=db_user_recipes, db_open_recipes=db_open_recipes,
    #              no_repeat=no_repeat, one_day=one_day, day=day)

    # default_types = ['hot', 'salads']
    # for type in default_types:
    #     for recipe in recipes_with_products:
    #         if recipe[0].type == type and meal_time in recipe[0].meal_time and result[day][meal_time][type] is None:
    #             result[day][meal_time][type] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': recipe[1]}
    #             if recipe[1] == True:
    #                 for _day in result:
    #                     for _meal_time in result[day]:
    #                         if _meal_time == 'dinner':
    #                             result[_day][_meal_time][type] = {'recipe': recipe[0].title, 'find_by_products': True, 'all_days': True}
    #             recipes_with_products.remove(recipe)
    #     if result[day][meal_time][type] is None:
    #         if db_user_recipes and db_open_recipes:
    #             user_recipe = db_user_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             open_recipe = db_open_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if user_recipe and open_recipe:
    #                 rand_recipe = random.choice([[user_recipe, 'user_db'], [open_recipe, 'open_db']])
    #                 result[day][meal_time][type] = rand_recipe[0].title
    #                 if no_repeat:
    #                     if rand_recipe[1] == 'user_db':
    #                         db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #                     elif rand_recipe[1] == 'open_db':
    #                         db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #             elif user_recipe:
    #                 result[day][meal_time][type] = user_recipe.title
    #                 if no_repeat:
    #                     db_user_recipes = db_user_recipes.exclude(pk=user_recipe.pk)
    #             elif open_recipe:
    #                 result[day][meal_time][type] = open_recipe.title
    #                 if no_repeat:
    #                     db_open_recipes = db_open_recipes.exclude(pk=open_recipe.pk)
    #         elif db_user_recipes:
    #             recipe = db_user_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if recipe:
    #                 result[day][meal_time][type] = recipe.title
    #                 if no_repeat:
    #                     db_user_recipes = db_user_recipes.exclude(pk=recipe.pk)
    #         elif db_open_recipes:
    #             recipe = db_open_recipes.filter(type=type, meal_time__contains=meal_time).order_by('?').first()
    #             if recipe:
    #                 result[day][meal_time][type] = recipe.title
    #                 if no_repeat:
    #                     db_open_recipes = db_open_recipes.exclude(pk=recipe.pk)
    #         if result[day][meal_time][type] is None:
    #             result[day][meal_time][type] = 'Нет рецептов'

    return result
