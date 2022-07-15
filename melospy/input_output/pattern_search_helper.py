from datetime import datetime

import pytz


def increment_generated_files_counter(search, db_session, app_name):
    if app_name == 'melospy-api':
        search.generated_files_count = search.generated_files_count + 1
        db_session.commit()

def set_generation_completed(generation_type, search, db_session, app_name):
    if app_name == 'melospy-api':
        if generation_type == 'audio':
            search.audio_generation_completed_at = datetime.now(pytz.utc)
        if generation_type == 'score':
            search.score_generation_completed_at = datetime.now(pytz.utc)

        db_session.commit()
