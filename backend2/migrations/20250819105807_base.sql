CREATE TYPE course_level_t AS ENUM (
  'undergraduate',
  'postgraduate',
  'postgraduate coursework',
  'uq college',
  'non-award',
  'other'
);

CREATE TYPE course_mode_t AS ENUM (
  'Work Experience',
  'In Person',
  'External',
  'Internal',
  'Weekend',
  'July Intensive',
  'Off-Shore',
  'Off-Campus',
  'Intensive',
  'Web Based',
  'Remote',
  'Flexible Delivery'
);

CREATE TYPE course_semester_t AS ENUM (
  'Research Quarter 1',
  'Research Quarter 2',
  'Research Quarter 3',
  'Research Quarter 4',
  'SFC Enrolment Year',
  'Semester 1',
  'Semester 2',
  'Summer Semester',
  'Trimester 1',
  'Trimester 2',
  'Trimester 3',
  'UQ College Intake 1',
  'UQ College Intake 2',
  'Other'
);

CREATE TABLE courses (
  course_id     uuid PRIMARY KEY,
  category      text NOT NULL,
  code          text NOT NULL,
  name          text NOT NULL,
  description   text NOT NULL,
  level         course_level_t NOT NULL,
  num_units     smallint NOT NULL CHECK (num_units >= 0),
  attendance_mode course_mode_t NOT NULL,
  active        boolean NOT NULL DEFAULT true,
  semesters     course_semester_t[] NOT NULL,
  CONSTRAINT courses_category_code_uk UNIQUE (category, code)
);

CREATE INDEX idx_courses_category_code ON courses (category, code);
