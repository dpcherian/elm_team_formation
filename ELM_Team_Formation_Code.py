#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from itertools import combinations as comb
import time
import random

import tkinter as tk
get_ipython().run_line_magic('gui', 'tk')


# # Common Functions for All 

# In[2]:


def write_csv(names,groups,group_constraints,input_file, output_file):
    import csv
    import datetime
    
    
    def calculate_group_happiness(g,gc):
        
        s=0
        
        nums = np.arange(0,len(g),1)    # Indices for each person in the group
        
        all_pairs = list(comb(nums,2))  # All pairs of individuals  
        
        for pair in all_pairs:
            
            pair_score = score(gc[pair[0]],gc[pair[1]])
            
            s = s + pair_score
        
        return s
    
    
    print_satisfaction = 0
    max_poss_happiness = 1
    
    if(len(group_constraints)!=0):
        print_satisfaction=1

        dummy_group = []
        dummy_group_constraints = []

        for i in range(0,len(group_constraints[0])):
            dummy_prefs = []
            dummy_group.append("person"+str(i+1))

            for j in range(0,len(group_constraints[0][0])):
                dummy_prefs.append("dummy"+str(j+1))

            dummy_group_constraints.append(dummy_prefs)

        dummy_group_constraints=np.array(dummy_group_constraints)
        max_poss_happiness=calculate_group_happiness(dummy_group,dummy_group_constraints)

    print()
    print("Maximum possible happiness is: "+str(max_poss_happiness))
    print("Creating output CSV.")
    print("Groups written to file: ",end=" ")
    
    data = pd.read_csv(input_file)
    
    
    date = datetime.datetime.now()
    dateString = date.strftime("-%Y-%b-%d_%H-%M-%S")
    fileName = output_file+dateString+".csv"
  
    counter = 0
    personCounter = 0

    with open(fileName, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data.columns.values)  # Write the first line with column headers
        
        
        for i in range(0,len(groups)):
            group = groups[i]
            
            if(print_satisfaction>0):
                group_happiness = calculate_group_happiness(groups[i],group_constraints[i])
                satisfaction = str(np.round(100.0*(group_happiness/max_poss_happiness),2))+"%" # This the "percentage" of happiness
            else:
                satisfaction = "Not defined"
            
            
            writer.writerow(["Group "+str(counter+1),"","Satisfaction: "+satisfaction])
            
            for person in group:
                
                if(person[0:8]!="!phantom"):
                    personCounter = personCounter + 1
                    index = np.where(names==person)[0][0]

                    line = data.iloc[[index]].fillna('').values[0]
                    writer.writerow(line)
#                 else:
#                     writer.writerow(["THE GHOST WHO WALKS"])
                    
            writer.writerow([])

            counter = counter + 1
            print(counter,end=" ")
    
    print()
    print("Done creating CSV.")
    print()
    print("Total students processed: "+str(personCounter))
            

def score(list1,list2):                        # accept 2 lists to compare
    num = 0                                    # to store rating of lists
    t = len(list1)                             # total number of preferences
    
    for i in range(0,len(list1)):
        for j in range(0,len(list2)):
            if(list1[i]==list2[j]):            # If any element of list1 is present in list2
                num = num + ((t-i)*(t-j))**2         # (in any order) increment num
    
    for i in range(0,len(list1)):              # if order is the same, add extra
        if(list1[i]==list2[i]):                # points. If 1st pref same, add 12
            num = num + int((24/(i+1))**2)     # for 2nd, add 6, and 3rd 4
    
    return num                            


def happiness(group,names,pair_rating):  # group is a "group" [name1, name2]
                                         # Remarkably, this also works when "group" is a pair of two groups!
                                         # Which is why it is *also* used in the group_pairs function!
    nums = []
    
    names = np.array(names)
    
    for i in range(0,len(group)):
        nums.append(np.where(names==group[i])[0][0])
        
    pairs_in_group = list(comb(nums,2))
        
    happiness = 0

    for pair in pairs_in_group:
        happiness = happiness + pair_rating[pair[0]][pair[1]]
    
    return(happiness)


# # Code to create Quartets

# In[3]:


def pair_groupmates(names,preferred_groupmate,constraints):
    
    print("Begin pairing preferred teammates.")
    
    # Assumptions in this function:
    # 1) All members are paired with one and only one other member
    # 2) Pairs are unique (A-->C => C-->A)
    # 3) All pair members have exactly the same preferences (constraints)
    
