-- -----------------------------------------------------
-- Table `applicant_information`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS applicant_information (
applicant_id SERIAL PRIMARY KEY,
comfortability_speaking_english BOOLEAN NOT NULL,
commitment BOOLEAN NOT NULL,
self_funding BOOLEAN NOT NULL,
graduated BOOLEAN NOT NULL,
awareness_to_payback BOOLEAN NOT NULL,
renowned_idea VARCHAR(2000) NOT NULL,
date_of_birth DATE NOT NULL,
education_level VARCHAR(100) NOT NULL,
field_of_study VARCHAR(100) NOT NULL,
honours VARCHAR(500) DEFAULT NULL,
github_profile VARCHAR(100) NOT NULL,
referee_name TEXT DEFAULT NULL,
mode_of_discovery TEXT NOT NULL,
work_experience TEXT DEFAULT NULL,
work_experience_details TEXT DEFAULT NULL,
python_proficiency INT NOT NULL,
sql_proficiency INT NOT NULL,
statistics_proficiency INT NOT NULL,
algebra_proficiency INT NOT NULL,
data_science_project TEXT NOT NULL,
data_science_profile VARCHAR(100) DEFAULT NULL,
self_taught VARCHAR(5000) DEFAULT NULL,
proceed_to_stage2 TEXT DEFAULT NULL;
reviewer_id INT DEFAULT NULL,
accepted VARCHAR(10) DEFAULT NULL);
COMMENT ON TABLE applicant_information IS 'store all general applicant information required for review';

-- -----------------------------------------------------
-- Table `REVIWER_INFO`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS reviewer (
reviewer_id SERIAL PRIMARY KEY,
reviewr_email VARCHAR(255) NOT NULL,
firstname TEXT NOT NULL,
lastname TEXT NOT NULL);
COMMENT ON TABLE reviewer IS 'store all general reviewer information';
