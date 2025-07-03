# Runtime hook para NumPy
import os
import sys

# Configurar variables de entorno antes de importar NumPy
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

# Evitar conflictos de CPU dispatcher
try:
    import numpy as np
    # Forzar inicialización limpia
    np._NoValue
except:
    pass
