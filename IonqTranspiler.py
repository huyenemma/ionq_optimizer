from qiskit.transpiler.basepasses import TransformationPass
from qiskit.dagcircuit import DAGCircuit
from qiskit.transpiler import PassManager


class GPI2Cancellation(TransformationPass):
    def run(self, dag: DAGCircuit) -> DAGCircuit:
        nodes_to_remove = []

        # Traverse all nodes in the DAG
        for node in dag.topological_op_nodes():
            if node.name == 'gpi2':
                successors = list(dag.successors(node))  # Convert the iterator to a list
                for next_node in successors:
                    if next_node.name == 'gpi2':
                        # Check if they cancel each other out
                        phi1 = node.op.params[0]
                        phi2 = next_node.op.params[0]
                        if (phi1 + 0.5) % 1 == phi2 % 1 or (phi2 + 0.5) % 1 == phi1 % 1:
                            # Mark both nodes for removal
                            nodes_to_remove.extend([node, next_node])

        # Remove the marked nodes
        for node in nodes_to_remove:
            dag.remove_op_node(node)
        
        return dag



def custom_pass_manager():
    pm = PassManager()
    pm.append(GPI2Cancellation())
    return pm