# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 11:35:01 2015

@author: miao
"""

import os
import sys

if (os.name == 'posix'):
    sys.path.append( os.environ['HOME'] + '/Python_scripts/geostat/' )
elif (os.name == 'nt'):
    #sys.path.append('C:\Users\miao\Documents\Python_Scripts\Pumping_Test')
	sys.path.append('C:\Users\miao\Documents\SVN-miao\ogspy')
#sys.path.append('\pre_post_processing')

import preprocessing as prepro

#-------------------------determin the parameters-----------------------------#
'''
msh_dir_path(string):  		-- directory path of msh file
msh_file_name(string)		-- full name of mesh file (with extension)
task_dir_path(string):  	-- directory path of this task
task_ID(string)				-- name of task
well_radius(float)			-- radius of well
bound_radius(float)			-- radius of boundary
absolute_depth(float)		-- absolute depth of model(positive)
layer_number(int)			-- the number of layers(in case of 2D equals to 0)
absolute_depth(float)		-- absolute depth of model(positive)
layer_number(int)			-- the number of layers(in case of 2D equals to 0)
permeability(float)			-- the mean of permeability
Kfield_type(int)			-- 1 corresponds to homogeneous Kfield and 2 heterogeneous Kfield
sigma_2(float)				-- variance
len_scale(float)			-- correlation length
'''

msh_dir_path = "C:\Users\miao\Documents\Pumping_Test\Mesh\Radial_Mesh"
msh_file_name = "Mesh_Radial_R128_S64_L5.msh"
task_dir_path = "C:\Users\miao\Documents\Pumping_Test\Simulation\Test\MiaoJing"
task_ID = "Ens1_G3_M4_L5"
well_radius = 0.01
bound_radius = 128
absolute_depth = 5
layer_number = 5
absolute_pumping_rate=1.e-4
permeability = 1.e-4

Kfield_type = 2  #1 corresponds to homogeneous Kfield and 2 heterogeneous Kfield
sigma_2 = 1.
len_scale = [64, 64, 64]


#-------------------------generate input files--------------------------------#
Test1 = prepro.Input_File_Generator(msh_dir_path, msh_file_name, task_dir_path, task_ID, well_radius, bound_radius,
						absolute_pumping_rate, absolute_depth, layer_number, permeability)

Test1.msh_copy()
Test1.gli_generator()
Test1.bc_generator()
Test1.mmp_generator(Kfield_type)
Test1.ic_generator()
Test1.mfp_generator()
Test1.num_generator()
Test1.out_generator()
Test1.pcs_generator()
Test1.tim_generator()

if Kfield_type==2:
	Test1.element_center_information()
	if (os.name == 'posix'):
		sys.path.append( os.environ['HOME'] + '/Python_scripts/geostat/' )
	elif (os.name == 'nt'):
		sys.path.append('C:\Users\miao\Documents\Python_Scripts\Pumping_Test\geostat')
	sys.path.append('\geospy')

	from geospy import *
	## configure mad and exporting data -------------------------------------------
	#
	SRFConfig = {
		'dim': 3 if absolute_depth else 2,
		'cov_model' : 'Gau',
		'mu' : np.log(permeability),
		'sigma_2' : sigma_2,
		'len_scale' : len_scale,
		'transformation' : 'Ln',
		'generator' : {'method': 'rand', 'mode_no': 2**10}
	}
	DomainConfig = {
		'dom_type' : 'structured',
		'origin': [0, 0, 0],
		'shape': [100, 50, 1],
		'resolution': [1, 1, 1]
	}
	
	x_pos = np.random.uniform(0, 100, 1000)
	y_pos = np.random.uniform(-10, 10, 1000)
	
	###############################################################################
	## Main part
	###############################################################################

	file_CenterKO = os.path.join( task_dir_path, task_ID + "_CenterKO.dat")
	file_Krandom = os.path.join( task_dir_path, "log-normal_Kfield.dat" )
	#file_seeds=dir_home+'\Kfields\Ens1_G3_M4_L5_seeds\Ens1_G3_M4_L5_Seends{}'.format(10,10)
	
	Kfield_range=range(1)                          # Number of Kfields to generate	
	srf = SRF( **SRFConfig )
	srf.read_domain(file_CenterKO)
	
	for KN in Kfield_range:
		srf.gen_srf()
		srf.write_srf(file_Krandom.format(KN), flag='OGS')