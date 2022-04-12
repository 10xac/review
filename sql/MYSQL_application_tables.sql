
-- -----------------------------------------------------
-- Schema tenxdb
-- -----------------------------------------------------





-- -----------------------------------------------------
-- Table `applicant_information`
-- -----------------------------------------------------

CREATE TABLE `applicant_information` (
	`time_stamp` varchar(20) NOT NULL,
	`email` varchar(255) NOT NULL UNIQUE,
	`firstname` TEXT NOT NULL,
	`english_level` TEXT(30) NOT NULL,
	`commitment` BOOLEAN NOT NULL,
	`self_funding` BOOLEAN NOT NULL,
	`graduated` BOOLEAN NOT NULL,
	`renowned_idea` varchar(2000) NOT NULL,
	`nationality` TEXT NOT NULL,
	`city` TEXT NOT NULL,
	`date_of_birth` DATE NOT NULL,
	`gender` TEXT NOT NULL,
	`education_level` varchar(100) NOT NULL,
	`field_of_study` varchar(100) NOT NULL,
	`name_of_instituition` TEXT NOT NULL,
	`honours` varchar(500) NOT NULL DEFAULT 'NULL',
	`github_profile` varchar(100) NOT NULL,
	`referee_name` varchar(100) NOT NULL DEFAULT 'NULL',
	`previously_applied` BOOLEAN NOT NULL,
	`mode_of_discovery` TEXT NOT NULL,
	`work_experience` TEXT NOT NULL,
	`work_experience_details` TEXT(1000) NOT NULL ,
	`python_proficiency` INT(4) NOT NULL,
	`sql_proficiency` INT(4) NOT NULL,
	`statistics_proficiency` INT(4) NOT NULL,
	`algebra_proficiency` INT(4) NOT NULL,
	`project_compeleted` INT(4) NOT NULL,
	`data_science_profile` varchar(100) NOT NULL DEFAULT 'NULL',
	`self_taught` TEXT(1000) NOT NULL ,
	`Accept_terms_and_conditions` BOOLEAN NOT NULL,
	`occupation` varchar(255) NOT NULL,
	`linkedIn_profile` varchar(100) NOT NULL,
	`reason_to_join` varchar(1000) NOT NULL,
	`current_batch` varchar(20) NOT NULL,
	`previously_applied_batch` varchar(20) NOT NULL,
	`stage_to_pevious_application` varchar(200) NOT NULL,
	`work_experience_month` varchar(200) NOT NULL,
	`applicant_id` INT NOT NULL AUTO_INCREMENT,
	`batch` varchar(255) NOT NULL,
	`2nd_reviewer_id` INT(4) NOT NULL,
	`3rd_reviewer_id` INT(4) NOT NULL,
	`accepted` varchar(10) NOT NULL,
	`3rd_reviewer_accepted` varchar(10) NOT NULL,
	`2nd_reviewer_accepted` varchar(10) NOT NULL,
	PRIMARY KEY (`applicant_id`)
);

-- -----------------------------------------------------
-- Table `applicantInterviewResult`
-- -----------------------------------------------------

CREATE TABLE `ApplicantInterviewResult` (
	`interviewer_email` varchar(255) NOT NULL,
	`interviewee_email` varchar(255) NOT NULL,
	`on_time` BOOLEAN NOT NULL,
	`communication_skill` TEXT(50) NOT NULL,
	`q1` TEXT(50) NOT NULL,
	`q2` TEXT(50) NOT NULL,
	`q3` TEXT(50) NOT NULL,
	`payforward_confirmation` BOOLEAN NOT NULL,
	`fulltime_confirmation` BOOLEAN NOT NULL,
	`selffund_confirmation` BOOLEAN NOT NULL,
	`mlflow_design_understanding` TEXT(50) NOT NULL,
	`code_understanding` TEXT(50) NOT NULL,
	`comments` TEXT(200) NOT NULL,
	`suitable` BOOLEAN NOT NULL,
	`predict_job_readiness` TEXT(50) NOT NULL,
	`predict_distinction_graduation` TEXT(50) NOT NULL,
	`predict_first_job_interview_pass` TEXT(50) NOT NULL,
	`predict_outstanding_social_contribution` TEXT(50) NOT NULL
);

-- -----------------------------------------------------
-- Table `reviewer`
-- -----------------------------------------------------

CREATE TABLE `reviewer` (
	`reviewer_id` INT(4) NOT NULL AUTO_INCREMENT,
	`reviewer_email` varchar(255) NOT NULL UNIQUE,
	`firstname` varchar(255) NOT NULL,
	`lastname` varchar(255) NOT NULL,
	`reviewer_group` varchar(255) NOT NULL,
	PRIMARY KEY (`reviewer_id`)
);









