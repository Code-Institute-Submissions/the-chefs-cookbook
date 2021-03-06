import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_DBNAME'] = os.getenv('MONGO_DBNAME')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')


mongo = PyMongo(app)


# Home
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


'''
User Login and Registeration taken from Pretty Printed youtube 
video https://www.youtube.com/watch?v=vVx1737auSE
'''

# User Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username' : request.form['username']})
        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), 
                            login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                flash("You have successfully logged in")
                return redirect(url_for('index'))
            flash("Invalid Username or Password. Try again.")
        flash("Invalid Username or Password. Try again.")    
    return render_template('login.html', title='Login')


# User Register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form.get('username')})

        if existing_user is None:
            hash_password = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username' :request.form['username'], 'password' : hash_password})
            session['username'] = request.form['username']

            flash('Lets get cooking!!')
            return redirect(url_for('index'))

        flash('That username already exists')
    
    return render_template('register.html', title='Register')


'''
Users can logout off their account and session.pop will 
clear the session.
'''
# User Logout
@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
    flash('You have been logged out')
    return redirect(url_for('index'))


# Display Recipes by Category
@app.route('/get_starter', methods=['GET'])
def get_starter():
    return render_template('recipes.html', 
                           title='Starters', 
                           recipes=mongo.db.recipes.
                           find({'recipe_cat': 'Starter'}))


@app.route('/get_main', methods=['GET'])
def get_main():
    return render_template('recipes.html', title='Main Courses',
                            recipes=mongo.db.recipes.
                            find({'recipe_cat': 'Main Course'}))


@app.route('/get_dessert', methods=['GET'])
def get_dessert():
    return render_template('recipes.html', title='Desserts',
                            recipes=mongo.db.recipes.find
                            ({'recipe_cat': 'Dessert'}))


@app.route('/get_lunch', methods=['GET'])
def get_lunch():
    return render_template('recipes.html', title='Lunch',
                            recipes=mongo.db.recipes.find
                            ({'recipe_cat': 'Lunch'}))


@app.route('/get_breakfast', methods=['GET'])
def get_breakfast():
    return render_template('recipes.html', title='Breakfast',
                            recipes=mongo.db.recipes.find
                            ({'recipe_cat': 'Breakfast'}))


@app.route('/get_slowcooker', methods=['GET'])
def get_slowcooker():
    return render_template('recipes.html', title='Slow Cooker',
                            recipes=mongo.db.recipes.find
                            ({'recipe_cat': 'Slow Cooker'}))


@app.route('/get_vegan', methods=['GET'])
def get_vegan():
    return render_template('recipes.html', title='Vegan',
                            recipes=mongo.db.recipes.find
                            ({'recipe_cat': 'Vegan'}))


@app.route('/get_vegetarian', methods=['GET'])
def get_vegetarian():
    return render_template('recipes.html', title='Vegetarian',
                            recipes=mongo.db.recipes.find
                            ({'recipe_cat': 'Vegetarian'}))



@app.route('/get_drinks', methods=['GET'])
def get_drinks():
    return render_template('recipes.html', title='Drinks',
                            recipes=mongo.db.recipes.find
                            ({'recipe_cat': 'Drinks'}))


# View All Recipes
@app.route('/get_recipes')
def get_recipes():
    return render_template('recipes.html', recipes=mongo.db.recipes.find())


# Show Individual Recipe
@app.route('/viewrecipe/<recipe_id>')
def recipes(recipe_id):
    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('viewrecipe.html', title=recipe['recipe_name'], recipe=recipe)


# Add Recipe
@app.route('/add_recipe')
def add_recipe():
    return render_template('addrecipe.html', title='Add Recipe',
                           categories=mongo.db.categories.find(),
                           difficulty=mongo.db.difficulty.find())


# Insert Recipe
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    recipes = mongo.db.recipes
    new_recipe = {
        'recipe_name': request.form.get('recipe_name'),
        'recipe_description': request.form.get('recipe_description'),
        'recipe_prep': request.form.get('recipe_prep'),
        'recipe_cook': request.form.get('recipe_cook'),
        'recipe_serving': request.form.get('recipe_serving'),
        'recipe_image': request.form.get('recipe_image'),
        'recipe_ingredients': request.form.getlist('recipe_ingredients'),
        'recipe_method': request.form.getlist('recipe_method'),
        'recipe_cat': request.form.get('recipe_cat'),
        'recipe_dif': request.form.get('recipe_dif'),
        'recipe_author': request.form.get('recipe_author')
    }
    recipes.insert_one(new_recipe)
    flash('You have added a new recipe successfully!', 'success')
    return redirect(url_for('get_recipes'))


# Edit and Update Recipe
@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
# Get the recipe that matches the recipe id 
    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    categories = mongo.db.categories.find()
    difficulty = mongo.db.difficulty.find()
    return render_template('editrecipe.html',
                           title='Edit Recipe',
                           recipe=recipe,
                           categories=categories,
                           difficulty=difficulty
                            )


# Update Recipe
@app.route('/edit_recipe/<recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    recipe = mongo.db.recipes
# Access recipes collection and call the update function
    recipe.replace_one({'_id': ObjectId(recipe_id)},
                  {
                    'recipe_name': request.form.get('recipe_name'),
                    'recipe_description': request.form.get('recipe_description'),
                    'recipe_prep': request.form.get('recipe_prep'),
                    'recipe_cook': request.form.get('recipe_cook'),
                    'recipe_serving': request.form.get('recipe_serving'),
                    'recipe_image': request.form.get('recipe_image'),
                    'recipe_ingredients': request.form.getlist('recipe_ingredients'),
                    'recipe_method': request.form.getlist('recipe_method'),
                    'recipe_cat': request.form.get('recipe_cat'),
                    'recipe_dif': request.form.get('recipe_dif'),
                    'recipe_author': request.form.get('recipe_author')
                    })
    flash('Your recipe has been updated')
    return redirect(url_for('recipes', recipe_id=recipe_id))


# Delete Recipe
@app.route('/delete_recipe<recipe_id>')
def delete_recipe(recipe_id):
    mongo.db.recipes.delete_one({'_id': ObjectId(recipe_id)})
    flash("This recipe has been deleted")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host=os.getenv('IP'), port=os.getenv('PORT'), debug=False)