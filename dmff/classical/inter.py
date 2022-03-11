import sys
sys.path.append('/share/home/jichen/work/DMFF')
import jax.numpy as jnp
from dmff.admp.spatial import v_pbc_shift
import numpy as np
import jax.numpy as jnp
from jax import grad

class LennardJonesForce:
    
    def __init__(self, isShift, isSwitch, r_switch, r_cut) -> None:
        
        self.isShift = isShift
        self.isSwitch = isSwitch
        self.r_switch = r_switch
        self.r_cut = r_cut
        
    def generate_get_energy(self):
        
        def get_energy(positions, box, pairs, epsilon, sigma):
            
            dr_vec = positions[pairs[:, 0]] - positions[pairs[:, 1]]
            dr_vec = v_pbc_shift(dr_vec, box, jnp.linalg.inv(box))
            dr_norm = jnp.linalg.norm(dr_vec, axis=1)
            dr_norm = dr_norm[dr_norm<=self.r_cut]
            
            dr_inv = 1.0/dr_norm
            sig_dr = sigma * dr_inv
            sig_dr12 = jnp.power(sig_dr, 12)
            sig_dr6 = jnp.power(sig_dr, 6)
            E = 4 * epsilon * (sig_dr12 - sig_dr6)
            
            shiftedE = 0
            
            if self.isShift:
                
                rcut_inv = 1.0/self.r_cut
                sig_rcut = sigma * rcut_inv
                sig_rcut12 = jnp.power(sig_rcut, 12)
                sig_rcut6 = jnp.power(sig_rcut, 6)
                shiftedE = 4*epsilon*(sig_rcut12 - sig_rcut6)
            
            if self.isSwitch:
                
                x = (dr_norm - self.r_switch) / (self.r_cut - self.r_switch)
                S = 1 - 6*x**5 + 15*x**4 - 10*x**3
                jnp.where(dr_norm>self.r_switch, E, E*S)
            
            return jnp.sum(E) + shiftedE
        
        return get_energy
    
class CoulombForce:
    pass

if __name__ == '__main__':
    
    lj = LennardJonesForce(False, False, r_switch=0, r_cut=3)
    
    positions = jnp.array([[0, 0, 0], [1, 0, 0]], dtype=float)
    
    box = jnp.array([[10, 0, 0], [0, 10, 0], [0, 0, 10]])
    
    pairs = np.array([[0, 1]])
    
    epsilon = jnp.array([1])
    sigma = jnp.array([0.1])
    
    get_energy = lj.generate_get_energy()
    
    E = get_energy(positions, box, pairs, epsilon, sigma)
    print(E)
    F = grad(get_energy)(positions, box, pairs, epsilon, sigma)
    print(F)