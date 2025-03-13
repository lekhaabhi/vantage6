""" Sample code to test the federated algorithm with a mock client
"""
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from vantage6.algorithm.tools.mock_client import MockAlgorithmClient

from v6_logistic_regression_py.helper import initialize_model


# Start mock client
data_directory = Path('./v6_logistic_regression_py') / 'local'
dataset_1 = {"database": data_directory / "data1.csv", "db_type": "csv"}
dataset_2 = {"database": data_directory / "data2.csv", "db_type": "csv"}

client = MockAlgorithmClient(
    datasets=[[dataset_1], [dataset_2]],
    module='v6_logistic_regression_py'
)

# Get mock organisations
organizations = client.organization.list()
print(f"Participating organizations: {organizations}")
ids = [organization['id'] for organization in organizations]

# Check master method
master_task = client.task.create(
    input_={
        'master': True,
        'method': 'master',
        'kwargs': {
            'org_ids': [0, 1],
            'predictors': ['t', 'n', 'm'],
            'outcome': 'vital_status',
            'classes': ['alive', 'dead'],
            'max_iter': 100,
            'delta': 0.0001
        }
    },
    organizations=[0]
)
results = client.result.get(master_task.get('id'))
model = initialize_model(LogisticRegression, results['model_attributes'])#
iteration = results['iteration']
print(model.coef_, model.intercept_)
print(f'Number of iterations: {iteration}')

print([model.intercept_.tolist(), model.coef_.tolist()])
# Check validation method
master_task = client.task.create(
    input_={
        'master': False,
        'method': 'run_validation',
        'kwargs': {
            'parameters': [model.intercept_.tolist(), model.coef_.tolist()],
            'classes': ['alive', 'dead'],
            'predictors': ['t', 'n', 'm'],
            'outcome': 'vital_status',
        }
    },
    organizations=[0]
)
results = client.result.get(master_task.get('id'))
accuracy = results['score']
cm = results['confusion_matrix']
print(f'Accuracy: {accuracy}')
print(f'Confusion matrix: {cm}')
