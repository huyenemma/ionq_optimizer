from qiskit import transpile
from qiskit.transpiler import PassManager
from qiskit.converters import dag_to_circuit, circuit_to_dag
from rewrite_rules import GPI2_Adjoint, GPI_Adjoint, CommuteGPI2MS

class IonQ_Transpiler:
    def __init__(self, backend):
        self.backend = backend
        self.pass_manager = self.custom_pass_manager()

    @staticmethod
    def custom_pass_manager():
        pm = PassManager()
        pm.append([
            GPI2_Adjoint(), 
            GPI_Adjoint(), 
            CommuteGPI2MS()
        ])
        return pm

    def transpile(self, qc):
        # Transpile with IBM transpiler first
        ibm_transpiled = transpile(qc, backend=self.backend, optimization_level=3)
        
        # Apply custom optimization passes
        optimized_dag = self.pass_manager.run(circuit_to_dag(ibm_transpiled))
        
        # Convert the optimized DAG back to a QuantumCircuit
        optimized_circuit = dag_to_circuit(optimized_dag)
        
        return optimized_circuit