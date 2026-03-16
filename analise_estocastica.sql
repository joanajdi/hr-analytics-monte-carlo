CREATE DATABASE analise_estocastica;
USE analise_estocastica;

CREATE TABLE employee_survey (
    EmpID INT PRIMARY KEY,
    Gender VARCHAR(20),
    Age INT,
    MaritalStatus VARCHAR(20),
    JobLevel VARCHAR(30),
    Experience INT,
    Dept VARCHAR(50),
    EmpType VARCHAR(30),
    WLB INT,                   -- Work-Life Balance
    WorkEnv INT,               -- Work Environment Satisfaction
    PhysicalActivityHours FLOAT,
    Workload INT,
    Stress INT,
    SleepHours FLOAT,
    CommuteMode VARCHAR(30),
    CommuteDistance FLOAT,
    NumCompanies INT,
    TeamSize INT,
    NumReports INT,
    EduLevel VARCHAR(30),
    haveOT VARCHAR(10),        -- Overtime (True/False)
    TrainingHoursPerYear INT,
    JobSatisfaction INT
);

SELECT COUNT(*) FROM employee_survey;