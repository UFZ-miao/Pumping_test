# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 11:35:01 2015

@author: miao
"""
import os
import sys
import shutil

class Mesh_Inf:
	"""
	Class for preprocessing of radial meshes.
	"""
	def __init__(self, msh_dir_path, msh_file_name, well_radius, bound_radius, absolute_depth=0,layer_number=0):
		'''
		Input
		----------
		msh_dir_path(string):  			-- full path of msh file dir 
		
		msh_file_name(string)			-- name of mesh file
		
		well_radius(float)			--radius of well
	 
		bound_radius(float)			--radius of boundary
		
		Optional Input
		----------
		absolute_depth(float)		--absolute depth of model(positive)
	 
		layer_number(int)			--the number of layers(in case of 2D equals to 0)
		'''
		self.msh_dir_path, self.msh_file_name, self.well_radius, self.bound_radius\
          = msh_dir_path, msh_file_name, well_radius, bound_radius
		self.absolute_depth,self.layer_number = absolute_depth, layer_number
		
	def __call__(self):
		'''
		Return the number of segments, the x coordinates of points at x axis(list), the information of well points and the information of boundary points.
		
		Output
		----------
		radial_node_dis(lis --x coordinates of points located at x axis (list).
	 
		well_infs(dictionary)		--dictionary of information(index,coordinates) of well points 
	 
		BC_infs(dictionary)		--dictionary of information(index,coordinates) of BC points
		
		'''
		
		file_msh = os.path.join( self.msh_dir_path, self.msh_file_name)
		infile=open(file_msh,'r')
		#node_coos=[]
		indexs={}
		radial_node_dis=[] #list of x coordinates of nodes in x axis in the ascending order
		for i, line in enumerate(infile):
			if i==4:
				nod_num=int(line)
			elif i>4:
				break
		infile.close()
				
		infile=open(file_msh,'r')
		for i, line in enumerate(infile):

			if (i>4)and(i<=nod_num+4):
				coos=line.split()
				index=int(coos[0])
				coo_x=float(coos[1])
				coo_y=float(coos[2])
				coo_z=float(coos[3])
				if (not coo_y) and (not coo_z) and (coo_x>0):#extract those points located at x axis
					
					radial_node_dis.append(coo_x)
					indexs[coo_x]=index
			elif i>(nod_num+6):
				break
		infile.close()
		radial_node_dis=sorted(radial_node_dis) #sort the numbers in the ascending number
		num_inds=[]
		for coo_x in radial_node_dis:
			num_ind=indexs[coo_x]
			num_inds.append(num_ind)
		
		#welltype=('Well type:vector' if radial_node_dis[0] else 'well type:point')
		#print nod_num,ele_num,radial_node_dis
		infile=open(file_msh,'r')
		well_infs={}
		BC_infs={}
		for layer in range(self.layer_number+1):
			well_infs[layer]=[]
			BC_infs[layer]=[]
		for i, line in enumerate(infile):
			if (i>4)and(i<=nod_num+4):
				coos=line.split()
				index=int(coos[0])
				coo_x=float(coos[1])
				coo_y=float(coos[2])
				coo_z=float(coos[3])
				for layer in range(self.layer_number+1):
					try:
						layer_depth=-layer*(self.absolute_depth/self.layer_number)
					except: # 2D case
						layer_depth=0
					if (abs((coo_x*coo_x+coo_y*coo_y)-self.well_radius*self.well_radius)<1e-5) and (abs(coo_z-layer_depth)<1e-5):
						well_inf=[index,coo_x,coo_y,coo_z]
						well_infs[layer].append(well_inf)
					elif (abs((coo_x*coo_x+coo_y*coo_y)-self.bound_radius*self.bound_radius)<1e-1) and (abs(coo_z-layer_depth)<1e-5):
						BC_inf=[index,coo_x,coo_y,coo_z]
						BC_infs[layer].append(BC_inf)
		seg_num=len(well_infs[0])				
		infile.close()
		
		return seg_num,radial_node_dis, well_infs, BC_infs


class Input_File_Generator(Mesh_Inf):

	"""
	Generate all input files according to specific radial mesh.
	"""
	
	def __init__(self, msh_dir_path, msh_file_name, task_dir_path, task_ID, well_radius, bound_radius,
				absolute_pumping_rate, absolute_depth=0,layer_number=0, permeability=None):
		'''
		Input
		----------
		msh_dir_path(string):  			-- full path of msh file dir 
		
		msh_file_name(string)			-- name of mesh file
		
		task_dir_path(string):  		--path of dir of this task
		
		task_ID(string)				--name of task
		
		well_radius(float)			--radius of well
	 
		bound_radius(float)			--radius of boundary
		
		Optional Input
		----------
		absolute_depth(float)		--absolute depth of model(positive)
	 
		layer_number(int)			--the number of layers(in case of 2D equals to 0)
		
		permeability(float)			--the mean of permeability
		'''
		#self.file_msh, self.well_radius, self.bound_radius = file_msh, well_radius, bound_radius
		#self.absolute_depth,self.layer_number = absolute_depth, layer_number
		Mesh_Inf.__init__(self, msh_dir_path, msh_file_name, well_radius, bound_radius, absolute_depth,layer_number)
		self.task_dir_path, self.task_ID, self.absolute_pumping_rate, self.permeability = task_dir_path, task_ID, absolute_pumping_rate, permeability
		
	def msh_copy(self):
		'''
		move msh file from original dir to target dir.
		'''
		src_file= os.path.join(self.msh_dir_path, self.msh_file_name)
		#os.chmod(src_file, 755)
		dst_dir = self.task_dir_path
		if not os.path.exists(dst_dir):
			os.makedirs(dst_dir)
		shutil.copy2 (src_file, dst_dir)
		dst_file = os.path.join(dst_dir, self.msh_file_name)
		new_dst_file_name=os.path.join(dst_dir, self.task_ID + '.msh')
		if not os.path.isfile(new_dst_file_name):
			os.rename(dst_file, new_dst_file_name)
		print('MSH-file copied to dictionary: ' + dst_dir)  
		
	def gli_generator(self):
	
		'''
		Generate a .gli file according to .msh file of radial mesh. Applicable to both 2D and 3D meshes.
		
		'''
		#from pre_processing import Mesh_inf
		seg_num,radial_node_dis, well_infs_ori, BC_infs_ori= Mesh_Inf.__call__(self)
		point_index=0
		well_infs={}
		BC_infs={}
		for layer in range(self.layer_number+1):
			well_inf_layer=well_infs_ori[layer]
			BC_inf_layer=BC_infs_ori[layer]
			well_infs[layer]=[]
			BC_infs[layer]=[]
			for well_inf_ori in well_inf_layer:
				well_inf=[point_index,well_inf_ori[1],well_inf_ori[2],well_inf_ori[3]]
				point_index+=1
				well_infs[layer].append(well_inf)
			for BC_inf_ori in BC_inf_layer:
				BC_inf=[point_index,BC_inf_ori[1],BC_inf_ori[2],BC_inf_ori[3]]
				point_index+=1
				BC_infs[layer].append(BC_inf)
		
		file_gli=os.path.join(self.task_dir_path, self.task_ID+'.gli')
		with open(file_gli,'w') as outfile:
			outfile.write('#POINTS\n')
			for layer in range(self.layer_number+1):
				well_inf_layer=well_infs[layer]
				BC_inf_layer=BC_infs[layer]
				for well_inf in well_inf_layer:
					outfile.write(str(well_inf[0])+'  '+str(well_inf[1])+'  '+str(well_inf[2])+'  '+str(well_inf[3])+'\n') 
				for BC_inf in BC_inf_layer:
					outfile.write(str(BC_inf[0])+'  '+str(BC_inf[1])+'  '+str(BC_inf[2])+'  '+str(BC_inf[3])+'\n')
			for layer in range(self.layer_number+1):
				well_inf_layer=well_infs[layer]
				BC_inf_layer=BC_infs[layer]
				outfile.write('#POLYLINE\n$NAME\nWELL_%d\n$EPSILON\n0.0001\n$POINTS\n'%layer)
				for well_inf in well_inf_layer:
					outfile.write(str(well_inf[0])+'\n')
				outfile.write(str(well_inf_layer[0][0])+'\n') #write the index of first point to make polyline closed
				outfile.write('#POLYLINE\n$NAME\nBC_%d\n$EPSILON\n0.0001\n$POINTS\n'%layer)
				for BC_inf in BC_inf_layer:
					outfile.write(str(BC_inf[0])+'\n')
				outfile.write(str(BC_inf_layer[0][0])+'\n') #write the index of first point to make polyline closed
			outfile.write('#STOP')
		print('GLI-file generated according to given MSH-file: ' + file_gli)  

	def bc_generator(self):
		'''
		Generate .bc file according to the layer number and pumping rate.
		'''
		file_bc=os.path.join(self.task_dir_path, self.task_ID+'.bc')
		
		with open(file_bc,'w') as outfile1:
			for layer in range(self.layer_number+1):
				outfile1.write('#BOUNDARY_CONDITION\n$PCS_TYPE\nGROUNDWATER_FLOW\n$PRIMARY_VARIABLE\nHEAD\n$GEO_TYPE\n')
				outfile1.write('POLYLINE  BC_%d \n$DIS_TYPE\nCONSTANT  0.0\n'%layer)
			outfile1.write('#STOP')
		print('BC-file generated according to given MSH-file: ' + file_bc)  
			
	def radial_st_generator(self):
		'''
		Generate .st file according to the layer number and pumping rate.
		'''
		file_st=os.path.join(self.task_dir_path, self.task_ID+'.st')
		seg_num,radial_node_dis, well_infs_ori, BC_infs_ori= Mesh_Inf.__call__(self)
		pr_layer=-self.absolute_pumping_rate/seg_num
		pr_top_bottom=pr_layer*0.5
		
		with open(file_st,'w') as outfile2:
			outfile2.write('#SOURCE_TERM\n$PCS_TYPE\nGROUNDWATER_FLOW\n$PRIMARY_VARIABLE\nHEAD\n')
			outfile2.write('$GEO_TYPE\nPOLYLINE  WELL_0\n$DIS_TYPE\nCONSTANT  %e\n'%(pr_top_bottom))
			for layer in range(1,self.layer_number):
				outfile2.write('#SOURCE_TERM\n$PCS_TYPE\nGROUNDWATER_FLOW\n$PRIMARY_VARIABLE\nHEAD\n')
				outfile2.write('$GEO_TYPE\nPOLYLINE  WELL_%d\n$DIS_TYPE\nCONSTANT  %e\n'%(layer,pr_layer))
			outfile2.write('#SOURCE_TERM\n$PCS_TYPE\nGROUNDWATER_FLOW\n$PRIMARY_VARIABLE\nHEAD\n')
			outfile2.write('$GEO_TYPE\nPOLYLINE  WELL_%d\n$DIS_TYPE\nCONSTANT  %e\n'%(self.layer_number,pr_top_bottom))
			outfile2.write('#STOP')	
		print('ST-file generated according to given MSH-file: ' + file_st)  
		
	def mmp_generator(self, Kfield_type):
		'''
		Input
		----------
		Kfield_type(int)    --with the value 1 of Homogeneous and 2 heterogeneous.
		'''
		
		Dim = 3 if self.layer_number else 2
		
		file_mmp=os.path.join(self.task_dir_path, self.task_ID+'.mmp')
	
		with open (file_mmp,'w') as outfile:
			outfile.write('#MEDIUM_PROPERTIES\n'+'$GEOMETRY_DIMENSION\n%d\n'%Dim+'$GEOMETRY_AREA\n1.000000e+001\n')
			outfile.write('$POROSITY\n'+'1  2.e-1'+'$TORTUOSITY\n'+'1  1.\n')
			if Kfield_type==1:
				outfile.write('$PERMEABILITY_TENSOR\nISOTROPIC  %e\n'%self.permeability)
			elif Kfield_type==2:
				outfile.write('$PERMEABILITY_DISTRIBUTION\nlog-normal_Kfield.dat\n')
			outfile.write('#STOP')
	
	def ic_generator(self):
		'''
		Hardcoded function to generate general input files.
		'''
		file_ic = os.path.join(self.task_dir_path,self.task_ID+'.ic')
		with open (file_ic, 'w') as outfile1:
			outfile1.write('#INITIAL_CONDITION\n$PCS_TYPE\nGROUNDWATER_FLOW\n$PRIMARY_VARIABLE\n'
			+'HEAD\n$GEO_TYPE\nDOMAIN\n$DIS_TYPE\nCONSTANT  0.0\n#STOP')
		print('IC-file generated according to given MSH-file: ' + file_ic)  
	
	def mfp_generator(self):
		'''
		Hardcoded function to generate general input files.
		'''
		file_mfp= os.path.join(self.task_dir_path,self.task_ID+'.mfp')
		with open (file_mfp, 'w') as outfile2:
			outfile2.write('#FLUID_PROPERTIES\n$FLUID_TYPE\nLIQUID\n$PCS_TYPE\nHEAD\n$DENSITY\n'+
				'1  1.000000e+003\n$VISCOSITY\n1 1.000000e-003\n#STOP')
		print('MFP-file generated according to given MSH-file: ' + file_mfp)  
		
	def num_generator(self):
		'''
		Hardcoded function to generate general input files.
		'''
		file_num = os.path.join(self.task_dir_path,self.task_ID+'.num')
		with open (file_num, 'w') as outfile3:
			outfile3.write ('#NUMERICS\n$PCS_TYPE\nGROUNDWATER_FLOW\n$LINEAR_SOLVER\n'
				+'; method error_tolerance max_iterations theta precond storage\n'
				+'2        5 1.0e-06       1000           1.0   1       4\n'
				+'$ELE_GAUSS_POINTS\n3\n#STOP')
		print('NUM-file generated according to given MSH-file: ' + file_num)
		
	def out_generator(self):
		'''
		Hardcoded function to generate general input files.
		'''
		file_out = os.path.join(self.task_dir_path,self.task_ID + '.out')
		with open (file_out, 'w') as outfile4:
			outfile4.write ('#OUTPUT\n$NOD_VALUES\nHEAD\n$GEO_TYPE\nDOMAIN\n$DAT_TYPE\nVTK\n'+
				'$TIM_TYPE\nSTEPS 1\n#STOP')
		print('OUT-file generated according to given MSH-file: ' + file_out)  
		
	def pcs_generator(self):
		'''
		Hardcoded function to generate general input files.
		'''
		file_pcs = os.path.join(self.task_dir_path,self.task_ID + '.pcs')
		with open (file_pcs,'w') as outfile5:
			outfile5.write('#PROCESS\n$PCS_TYPE\nGROUNDWATER_FLOW\n$NUM_TYPE\nNEW\n#STOP')
		print('PCS-file generated according to given MSH-file: ' + file_pcs)  
		
	def tim_generator(self):	
		'''
		Hardcoded function to generate general input files.
		'''
		file_tim = os.path.join(self.task_dir_path,self.task_ID + '.tim')
		with open (file_tim,'w') as outfile6:
			outfile6.write('#TIME_STEPPING\n$PCS_TYPE\nGROUNDWATER_FLOW\n$TIME_START\n'
				+'0.0\n$TIME_END\n10000\n$TIME_STEPS\n1  10000#STOP')
		print('TIM-file generated according to given MSH-file: ' + file_tim)  
		
	def element_center_information(self):	  
		'''
		This is a Python file to create a nested list containing index and coordinates (x,y,z) of element centers, and
		save it as a .txt file.
						
		Output
		----------
		inf_centers(lists)			--a nested list containing information(index,x,y,z) of element centers
		
		'''
		
		node_num_per_ele=8 if self.layer_number else 4 # recognize the dimension of problem
		
		file_msh = os.path.join(self.msh_dir_path, self.msh_file_name)
		infile=open(file_msh, 'r')
			
		ele_indexs=[]	 # number of elements
		ele_nodes={} # corresponding node number of each node of elements(length: element numbe)
		for index in range(node_num_per_ele):
			ele_nodes[index]=[]
			node_index_number={} #dictionary with each component of a list of nodes' indexs 
			
		for line in infile:
			if 'ELEMENTS' in line:
				next(infile) #skip the next line	 
						   
				for line in infile:
					if 'STOP' in line:
						break
					else:			
						words=line.split()
						elelist=int(words[0])
						ele_indexs.append(elelist)
						for index in range(node_num_per_ele):
							node_index_number[index]=int(words[index+3])
							ele_nodes[index].append(node_index_number[index])
		infile.close()
		 
		infile=open(file_msh,'r')
		lines=infile.readlines() # load all lines into a list of strings
		node_num=int(lines[4]) # extract the number of node amounts from line4
		node_infs=lines[5:5+node_num] #load all node number and coordinate into a list
		
		coo_x_nodes={}
		coo_y_nodes={}
		coo_z_nodes={}
		inf_centers=[]
		
		for index in range(node_num_per_ele):
			coo_x_nodes[index]=[]
			coo_y_nodes[index]=[]
			coo_z_nodes[index]=[]
			for ele_node in ele_nodes[index]:
				node_inf=node_infs[ele_node]
				words=node_inf.split()
				coo_x_node=float(words[1])
				coo_y_node=float(words[2])
				coo_z_node=float(words[3])
				coo_x_nodes[index].append(coo_x_node)
				coo_y_nodes[index].append(coo_y_node)
				coo_z_nodes[index].append(coo_z_node)
				
		for ele_index in ele_indexs:
			coo_x_sum=coo_y_sum=coo_z_sum=0
			for index in range(node_num_per_ele):
				coo_x_sum+=coo_x_nodes[index][ele_index]
				coo_y_sum+=coo_y_nodes[index][ele_index]
				coo_z_sum+=coo_z_nodes[index][ele_index]
			coo_x_center=coo_x_sum/node_num_per_ele
			coo_y_center=coo_y_sum/node_num_per_ele
			coo_z_center=coo_z_sum/node_num_per_ele
			inf_center=[ele_index,coo_x_center,coo_y_center,coo_z_center]	
			inf_centers.append(inf_center)
			#CenterKO_lists.append(CenterKO_list)
		
		outfile_path=os.path.join(self.task_dir_path, self.task_ID+'_CenterKO.dat')
		with open(outfile_path,'w') as outfile:
			for row in inf_centers:
				outfile.write('%d  ' %row[0])
				outfile.write('%18.8f ' %row[1])
				outfile.write('%18.8f' %row[2])
				outfile.write('%18.8f' %row[3])
				#for column in row:
					#outfile.write('%14.8f' %column)
				outfile.write('\n')
		print('Center coordinates of elements saved to : ' + outfile_path)  
		return inf_centers