#     names               = np.array(["A","B","C","D","E","F"])
#     preferred_groupmate = np.array(["", "E", "D","C" ,"B",""])
#     d1 = [1,2,3,3,2,0]
#     d2 = [6,7,8,8,7,10]
#     d3 = [11,12,13,13,12,20]
    
#     constraints         =  np.array([d1,d2,d3])
#     print(constraints)
    groups = []
    group_constraints = []
    new_names=[]
    new_constraints = []
    i=0
    
    while(i<len(names)):
        
        if(preferred_groupmate[i]==''):
            new_names.append(names[i])
            new_constraints.append(constraints[:,i].tolist())
            i=i+1
            continue
       
        pair = [names[i],preferred_groupmate[i]]
  
        groups.append(pair)
        
        
        index = np.where(preferred_groupmate == names[i])
        
        if(len(index[0])>1):
            print("ERROR! " + names[i] + " has been chosen twice!")
            break
        elif(len(index[0])==1):
            temp = index[0][0]
            group_constraints.append([constraints[:,i].tolist(),constraints[:,temp].tolist()])
            names = np.delete(names,temp)
            preferred_groupmate = np.delete(preferred_groupmate,temp)
            constraints = np.delete(constraints,temp,axis=1)
            
        i = i+1

        # The new_constraints here is a little odd, while in this function we use constraints[:,index] to
        # get a person's preferences, if you wanted to do the same thing with new_constraints, you need to use
        # new_constraints[index,:]. I'd try to fix it, but it doesn't really matter and I can't be too bothered.
    
    print("Done pairing preferred teammates.")
    
    return new_names, new_constraints, groups, group_constraints


# In[4]:


def pair_remaining(names,constraints,groups,group_constraints):
    
    print("Begin pairing remaining students.")
    print("Students remaining:",end=" ")
    
    names = np.array(names)
    constraints = np.array(constraints) # Check final comment in pair_groupmates regarding how this is indexed.
    
    while(len(names)>0):
    
        N = len(names)
        #print(N)
        pair_rating = np.zeros((N,N),int)


        ## Create pair_ratings based on the provided names array

        for i in range(0,N):
            for j in range(i+1,N):

                #print(constraints[i,:],constraints[j,:])
                s = score(constraints[i,:],constraints[j,:])

                pair_rating[i,j]=s
                pair_rating[j,i]=s 

        ## Finding the best match among all pairs of students provided by the names array

        all_pairs = list(comb(names,2))    # List of all pairs of students

        happiness_array = []               # Array to store the happiness of each pair

        # Find happiness for every pair

        for i in range(0, len(all_pairs)):
            happiness_array.append(happiness(all_pairs[i],names,pair_rating))

        happiness_array=np.array(happiness_array)  # Convert it to a numpy array

        max_val = max(happiness_array)             # Find maximum value of the happiness array. 

        pair_nums = np.where(happiness_array==max_val)[0] # Find pairs that have this max_val. Returns an array 
                                                          # since there may be more than one result. The array
                                                          # contains integers that represent the position of the pair
                                                          # in the happiness_array / all_pairs lists.

        #### COULD BE BETTER -- Right now choosing randomly

        # Since there could be many pairs that have the same "largest" value of happiness, and since 
        # the same student(s) may be present in multiple pairs, we have a slight problem. To circumvent this, I
        # have decided to choose a pair at random. However, I continue to use pair_nums as if it were an array of pairs
        # so that if I want to improve on this later, I don't need to change the code.

        # Ideally, I'd like to remove all cases where the same person exists in more than one pair (by, say, choosing
        # one of *those* pairs randomly), and then pair up all the rest. But frankly, now that I think about it, I
        # don't think it'd really be very different from what I'm doing now.

        pair_nums = [random.choice(pair_nums)] 

        for pair in pair_nums:
    
            people = all_pairs[pair]
            sample = [people[0],people[1]]         # Group with names instead of numbers

            sample_constraints = []

            for person in sample:

                index = np.where(names==person)[0][0]
                sample_constraints.append(constraints[index,:])

                names = np.delete(names,index)
                constraints = np.delete(constraints, index, axis = 0)

            groups.append(sample)
            group_constraints.append(sample_constraints)

            print(len(names),end=" ")
    print()
    print("Done pairing remaining students.")
    return groups, group_constraints


