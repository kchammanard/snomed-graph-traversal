import collections
from py2neo import Graph, NodeMatcher, RelationshipMatcher
import tkinter as tk
from tkinter import messagebox

class DifferentialDiagnosis:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "snomedctneo4j"))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)

    def calculate_diagnosis_probabilities(self, user_symptoms):
        start_node = self.node_matcher.match("Node", name="Start").first()
        current_node = self.rel_matcher.match(nodes=[start_node], r_type='FIRST').first().end_node

        diagnoses = collections.defaultdict(lambda: {"match": 0, "missing": 0, "total": 0})
        symptoms_on_path = []
        contradictory_symptoms = set(user_symptoms)

        while True:
            join_type = current_node['joinType']
            conditions = list(self.rel_matcher.match(nodes=[current_node], r_type='CONDITION'))

            conditions_met = [condition.end_node['name'] for condition in conditions if condition.end_node['name'] in user_symptoms]
            conditions_missed = [condition.end_node['name'] for condition in conditions if condition.end_node['name'] not in user_symptoms]
            symptoms_on_path += conditions_met + conditions_missed

            contradictory_symptoms -= set(symptoms_on_path)

            if (join_type == 'AND' and len(conditions_met) == len(conditions)) or (join_type == 'OR' and conditions_met):
                next_node = self.rel_matcher.match(nodes=[current_node], r_type='YES').first()
            else:
                next_node = self.rel_matcher.match(nodes=[current_node], r_type='NO').first()

            if next_node is None or 'Diagnosis' in next_node.end_node.labels:
                if next_node is not None:
                    diagnoses[next_node.end_node['name']]["match"] += len([symptom for symptom in symptoms_on_path if symptom in user_symptoms])
                    diagnoses[next_node.end_node['name']]["missing"] += len([symptom for symptom in symptoms_on_path if symptom not in user_symptoms])
                    diagnoses[next_node.end_node['name']]["total"] += len(symptoms_on_path)
                break
            else:
                current_node = next_node.end_node

        results = {}
        for diagnosis, values in diagnoses.items():
            total = values["total"]
            if total > 0:
                results[diagnosis] = (values["match"] / total) * 100
            else:
                results[diagnosis] = 0

        if contradictory_symptoms:
            max_reduction = 0.1
            reduction_per_symptom = max_reduction / len(contradictory_symptoms)
            for diagnosis in results:
                reduction_factor = 1.0
                for symptom in contradictory_symptoms:
                    reduction_factor -= reduction_per_symptom
                results[diagnosis] *= reduction_factor

        missing_symptoms = set(symptoms_on_path) - set(user_symptoms)

        return results, contradictory_symptoms, missing_symptoms