CREATE INDEX IF NOT EXISTS idx_word_progress_due ON word_progress(due_at);
CREATE INDEX IF NOT EXISTS idx_topic_progress_mastery ON topic_progress(mastery);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON study_sessions(started_at);
