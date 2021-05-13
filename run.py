# from flask_script import Manager
from flask_migrate import Migrate
from app import create_app, db

app = create_app(config_name="development")
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)

migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()
