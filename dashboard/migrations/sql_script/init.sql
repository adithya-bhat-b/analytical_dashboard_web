INSERT INTO department (department_id, name, location, date_of_innaugration) VALUES (1,'Product', 'Bengaluru', '2019-07-1'),(2,'Engineering', 'Redwood City', '2019-07-1'),(3,'Marketing', 'New York', '2019-07-1');
INSERT INTO teams (team_id, department_id_id, average_pay) VALUES (1,1, '20000'),(2,2,'30000'),(3,1,'40000');
INSERT INTO users (user_id,first_name,last_name,team_id_id) VALUES (1,'Navneet','Menon', 1),(2,'Kailash','Raghav',2),(3,'Johnson','Stevenson', 1);
UPDATE teams SET team_lead_id_id = 3 WHERE team_id='1';
UPDATE teams SET team_lead_id_id = 2 WHERE team_id='2';
UPDATE teams SET team_lead_id_id = 1 WHERE team_id='3';
INSERT INTO objectives (objective_id,user_id_id,objective_text) VALUES (1,1, 'Improve HR Processes'),(2,2, 'Raise participation in Surveys'),(3,2, 'Improve Engineering Processes');
INSERT INTO keyresults (keyresult_id,objective_id_id,keyresult_text,status,due_date,updated_date) VALUES (1,1,'Set up onboarding process','Pending', '2020-08-11', '2020-08-04'),(2,1,'Conduct 3 Surveys','Complete', '2020-08-11', '2020-08-03'),(3,1,'Implement organization chart','Complete', '2020-08-11', '2020-07-27');
INSERT INTO keyresults (keyresult_id,objective_id_id,keyresult_text,status,due_date,updated_date) VALUES (4,2,'Draw up survey participation incentive plan','Complete', '2020-08-11', '2020-07-25'),(5,2,'Create Survey non-participation list','Complete', '2020-08-11', '2020-08-01'),(6,2,'Speak with survey vendor regarding employee complaints','Complete', '2020-08-11', '2020-08-02');