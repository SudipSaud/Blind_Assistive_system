"""
Database Management Module
Handles all interactions with the TinyDB database.
This class acts as an abstraction layer, so if we ever want to switch
to a more powerful database (like SQLite or MongoDB), we only need to
change the code in this file.
"""
import logging
from tinydb import TinyDB, Query

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='memory.json'):
        """
        Initializes the DatabaseManager.
        Args:
            db_path: The path to the database file.
        """
        try:
            self.db = TinyDB(db_path)
            self.people_table = self.db.table('people')
            self.objects_table = self.db.table('personal_objects')
            self.scene_history_table = self.db.table('scene_history')
            self.feedback_table = self.db.table('feedback')
            self.ai_correction_feedback_table = self.db.table('ai_correction_feedback') # New table for AI corrections
            logger.info(f"Database initialized successfully at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.db = None

    def add_scene(self, timestamp: str, detected_objects: list, detected_people: list, image_summary: str):
        """Adds a new scene record to the scene history."""
        if not self.db:
            return None
        try:
            scene_id = self.scene_history_table.insert({
                'timestamp': timestamp,
                'detected_objects': detected_objects,
                'detected_people': detected_people,
                'image_summary': image_summary
            })
            return scene_id
        except Exception as e:
            logger.error(f"Error adding scene to database: {e}")
            return None

    def get_last_scene(self):
        """Retrieves the most recent scene from the history."""
        if not self.db or not self.scene_history_table:
            return None
        try:
            # TinyDB doesn't have a built-in "last" function, so we get all and take the last one.
            # For a large DB, this is inefficient, but it's fine for our current scale.
            # This is a key area we would optimize when upgrading the DB.
            all_scenes = self.scene_history_table.all()
            return all_scenes[-1] if all_scenes else None
        except Exception as e:
            logger.error(f"Error retrieving last scene: {e}")
            return None

    def add_ai_correction_feedback(self, event_id: str, incorrect_ai_response: str, user_correction_text: str, timestamp_utc: str):
        """Adds AI correction feedback from the user to the database."""
        if not self.db:
            return None
        try:
            feedback_id = self.ai_correction_feedback_table.insert({
                'event_id': event_id,
                'incorrect_ai_response': incorrect_ai_response,
                'user_correction_text': user_correction_text,
                'timestamp': timestamp_utc
            })
            logger.info(f"Logged AI correction feedback {feedback_id} for event {event_id}")
            return feedback_id
        except Exception as e:
            logger.error(f"Error adding AI correction feedback to database: {e}")
            return None

    def add_feedback(self, event_id: str, feedback: str, timestamp: str):
        """Adds user feedback to the database."""
        if not self.db:
            return None
        try:
            feedback_id = self.feedback_table.insert({
                'event_id': event_id,
                'feedback': feedback,
                'timestamp': timestamp
            })
            return feedback_id
        except Exception as e:
            logger.error(f"Error adding feedback to database: {e}")
            return None

    def learn_personal_object(self, object_name: str, embedding: list):
        """
        Saves or updates a personal object's feature embedding.
        Args:
            object_name: The name of the object (e.g., "my keys", "wallet").
            embedding: The feature vector (embedding) of the object's image.
        """
        if not self.db:
            return None
        try:
            Object = Query()
            # Using upsert: update if exists, insert if not.
            self.objects_table.upsert(
                {'name': object_name.lower(), 'embedding': embedding},
                Object.name == object_name.lower()
            )
            logger.info(f"Learned or updated personal object: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Error learning personal object '{object_name}': {e}")
            return False

    def get_all_personal_objects(self):
        """Retrieves all known personal objects and their embeddings."""
        if not self.db:
            return []
        try:
            return self.objects_table.all()
        except Exception as e:
            logger.error(f"Error retrieving all personal objects: {e}")
            return []

    def get_personal_object_by_name(self, object_name: str):
        """
        Retrieves a specific personal object by its name.
        Args:
            object_name: The name of the object to find.
        """
        if not self.db:
            return None
        try:
            Object = Query()
            result = self.objects_table.get(Object.name == object_name.lower())
            return result
        except Exception as e:
            logger.error(f"Error retrieving object '{object_name}': {e}")
            return None

    # --- Methods for managing people (face recognition) ---
    
    def add_person(self, name: str, face_embedding: list):
        """
        Adds a new person with their face embedding to the database.
        Args:
            name: The person's name.
            face_embedding: The face embedding as a list.
        Returns:
            True if successful, False otherwise.
        """
        if not self.db:
            return False
        try:
            Person = Query()
            # Check if person already exists
            existing = self.people_table.get(Person.name == name)
            if existing:
                logger.warning(f"Person '{name}' already exists in database. Updating their face embedding.")
                self.people_table.update(
                    {'face_embedding': face_embedding},
                    Person.name == name
                )
            else:
                self.people_table.insert({
                    'name': name,
                    'face_embedding': face_embedding
                })
            logger.info(f"Successfully added/updated person: {name}")
            return True
        except Exception as e:
            logger.error(f"Error adding person '{name}': {e}")
            return False

    def get_all_people(self):
        """
        Retrieves all known people and their face embeddings from the database.
        Returns:
            A list of dictionaries, each containing 'name' and 'face_embedding'.
        """
        if not self.db:
            return []
        try:
            return self.people_table.all()
        except Exception as e:
            logger.error(f"Error retrieving all people: {e}")
            return []

    def get_person_by_name(self, name: str):
        """
        Retrieves a specific person by their name.
        Args:
            name: The person's name.
        Returns:
            A dictionary with 'name' and 'face_embedding', or None if not found.
        """
        if not self.db:
            return None
        try:
            Person = Query()
            result = self.people_table.get(Person.name == name)
            return result
        except Exception as e:
            logger.error(f"Error retrieving person '{name}': {e}")
            return None

    def close(self):
        """Closes the database connection."""
        if self.db:
            self.db.close()
            logger.info("Database connection closed.")

