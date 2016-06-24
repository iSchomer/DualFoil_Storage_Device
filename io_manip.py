
# INPUT

def first_leg(title, cu, tt, mc, vcutL, vcutH):    
    newInput = ''
    tracker = False
    modified = False
    with open('/Users/ips/dualfoil/dualfoil5.in', 'r+') as file:
        line = file.readline()
        while line != '':
            #make sure restart is set to false
            if line.find('.true.') != -1:
                line = line.replace('.true.', '.false.')

            #find line before the one we need; set tracker 
            if line.find('lcurs') != -1 and modified == False:
                tmp = line.lstrip().split()
                #also make sure lcurs is 1
                if int(tmp[0]) != 1:
                    line = line.replace(str(tmp[0]), '1', 1)
                newInput += line
                tracker = True
                #read past all steps left from previous simulations
                while line != '\n':
                    line = file.readline()
                            
            if (tracker == True):
                #replace whatever the current cmd line is with the given leg
                line = str(cu) + ' ' + str(tt) + ' ' + str(mc) + ' ' + str(vcutL) + ' ' + str(vcutH) + ' !' + title + '\n\n'
                tracker = False 
                modified = True    
                
            #keep up the new file and read next line
            newInput += line  
            line = file.readline()

    with open('/Users/ips/dualfoil/dualfoil5.in', 'w') as file:
        file.write(newInput)

def add_new_leg(title, cu, tt, mc, vcutL, vcutH):

    """
    Appends a new leg to dualfoil's input file, adjusting the restart parameter if needed.
    Also edits previous leg as needed to avoid data errors.
    
    Parameters
    ----------
    title : str
        comment that describes the function of the new leg
    cu : float
        defines cu(i) for the input
        if mc = 1 or 2, cu is the current
        if mc = 0, cu is the potential
    tt : float
        defines tt(i) for the input
        if mc = 0 or 1, tt is the new leg's duration (min)
        if mc = 2, tt is the cuttof potential (V)
    mc : float
        defines mc(i) for the input, which controls mode of operation
        possible values for dualfoil 5.2 are 0, 1, and 2
    vcutL : float
        Low Voltage cutoff point
    vcutH : float
        High Voltage cutoff point
    """
    
    newInput = ''
    newLeg = ''
    tracker = False
    modified = False
    firstRst = False
    with open('/Users/ips/dualfoil/dualfoil5.in', 'r+') as file:
        line = file.readline()
        while line != '':
            #make sure restart is set to true
            if line.find('.false.') != -1:
                firstRst = True
                line = line.replace('.false.', '.true.')
                
            
            if (tracker == True):
                #if we have already made all required modifications, add new leg
                if (modified == True):
                    newLeg = str(cu) + ' ' + str(tt) + ' ' + str(mc) + ' ' + str(vcutL) + ' ' + str(vcutH) + ' !' + title + '\n'
                    newInput += newLeg
                    tracker = False 
                else: 
                    #Make required modifications; should be left with a reference leg and the new leg.

                    #Get the total simulation time; we might need it
                    rstFile = open('/Users/ips/dualfoil/df_restart.dat', 'r')
                    rstLine = rstFile.readline()
                    rstLine = rstLine.split('        ') #two values separated by 8 spaces
                    totalT = float(rstLine[1]) / 60.0    #convert to minutes
                    rstFile.close() 
                    
                    #if there are 2 legs from a previous restart, only keep the last one
                    if firstRst == False: 
                        line = file.readline()
                        #^this leg^ will become the reference leg for the next simulation

                        #modify tt(i) of most recent leg if it is terms of time
                        tmp = line.split(' ')
                        
                        #check mc(i): did most recent leg depended on time?
                        if float(tmp[2]) == 1 or float(tmp[2]) == 0:
                            #replace old tt(i) with total run time so far
                            oldTT = float(tmp[1])
                            line = line.replace(str(oldTT), str(totalT))

                    #mark that we have completed tasks
                    modified = True
            
            #find line before the one we need; set tracker for next loopthru
            if line.find('lcurs') != -1 and modified == False:
                #if first restart, must change lcurs to 2 steps
                if firstRst == True:
                    line = line.replace('1', '2', 1)
                tracker = True
            
            #keep up the new file and read next line
            newInput += line  
            line = file.readline()
            
    with open('/Users/ips/dualfoil/dualfoil5.in', 'w') as file:
        file.write(newInput)


# OUTPUT:

#for extracting and organizing data from dualfoil5.out