# In[5]:


def groups_pairs(groups,group_constraints):
    
    print("Begin creating quartets.")
    print("Pairs remaining:",end=" ")
    
    groups, group_constraints = np.array(groups), np.array(group_constraints)
    
    # The idea here is to group the pairs by similar interests. We will again need to make a "pair_ratings"
    # type table, and pick out the pairs that have a maximum value. This function should thus follow very
    # closely the logic of the function pair_remaining.
    
    final_quartets = []                      # Array to store results of final quartets.
    final_quartet_constraints = []           # Array to store constraints of final quartets
    
    while(len(groups)>0):
    
    
        N = len(groups)

        quartet_rating = np.zeros((N,N),int) # We now have groups of 4, so it's a quartet rating


        ## Create quartet_ratings based on the provided groups array

        for i in range(0,N):
            for j in range(i+1,N):

                # The two groups to compare are now groups[i] and groups[j], each with their own 'interests'
                # group_constraints[i,:], group_constraints[j,:].

                # To calculate the score of the potential team formed by [A, B] and [C, D], I calculate the 
                # score(A,C) + score(B,D) + score(A,D) + score(B,C). I *do not* add to it the score of (A,B) and
                # (C,D), to avoid groups having a very strong compatibility mucking it up for everyone else.
                # Below is a simple piece of code you can uncomment to see how the score is calculated

#                 print("Groups formed by", groups[i], " and ", groups[j])

#                 print(groups[i][0], "   ", groups[j][0])
#                 print(group_constraints[i,:][0],"\n",group_constraints[j,:][0])

#                 print(groups[i][1], "   ", groups[j][1])
#                 print(group_constraints[i,:][1],"\n",group_constraints[j,:][1])

#                 print(groups[i][0], "   ", groups[j][1])
#                 print(group_constraints[i,:][0],"\n",group_constraints[j,:][1])

#                 print(groups[i][1], "   ", groups[j][0])
#                 print(group_constraints[i,:][1],"\n",group_constraints[j,:][0])

                # s below uses the algorithm mentioned above s(AC) + s(BD) + s(AD) + s(BC)
                s = score(group_constraints[i,:][0],group_constraints[j,:][0]) + score(group_constraints[i,:][1],group_constraints[j,:][1]) + score(group_constraints[i,:][1],group_constraints[j,:][0]) + score(group_constraints[i,:][0],group_constraints[j,:][1])

                quartet_rating[i,j]=s
                quartet_rating[j,i]=s 

        ## Finding the best match among all pairs of pairs provided by the groups array

        all_quartets = list(comb(groups.tolist(),2))    # List of all pairs of pairs of students
        #print(all_quartets[0])

        happiness_array = []               # Array to store the happiness of each quartet

        # Find happiness for every quartet

        for i in range(0, len(all_quartets)):
            happiness_array.append(happiness(all_quartets[i],groups,quartet_rating))

        happiness_array=np.array(happiness_array)  # Convert it to a numpy array

        max_val = max(happiness_array)             # Find maximum value of the happiness array. 

        quartet_nums = np.where(happiness_array==max_val)[0] # Find quartets that have this max_val. Returns an array 
                                                             # since there may be more than one result. The array
                                                             # contains integers that represent the position of the
                                                             # quartet in the happiness_array / all_quartets lists.


        #### COULD BE BETTER -- Right now choosing randomly

        # Since there could be many quartets that have the same "largest" value of happiness, and since 
        # the same pair(s) may be present in multiple quartets, we have a slight problem. To circumvent this, I
        # have decided to choose a quartet at random. However, I continue to use quartet_nums as if it were an array of pairs
        # so that if I want to improve on this later, I don't need to change the code.

        # Ideally, I'd like to remove all cases where the same pair exists in more than one quartet (by, say, choosing
        # one of *those* quartets randomly), and then pair up all the rest. But frankly, now that I think about it, I
        # don't think it'd really be very different from what I'm doing now.

        quartet_nums = [random.choice(quartet_nums)] 


        for quartet in quartet_nums:

            pairs = all_quartets[quartet]
            
            sample = pairs[0].copy()              # Make a copy of the first pair

            for person in pairs[1]:
                sample.append(person)             # Append to this copy all people in second pair.
                                                  # The variable sample now has a full quartet

            #print(sample)

            sample_constraints = []               # Array to store constraints of quartet

            for pair in pairs:
                index = np.where(groups==pair)[0][0]
                for constraint in group_constraints[index,:]:
                    sample_constraints.append(constraint.tolist())

                groups = np.delete(groups,index,axis=0)                           # Axis is important! Pay attention.
                group_constraints = np.delete(group_constraints, index, axis = 0)

            final_quartets.append(sample)
            final_quartet_constraints.append(sample_constraints)

            print(len(groups),end=" ")
    
    print()
    print("Done creating quartets.")
    
    return final_quartets, final_quartet_constraints


