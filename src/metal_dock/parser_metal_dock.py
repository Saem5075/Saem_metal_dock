import sys, os
import re
import configparser

             #         e_NA, e_OA, e_SA,  e_HD,
standard_set = {'V' : [ 4.696,	6.825,	5.658,	3.984],
                'CR': [ 6.371,	1.998,	0.144,	3.625],
                'CO': [ 5.280,	0.050,	6.673,	5.929],
                'NI': [ 0.630,	2.732,	4.462,	2.820],
                'CU': [ 4.696,	1.277,	6.791,	1.114],
                'MO': [ 1.330,	0.014,	0.168,	5.620],
                'RU': [ 6.936,	2.796,	4.295,	6.357],
                'RH': [ 5.559,	2.056,	0.573,	5.471],
                'PD': [ 4.688,	0.845,	5.574,	3.159],
                'RE': [ 6.738,	0.645,	3.309,	4.502],
                'OS': [ 5.958,	0.135,	4.102,	6.589],
                'PT': [ 6.532,	2.020,	6.332,	1.844],
            }

config = configparser.ConfigParser(interpolation=None)
config['DEFAULT']       =   { "method"                  :              'dock',
                              "metal_symbol"            :                'Ru',
                              "parameter_file"          :    'metal_dock.dat',
                              "ncpu"                    :                 '1'}

config['PROTEIN']       =   { "pdb_file"                :       'protein.pdb',
                              "pH"                      :               '7.4',
                              "clean_pdb"               :              'True'}

config['METAL_COMPLEX'] =   { "geom_opt"                :              'True',
                              "xyz_file"                : 'metal_complex.xyz',
                              "charge"                  :                 '0',
                              "spin"                    :                 '0',
                              "vacant_site"             :              'True',}

config['QM']            =   { "engine"                  :                'ADF',

                              # ADF & Gaussian input keywords
                              "basis_set"               :                'TZP',
                              "functional_type"         :                'GGA',
                              "functional"              :                'PBE',
                              "dispersion"              :    'GRIMME3 -BJDAMP',
                              "solvent"                 :              'Water',

                              # ORCA input keywords
                              "orcasimpleinput"         : 'PBE def2-TZVP CPCMC(Water)',
                              "orcablocks"              :                  ''}

config['DOCKING']       =   { "ini_parameters"          :              'False',
                              "rmsd"                    :              'False',
                              "dock_x"                  :                '0.0',
                              "dock_y"                  :               ' 0.0',
                              "dock_z"                  :               ' 0.0',
                              "box_size"                :                 '20',
                              "scale_factor"            :                   '',
                              "random_pos"              :               'True',
                              "num_poses"               :                 '10',
                              "e_NA"                    :                '5.0',
                              "e_OA"                    :                '5.0',
                              "e_SA"                    :                '5.0',
                              "e_HD"                    :                '5.0',
                              "ga_dock"                 :              'True',
                              "ga_dock_pop_size"        :                '150',
                              "ga_dock_num_evals"       :            '2500000',
                              "ga_dock_num_generations" :              '27000',
                              "ga_dock_elitism"         :                  '1',
                              "ga_dock_mutation_rate"   :               '0.02',
                              "ga_dock_crossover_rate"  :               '0.80',
                              "ga_dock_window_size"     :                 '10',
                              "sa_dock"                 :              'False',
                              "temp_reduction_factor"   :               '0.90',
                              "number_of_runs"          :                 '50',
                              "max_cycles"              :                 '50'}

config['MC']            =   { "mc_steps"                 :               '250'}