def extract_main_output(file):
    """
    Parameters
    ----------
    file : str
        main output file (most likely "Dualfoil5.out") generated by Dualfoil 5.2
        
    Returns
    -------
    time : list of float
    n_util : list of float
    p_util : list of float
    potential : list of float
    uocp : list of float
    curr : list of float
    temp : list of float
    heatgen : list of float
    """
    
    #first go through and find position where output starts in file
    x = 0
    previous = ''
    with open(file, 'r') as fin:
        data_list = []
            
        for line in fin.readlines():
            if line.find('(min)') != -1:
                #found it! stop here
                break
            x += 1
    
    #now read lines again 
    with open(file, 'r') as fin:
        
        for line in fin.readlines()[x+2:] :
            #only take lines with convertable data
            if line.find(',') != -1:
                #make sure we are not taking in a copy 
                if line != previous:
                    previous = line
                    line = line.rstrip('\n').rstrip(' ').lstrip(' ')
                    data_list.append(line)  
                
    #variable lists for each time
    time = [];
    n_util = []
    p_util = []
    potential = []
    uocp = []
    curr = []
    temp = []
    heatgen = []

    for data in data_list:
        tmp = data.split(',')
        for i in tmp:
            i.lstrip(' ')
        time.append(float(tmp[0]))
        n_util.append(float(tmp[1]))
        p_util.append(float(tmp[2]))
        potential.append(float(tmp[3]))
        uocp.append(float(tmp[4]))
        curr.append(float(tmp[5]))
        temp.append(float(tmp[6]))
        #for 5.1 code
        if (tmp[7] == ' ******'):
            tmp[7] = '0.00'
        heatgen.append(float(tmp[7]))
        
    #return data in order it appears
    return time, n_util, p_util, potential, uocp, curr, temp, heatgen


#NOTES ON OUT SAMPLE DATA
#profiles.out used original input file data
#profiles2.out held 4.3V for 1.5min
#profiles2_detailed.out gives much more data for the above simulation
#profiles3_long.out was set to run 3 min instead of 1.5; stopped at 1.7 due to comp. time

def extract_profiles(file) :
    
    """
    Parameters
    ----------
    file : str
        main output file (most likely "Dualfoil5.out") generated by Dualfoil 5.2
        
    Returns
    -------
    time : list of floats
    distance : list of list of floats
    elec_conc : list of list of floats
    sol-surf : list of list of floats
    liq_potential : list of list of floats
    sol_potential : list of list of floats
    liq_cur : list of list of floats
    jmain : list of list of floats
    jside1 : list of list of floats
    jside2 : list of list of floats
    jside3 : list of list of floats
    """
    
    with open(file, 'r') as fin:
        profile_list = []
        profile = []

        # ignore the first line
        for line in fin.readlines()[1:]:

            line = line.rstrip('\n').rstrip(' ')
            if line == '':
                if profile != []:
                    profile_list.append(profile)
                    profile = []
                continue
            #print(line)
            profile.append(line)
            
    # list of appropriate variable lists for each time chunk
    distance_list = []
    elec_conc_list = []
    sol_surf_conc_list = []
    liquid_potential_list = []
    solid_potential_list = []
    liquid_cur_list = []
    j_main_list = []
    j_side1_list = []
    j_side2_list = []
    j_side3_list = []
    time_list = []


    # extract numeric data from each chunk into appropriate lists
    for profile in profile_list :
        # extract columns
        distance = []
        elec_conc = []
        sol_surf_conc = []
        liquid_potential = []
        solid_potential = []
        liquid_cur = []
        j_main = []
        j_side1 = []
        j_side2 = []
        j_side3 = []

        # add each row's data into appropriate list
        for row in profile[3:]:
            tmp = row.split(',')
            distance.append(float(tmp[0]))
            elec_conc.append(float(tmp[1]))
            sol_surf_conc.append(float(tmp[2]))
            liquid_potential.append(float(tmp[3]))
            solid_potential.append(float(tmp[4]))
            liquid_cur.append(float(tmp[5]))
            j_main.append(float(tmp[6]))
            j_side1.append(float(tmp[7]))
            j_side2.append(float(tmp[8]))
            j_side3.append(float(tmp[9]))
            

        #add each data list to its corresponding vector
        distance_list.append(distance)
        elec_conc_list.append(elec_conc)
        sol_surf_conc_list.append(sol_surf_conc)
        liquid_potential_list.append(liquid_potential)
        solid_potential_list.append(solid_potential)
        liquid_cur_list.append(liquid_cur)
        j_main_list.append(j_main)
        j_side1_list.append(j_side1)
        j_side2_list.append(j_side2)
        j_side3_list.append(j_side3)

        # extract time step and add to time list
        tmp = profile[2]
        time = float(tmp.lstrip('t = ').split(' ')[0]) 
        time_list.append(time)
    
    #return data in order it appears
    return time_list, distance_list, elec_conc_list, sol_surf_conc_list, liquid_potential_list,    solid_potential_list, liquid_cur_list, j_main_list, j_side1_list, j_side2_list, j_side3_list


