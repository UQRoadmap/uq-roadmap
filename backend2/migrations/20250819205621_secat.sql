CREATE TABLE secats (
  secat_id      uuid PRIMARY KEY,
  course_id     uuid REFERENCES courses(course_id),
  num_enrolled  bigint NOT NULL,
  num_responses bigint NOT NULL,
  response_rate real NOT NULL
);

CREATE TABLE secat_questions(
  question_id       uuid PRIMARY KEY,
  secat_id          uuid REFERENCES secats(secat_id),
  name              text NOT NULL,
  strongly_agree    real NOT NULL,
  agree             real NOT NULL,
  middle            real NOT NULL,
  disagree          real NOT NULL,
  strongly_disagree real NOT NULL
);