# # Code to create Groups of Indeterminate Sizes

# In[6]:


def create_indeterminate_groups(new_names, new_d1, new_d2, new_d3, new_d4, new_d5):
    
    N = len(new_names)
    pref = np.zeros((N,N),int)
    
    for i in range(0,N):
        for j in range(i+1,N):

            s = score([new_d1[i],new_d2[i],new_d3[i],new_d4[i],new_d5[i]],[new_d1[j],new_d2[j],new_d3[j],new_d4[j],new_d5[j]])

            pref[i,j]=s
            pref[j,i]=s 
    
    
    class_pairs = list(comb(new_names,2))
    
    happiness_array = []
    
    for i in range(0, len(class_pairs)):
        happiness_array.append(happiness(class_pairs[i],new_names,pref))
    
    happiness_array=np.array(happiness_array)
    
    #print("happiness checked " + str(np.sum(happiness_array)))
    
    #print(happiness_array)
    
    max_val = max(happiness_array)
    #print("Max happiness is" + str(max_val))
    pair_nums = np.where(happiness_array==max_val)[0]
    #print(pair_nums)
    
    #### COULD BE BETTER -- Right now choosing randomly
    
    pair_nums = [random.choice(pair_nums)]
    
    for pair in pair_nums:
        people = class_pairs[pair]
        sample = np.array([people[0],people[1]])
        #print(sample)
        pref1 = []
        pref2 = []
        pref3 = []
        
        pref4 = []
        pref5 = []

        for person in sample:
            index = np.where(new_names==person)[0][0]
            pref1.append(new_d1[index])
            pref2.append(new_d2[index])
            pref3.append(new_d3[index])
            
            pref4.append(new_d4[index])
            pref5.append(new_d5[index])
            

            new_names = np.delete(new_names,index)
            new_d1 = np.delete(new_d1,index)
            new_d2 = np.delete(new_d2,index)
            new_d3 = np.delete(new_d3,index)
            
            new_d4 = np.delete(new_d5,index)
            new_d5 = np.delete(new_d5,index)


        new_names = np.append(new_names,str(sample[0])+"-"+str(sample[1]))
        
        ##### COULD BE BETTER -- Currently random choice 
        ##### is made between 1st,2nd,3rd preferences respectively
        
        new_d1 = np.append(new_d1,random.choice(pref1))
        new_d2 = np.append(new_d2,random.choice(pref2))
        new_d3 = np.append(new_d3,random.choice(pref3))
        
        new_d4 = np.append(new_d4,random.choice(pref4))
        new_d5 = np.append(new_d5,random.choice(pref5))
    
    print(len(new_names),end=" ")
    return new_names,new_d1,new_d2,new_d3,new_d4,new_d5,max_val


# # Functions called directly by GUI

# In[7]:


def run_groups_of_four(names,preferred_groupmate,constraints,input_filename, output_filename):
    
    # Make groups out of the team member preferences
    new_names, new_constraints, groups, group_constraints = pair_groupmates(names,preferred_groupmate,constraints)

    # Assign the remaining students to groups based on constraints (project preferences etc.)
    groups, group_constraints = pair_remaining(new_names,new_constraints,groups,group_constraints)

    # Make groups of 4 out of the pairs
    quartets, quartet_constraints = groups_pairs(groups,group_constraints)

    # Write resulting groups to a .csv file
    write_csv(names, quartets, quartet_constraints, input_filename, output_filename)