class Parser:
  
  def __init__(self, input_file):
    config.read(input_file)

    # Convert to correct datatype if necessary
    # [DEFAULT] #
    self.method                   = config['DEFAULT']['method']
    self.metal_symbol             = config['DEFAULT']['metal_symbol']

    self.parameter_file           = config['DEFAULT']['parameter_file']
    self.ncpu                     = int(config['DEFAULT']['ncpu'])

    self.atom_types_included()

    # [PROTEIN] # 
    self.pdb_file                 = config['PROTEIN']['pdb_file']
    self.name_protein             = config['PROTEIN']['pdb_file'].split('/')[-1][:-4]
    self.pH                       = float(config['PROTEIN']['pH'])
    self.clean_pdb                = config['PROTEIN'].getboolean('clean_pdb')

    # [METAL_COMPLEX] #
    self.geom_opt                 = config['METAL_COMPLEX'].getboolean('geom_opt')
    self.xyz_file                 = config['METAL_COMPLEX']['xyz_file']
    self.name_ligand              = config['METAL_COMPLEX']['xyz_file'].split('/')[-1][:-4]
    self.charge                   = int(config['METAL_COMPLEX']['charge'])
    self.spin                     = float(config['METAL_COMPLEX']['spin'])
    self.vacant_site              = config['METAL_COMPLEX'].getboolean('vacant_site')

    # [QM] # 
    self.engine                   = str(config['QM']['engine'])
    self.basis_set                = config['QM']['basis_set']
    self.functional_type          = config['QM']['functional_type']
    self.functional               = config['QM']['functional']
    self.dispersion               = config['QM']['dispersion']
    self.solvent                  = config['QM']['solvent']
    self.orcasimpleinput          = config['QM']['orcasimpleinput']
    self.orcablocks               = config['QM']['orcablocks']

    if self.engine == 'ORCA' and self.orcasimpleinput == '':
      print('ORCA engine selected but no ORCA input found')
      print('Please insert QM specifications with the orcasimpleinput & orcablocks keywords in the .ini file')
      sys.exit()

    # [DOCKING] #
    self.ini_parameters           = config['DOCKING'].getboolean('ini_parameters')
    if self.metal_symbol.upper() == 'FE' or self.metal_symbol.upper() == 'ZN' or self.metal_symbol.upper() == 'MN':
      self.internal_param = True
    else:
      self.internal_param = False
      if self.ini_parameters == True:
        self.parameter_set          = [self.e_NA, self.e_OA, self.e_SA, self.e_HD]
      else:
        self.parameter_set          = standard_set.get(self.metal_symbol.upper())

    self.rmsd                     = config['DOCKING'].getboolean('rmsd')
    self.dock_x                   = float(config['DOCKING']['dock_x'])
    self.dock_y                   = float(config['DOCKING']['dock_y'])
    self.dock_z                   = float(config['DOCKING']['dock_z'])
    
    try: 
      self.box_size               = int(config['DOCKING']['box_size'])
    except ValueError:
      self.box_size               = 0 
    
    try:
      self.scale_factor           = float(config['DOCKING']['scale_factor'])
    except ValueError:
      self.scale_factor           = 0 

    self.random_pos               = config['DOCKING'].getboolean('random_pos')
    self.num_poses                = int(config['DOCKING']['num_poses'])
    self.e_NA                     = float(config['DOCKING']['e_NA'])
    self.e_OA                     = float(config['DOCKING']['e_OA'])
    self.e_SA                     = float(config['DOCKING']['e_SA'])
    self.e_HD                     = float(config['DOCKING']['e_HD'])

    self.ga_dock                  = config['DOCKING'].getboolean('ga_dock')
    self.ga_dock_pop_size         = int(config['DOCKING']['ga_dock_pop_size'])
    self.ga_dock_num_evals        = int(config['DOCKING']['ga_dock_num_evals'])   
    self.ga_dock_num_generations  = int(config['DOCKING']['ga_dock_num_generations'])
    self.ga_dock_elitism          = int(config['DOCKING']['ga_dock_elitism'])
    self.ga_dock_mutation_rate    = float(config['DOCKING']['ga_dock_mutation_rate'])
    self.ga_dock_crossover_rate   = float(config['DOCKING']['ga_dock_crossover_rate'])
    self.ga_dock_window_size      = int(config['DOCKING']['ga_dock_window_size'])

    self.sa_dock                  = config['DOCKING'].getboolean('sa_dock')
    self.temp_reduction_factor    = float(config['DOCKING']['temp_reduction_factor'])
    self.number_of_runs           = int(config['DOCKING']['number_of_runs'])
    self.max_cycles               = int(config['DOCKING']['max_cycles'])

    # [MC] #
    self.mc_steps                 = int(config['MC']['mc_steps'])

    if self.ga_dock == True and self.sa_dock == True:
        print('Only one docking algorithm can be chosen, set either ga_dock or sa_dock to False')
        sys.exit()
    
    if self.ga_dock == True:
      self.dock_algorithm         = [self.ga_dock_pop_size, self.ga_dock_num_evals, self.ga_dock_num_generations, self.ga_dock_elitism, self.ga_dock_mutation_rate, self.ga_dock_crossover_rate, self.ga_dock_window_size]

    if self.sa_dock == True:
      self.dock_algorithm        = [self.temp_reduction_factor, self.number_of_runs, self.max_cycles]

    if self.ga_dock == False and self.sa_dock == False:
        print('At least ga_dock or sa_dock must be set to True for MetalDock to run properly')
        sys.exit()

  def atom_types_included(self):
    if self.parameter_file == 'metal_dock.dat':
      param_file = os.path.join(os.environ['ROOT_DIR'],'metal_dock.dat')
    else:
      param_file = self.parameter_file

    # Open the text file for reading
    with open(param_file, 'r') as file:
        # Initialize an empty list to store the symbols
        symbols_list = []

        # Iterate through each line in the file
        for line in file:
            # Use regular expressions to find matches and extract symbols
            matches = re.findall(r'atom_par\s+([A-Za-z]+)', line)
            
            # Extend the symbols list with the matches (if any)
            symbols_list.extend(matches)

    # Remove following atom symbols:
    rmv_list = ['H','HD','HS','C','A','N','NA','NS','OA','OS','F','MG','P','SA','S','Cl','CL','CA','MN','FE','ZN','BR','I','Z','G','GA','J','Q','DD']  

    for rmv in rmv_list:
      if rmv in symbols_list:
        symbols_list.remove(rmv)

    # Print the list of symbols
    if self.metal_symbol not in symbols_list and self.parameter_file == 'metal_dock.dat':
      print('The metal symbol you have chosen is currently not supported by MetalDock')
      print('The following atom types are present in the parameter file: ')
      print(' '.join(symbols_list))
      sys.exit()
    elif self.metal_symbol not in symbols_list and self.parameter_file != 'metal_dock.dat':
      print('The metal symbol you have chosen is currently not supported by your selected parameter file')
      print('The following atom types are present in the parameter file: ')
      print(' '.join(symbols_list))
      print('Please choose a different parameter file or add the missing atom types to the parameter file')
      sys.exit()
