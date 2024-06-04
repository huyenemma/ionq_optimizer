from qiskit.transpiler.basepasses import TransformationPass
from qiskit.dagcircuit import DAGCircuit
from qiskit.dagcircuit.dagnode import DAGOpNode

class GPI2_Adjoint(TransformationPass):
    def run(self, dag: DAGCircuit) -> DAGCircuit:
        nodes_to_remove = []

        for node in dag.op_nodes():
            if isinstance(node, DAGOpNode) and node.op.name == 'gpi2':
                print(f"Found gpi2 node: {node}, params: {node.op.params}")
                successors = [succ for succ in dag.quantum_successors(node) if isinstance(succ, DAGOpNode)]
                for next_node in successors:
                    if next_node.op.name == 'gpi2':
                        phi1 = node.op.params[0]
                        phi2 = next_node.op.params[0]
                        if (phi2 + 0.5) % 1 == phi1 % 1 or (phi1 + 0.5) % 1 == phi2 % 1:
                            print(f"Removing gpi2 nodes: {node} and {next_node}")
                            nodes_to_remove.extend([node, next_node])

        for node in nodes_to_remove:
            dag.remove_op_node(node)
        
        return dag

class GPI_Adjoint(TransformationPass):
    def run(self, dag: DAGCircuit) -> DAGCircuit:
        nodes_to_remove = []

        for node in dag.op_nodes():
            if isinstance(node, DAGOpNode) and node.op.name == 'gpi':
                print(f"Found gpi node: {node}, params: {node.op.params}")
                successors = [succ for succ in dag.quantum_successors(node) if isinstance(succ, DAGOpNode)]
                for next_node in successors:
                    if next_node.op.name == 'gpi':
                        phi1 = node.op.params[0]
                        phi2 = next_node.op.params[0]
                        if phi2 == phi1:
                            print(f"Removing gpi nodes: {node} and {next_node}")
                            nodes_to_remove.extend([node, next_node])

        for node in nodes_to_remove:
            dag.remove_op_node(node)
        
        return dag

class CommuteGPI2MS(TransformationPass):
    def run(self, dag: DAGCircuit) -> DAGCircuit:
        for node in dag.op_nodes():
            if node.op.name == 'gpi2' and node.op.params == [0.5]:  # GPI2(pi/2)
                successors = list(dag.successors(node))
                for next_node in successors:
                    if isinstance(next_node, DAGOpNode) and next_node.op.name == 'ms' and next_node.op.params == [0, 0, 0.25]:
                        sub_dag = DAGCircuit()
                        for qreg in dag.qregs.values():
                            sub_dag.add_qreg(qreg)
                        if dag.cregs:
                            for creg in dag.cregs.values():
                                sub_dag.add_creg(creg)
                        sub_dag.apply_operation_back(next_node.op, next_node.qargs)
                        sub_dag.apply_operation_back(node.op, node.qargs)

                        dag.substitute_node_with_dag(node, sub_dag, wires={q: q for q in dag.qubits})
                        dag.remove_op_node(next_node)
                        break
        return dag