def run_groups_of_two(names,preferred_groupmate,constraints,input_filename,output_filename):
    
    # Make groups out of the team member preferences
    new_names, new_constraints, groups, group_constraints = pair_groupmates(names,preferred_groupmate,constraints)
    
    # Assign the remaining students to groups based on constraints (project preferences etc.)
    groups, group_constraints = pair_remaining(new_names,new_constraints,groups,group_constraints)

    # Write resulting groups to a .csv file
    write_csv(names, groups, group_constraints, input_filename, output_filename)
    

def run_indeterminate_groups(names,preferred_groupmate,constraints,max_groups,input_filename,output_filename):
    
    ## This part of the code assumes both preferred teammates have same preferences.
    
    # Make groups out of the team member preferences
    new_names, new_constraints, paired_teammates, paired_constraints = pair_groupmates(names,preferred_groupmate,constraints)
    
    print(len(new_names),end=" ")
    
    for i in range(0,len(paired_teammates)):
        
        group = paired_teammates[i]
        
        if(len(group)>2):
            print("ERROR! More than two preferred teammates paired together. Output unreliable.")
        
        temp = group[0]+"-"+group[1]
        
        new_names.append(temp)
        
        new_constraints.append(paired_constraints[i][0])   # Assuming both teammates have same preferences, so
                                                           # only appending the preferences of the first 
        
    
    new_names = np.array(new_names)
    new_constraints = np.array(new_constraints)
    
    new_d1 = new_constraints[:,0].copy()
    new_d2 = new_constraints[:,1].copy()
    new_d3 = new_constraints[:,2].copy()

    new_d4 = new_constraints[:,3].copy()
    new_d5 = new_constraints[:,4].copy()
    
    print("Starting pairing.")
    print("Groups remaining: ",end=" ")
    
    while(len(new_names)>max_groups):
        new_names, new_d1, new_d2, new_d3, new_d4, new_d5, val = create_indeterminate_groups(new_names,new_d1,new_d2,new_d3,new_d4,new_d5)
        print(len(new_names),end=" ")
    print("Done pairing.")
    
    groups = []
    
    for group in new_names:
        members = group.split("-")
        groups.append(members)
    
    group_constraints = np.array([]) # As of right now, we can't measure a score for indeterminate groups.
    
    write_csv(names,groups,group_constraints,input_filename,output_filename)


# # Adding Phantom Students

# In[8]:


## Adding Phantom Students to make the numbers divisible by 4

def add_one_phantom(names,preferred_groupmate,constraints,phantomNo):
    names = np.append(names,"!phantom"+str(phantomNo))
    preferred_groupmate = np.append(preferred_groupmate,"")
    
    dummy_constraint = []
    
    for i in range(0,len(constraints)):
        dummy_constraint.append("!pcriterion"+str(i+1))
        
    constraints = np.c_[constraints,dummy_constraint]
    
    phantomNo = phantomNo + 1
    
    return names,preferred_groupmate,constraints,phantomNo
    
def add_two_phantom(names,preferred_groupmate,constraints,phantomNo):
    
    # Add First Person
    
    names = np.append(names,"!phantom"+str(phantomNo))
    preferred_groupmate = np.append(preferred_groupmate,"!phantom"+str(phantomNo+1))
    
    # Add Second Person 
    
    names = np.append(names,"!phantom"+str(phantomNo+1))
    preferred_groupmate = np.append(preferred_groupmate,"!phantom"+str(phantomNo))
    
    # Dummy constraints for both (they have the same), so appended twice
    
    dummy_constraint = []
    
    for i in range(0,len(constraints)):
        dummy_constraint.append("!pcriterion"+str(i+1))
        
    constraints = np.c_[constraints,dummy_constraint]
    constraints = np.c_[constraints,dummy_constraint]
    
    phantomNo = phantomNo + 2
    
    return names,preferred_groupmate,constraints,phantomNo


# # The GUI (Main)

# In[9]:


from tkinter import *
import tkinter.messagebox as messagebox
import traceback
from tkinter import ttk
from tkinter import filedialog 

versionNumber = "1.0"

def browseFiles(): 
    filename = filedialog.askopenfilename(initialdir = "./", 
                                          title = "Select a File", 
                                          filetypes = (("Text files", 
                                                        "*.csv"), 
                                                       ("all files", 
                                                        "*.*"))) 
    # Change label contents 
    entryText.set(filename)
    updateLists(filename)
       


