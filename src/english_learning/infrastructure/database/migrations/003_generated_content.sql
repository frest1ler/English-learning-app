CREATE INDEX IF NOT EXISTS idx_generated_review ON generated_content(review_status, content_type);
CREATE INDEX IF NOT EXISTS idx_exercises_review ON exercises(review_status, exercise_type);
