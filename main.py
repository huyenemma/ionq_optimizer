import os
from qiskit import QuantumCircuit, transpile
from qiskit_ionq import IonQProvider
import IonqTranspiler as transpiler


# Initialize the IonQ provider and backend
api_key = os.getenv("IONQ_API_KEY") # Get the API key from the environment
provider = IonQProvider(token=api_key)
backend = provider.get_backend("simulator", gateset="native")


qc = QuantumCircuit(2, name="2cnots")
qc.cx(0, 1)
qc.cx(0, 1)
ibm_transpiled = transpile(qc, backend=backend, optimization_level=3) 


pm = transpiler.custom_pass_manager()


pm.run(ibm_transpiled)
pm.draw(output = 'mpl')