def get_input():
    
    try:
        
        input_filename = fileName.get()                # Get the name of the input file
        
        #uid = "First Name"                             # Get the UID string title
        #ptm = "Preferred Team Member (Paired)"         # Get the Preferred Team-mate column title
        
        data = pd.read_csv(input_filename)
        names = data[uid_field.get()].values
        preferred_groupmate = data[ptm_field.get()].fillna('').values        
        
        d_array = [c1.get(),c2.get(),c3.get(),c4.get(),c5.get()]
        
        constraints = []
        
        for element in d_array:
            if(len(element)!=0):
                constraints.append(data[element].values)
        
        constraints = np.array(constraints)
        
        #####################################################
        ##                                              #####
        ## Dealing with odd numbers of people or groups #####
        ## As of now the code creates either groups of  #####
        ## two or four, and so we need to make sure the #####
        ## arrays above are multiples of 4. This is not #####
        ## essential for the indeterminate sized groups.#####
        ## We add enough"phantom" students to do this.  #####
        ##                                              #####
        #####################################################
        
        print("Total number of students: "+str(len(names)))
        
        phantomNo = 1      # A counter for the number of phantom students added.
        
        if(len(names)%4==3):
            names,preferred_groupmate,constraints,phantomNo = add_one_phantom(names,preferred_groupmate,constraints,phantomNo)
        elif(len(names)%4==2):
            names,preferred_groupmate,constraints,phantomNo = add_two_phantom(names,preferred_groupmate,constraints,phantomNo)
        elif(len(names)%4==1):
            names,preferred_groupmate,constraints,phantomNo = add_one_phantom(names,preferred_groupmate,constraints,phantomNo)
            names,preferred_groupmate,constraints,phantomNo = add_two_phantom(names,preferred_groupmate,constraints,phantomNo)
        
        print("Number of phantoms added: "+ str(phantomNo-1) + " (Yay!)")
        print()
        
        button = v.get()
        
        max_groups = int(max_groups_entry.get())
        
        output_filename = output_file.get()
        
        if button == 1:
            if(len(names)%4!=0):
                messagebox.showerror("What on Earth!","It seems that the number of students isn't a multiple of four.",detail="This error certainly shoudn't occur. Call Philip up and complain at once!")
            else:
                run_groups_of_four(names,preferred_groupmate,constraints,input_filename,output_filename)
        elif button == 2:
            if(len(names)%2!=0):
                messagebox.showerror("What on Earth!","It seems that the number of students isn't a multiple of two.",detail="This error certainly shoudn't occur. Call Philip up and complain at once!")
            else:
                run_groups_of_two(names,preferred_groupmate,constraints,input_filename,output_filename)
        elif button == 3:
            #run_beta_groups_of_four()
            messagebox.showerror("Work in progress!","I'm working on how to do this.",detail="Hopefully should be done in a couple of days.")
        elif button == 4:
            if(len(constraints)!=5):
                messagebox.showerror("Work in progress!","Currently all five preferences are needed for groups of indeterminate sizes.",detail="Hopefully should be done in a couple of days.")
            else:
                run_indeterminate_groups(names,preferred_groupmate,constraints,max_groups,input_filename,output_filename)
        
    except Exception as e:
        messagebox.showerror("Oh No!",e,detail=traceback.format_exc())
    root.destroy()
    
    
    
##### Graphic User Interface ############################   
##                                                      #
## This uses TkInter to create a simple GUI. Pressing   #
## the 'Submit' button leads to the above 'get_input'   #
## function to run with specific options.               #
##                                                      #
#########################################################


root = Tk()

root.title("ELM Team Formation Tool (v "+versionNumber+")")

f1 = Frame(root, relief=GROOVE, width=50,height=50,borderwidth=0)
f1.pack()



label1 = Label(f1,text = 'Raw Data File (example.csv)')
label1.pack(pady=5)
label1.config(justify = CENTER)


entryText = StringVar(value='Final_Sample_Data.csv')
fileName = Entry(f1, width = 40,textvariable=entryText)
fileName.pack(side=LEFT,pady=10)

button_explore = Button(f1,text = "Browse",
                        command = browseFiles,
                        bg='#aaa662').pack(side=RIGHT)


f = Frame(root, relief=GROOVE, width=50,height=50,borderwidth=2)
f.pack()

## Radio Buttons #############################################


v = IntVar(value=1)

