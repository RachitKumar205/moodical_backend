
# Moodical Backend

Moodical is a website that suggests music based on the mood of the user, which is predicted using a live feed captured from the user's webcam, and running a pre-trained model to recognise emotions.






## Installation

* Install the project

```bash
   pip install -r requirements.txt
```

* Create a super-user

```bash
   python manage.py createsuperuser
```

* Run the local development server

```bash
   python manage.py runserver
```

* Login to django admin panel (http://localhost:8000/admin) and add songs along with the mood tags