Label(f, 
        text="How would you like the groups formed?",
        justify = LEFT,
        padx = 20).pack(pady=10)

Radiobutton(f, 
              text="Groups of 4",
              padx = 20, 
              variable=v, 
              value=1).pack(anchor=W)

Radiobutton(f, 
              text="Groups of 2",
              padx = 20, 
              variable=v, 
              value=2).pack(anchor=W)

Radiobutton(f, 
              text="Groups of 4 (Warning! May take up to 1 hour)",
              padx = 20, 
              variable=v, 
              value=3).pack(anchor=W)


Radiobutton(f, 
              text="Groups of indeterminate sizes. Total groups:",
              padx = 20, 
              variable=v, 
              value=4).pack(anchor=W,side=LEFT)

max_groups_entry = Entry(f, width = 3,justify=CENTER)
max_groups_entry.insert(END,'40')
max_groups_entry.pack(anchor=W,side=RIGHT,padx=10)

###################################################################


## Make sure the right dropbox menus show #########

def updateLists(filename):
    
    if(len(filename)!=0):
    
        data = pd.read_csv(filename)
        listvalues = list(data.columns)

        uid_field['values'] = listvalues
        ptm_field['values'] = listvalues
        c1['values'] = listvalues
        c2['values'] = listvalues
        c3['values'] = listvalues
        c4['values'] = listvalues
        c5['values'] = listvalues        

###################################################


input_filename = fileName.get()

uid = "UID"                             # Get the UID string title
ptm = "Team_Member"                     # Get the Preferred Team-mate column title

c1temp = "ProjPref_1"
c2temp = "ProjPref_2"
c3temp = "ProjPref_3"
c4temp = "ProjPref_4"
c5temp = "ProjPref_5"

# data = pd.read_csv(input_filename)
# listvalues = list(data.columns)

listvalues = []


label1a = Label(root, text="Unique Identifier")
label1a.pack(pady=(10,0))
label1a.config(justify = CENTER)

uid_field = ttk.Combobox(root,width=50,values=listvalues)
uid_field.insert(END,uid)
uid_field.pack(pady=(0,5))


label1b = Label(root, text="Preferred Teammates")
label1b.pack(pady=(10,0))
label1b.config(justify = CENTER)

ptm_field = ttk.Combobox(root,width=50,values=listvalues)
ptm_field.insert(END,ptm)
ptm_field.pack(pady=(0,5))


label2 = Label(root, text="Criterion 1")
label2.pack(pady=(10,0))
label2.config(justify = CENTER)

#c1 = Entry(root, width = 50)
c1 = ttk.Combobox(root,width=50,values=listvalues)
c1.insert(END,c1temp)
c1.pack(pady=(0,5))

label3 = Label(root, text="Criterion 2")
label3.pack(pady=(10,0))
label3.config(justify = CENTER)

#c2 = Entry(root, width = 50)
c2 = ttk.Combobox(root,width=50,values=listvalues)
c2.insert(END,c2temp)
c2.pack(pady=(0,5))

label4 = Label(root, text="Criterion 3")
label4.pack(pady=(10,0))
label4.config(justify = CENTER)

#c3 = Entry(root, width = 50)
c3 = ttk.Combobox(root,width=50,values=listvalues)
c3.insert(END,c3temp)
c3.pack(pady=(0,5))

label5 = Label(root, text="Criterion 4")
label5.pack(pady=(10,0))
label5.config(justify = CENTER)

#c4 = Entry(root, width = 50)
c4 = ttk.Combobox(root,width=50,values=listvalues)
c4.insert(END,c4temp)
c4.pack(pady=(0,5))

label6 = Label(root, text="Criterion 5")
label6.pack(pady=(10,0))
label6.config(justify = CENTER)

#c5 = Entry(root, width = 50)
c5 = ttk.Combobox(root,width=50,values=listvalues)
c5.insert(END,c5temp)
c5.pack(pady=(0,5))

button1 = Button(root, text = 'Submit',bg='#4B8BBE')
button1.pack(pady=5) 
button1.config(command = get_input)

label7 = Label(root, text="Output File (Date and time will be appended)")
label7.pack()
label7.config(justify = CENTER)

output_file = Entry(root, width = 50)
output_file.insert(END,'groups')
output_file.pack()




root.mainloop()


# In[ ]:




