#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
from itertools import combinations as comb
import time
import random

import tkinter as tk
#get_ipython().run_line_magic('gui', 'tk')


# # Common Functions for All 

# In[ ]:


def write_csv(names,groups,output_file):
    import csv
    import datetime
    
    print("Creating output CSV.")
    
    data = pd.read_csv("Biased_Data.csv")
    names = data["First Name"].values
    preferred_groupmate = data["Preferred Team Member (Paired)"].fillna('').values        

    d1 = data["Project Preference 1"].values
    d2 = data["Project Preference 2"].values
    d3 = data["Project Preference 3"].values

    d4 = data["Project Preference 4"].values
    d5 = data["Project Preference 5"].values
    
    
    
    date = datetime.datetime.now()

    dateString = date.strftime("-%Y-%b-%d_%H-%M-%S")
    
    fileName = output_file+dateString+".csv"
  
    counter = 0 

    with open(fileName, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data.columns.values)  # Write the first line with column headers
        
        
        for group in groups:
            writer.writerow(["Group "+str(counter+1)])

            for person in group:
                index = np.where(names==person)[0][0]

                line = data.iloc[[index]].fillna('').values[0]
                writer.writerow(line)
            writer.writerow([])

            counter = counter + 1
            print(counter)
    
    print("Done creating CSV.")
            

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

# In[ ]:


def pair_groupmates(names,preferred_groupmate,constraints):
    
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
    return new_names, new_constraints, groups, group_constraints


# In[ ]:


def pair_remaining(names,constraints,groups,group_constraints):
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

            print(len(names))
        
    return groups, group_constraints


# In[ ]:


def groups_pairs(groups,group_constraints):
    
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

            print(len(groups))
            
    return final_quartets, final_quartet_constraints


# # Code to create Groups of Indeterminate Sizes

# In[ ]:


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
    
    print(len(new_names))
    return new_names,new_d1,new_d2,new_d3,new_d4,new_d5,max_val


# In[ ]:


def run_groups_of_four(names,preferred_groupmate,constraints,output_filename):
    
    # Make groups out of the team member preferences
    new_names, new_constraints, groups, group_constraints = pair_groupmates(names,preferred_groupmate,constraints)

    # Assign the remaining students to groups based on constraints (project preferences etc.)
    groups, group_constraints = pair_remaining(new_names,new_constraints,groups,group_constraints)

    # Make groups of 4 out of the pairs
    quartets, quartet_constraints = groups_pairs(groups,group_constraints)

    # Write resulting groups to a .csv file
    write_csv(names, quartets, output_filename)


def run_groups_of_two(names,preferred_groupmate,constraints,output_filename):
    
    # Make groups out of the team member preferences
    new_names, new_constraints, groups, group_constraints = pair_groupmates(names,preferred_groupmate,constraints)
    print(groups)
    # Assign the remaining students to groups based on constraints (project preferences etc.)
    groups, group_constraints = pair_remaining(new_names,new_constraints,groups,group_constraints)

    # Write resulting groups to a .csv file
    write_csv(names, groups, output_filename)
    

def run_indeterminate_groups(names,preferred_groupmate,constraints,max_groups,output_filename):
    
    ## This part of the code assumes both preferred teammates have same preferences.
    
    # Make groups out of the team member preferences
    new_names, new_constraints, paired_teammates, paired_constraints = pair_groupmates(names,preferred_groupmate,constraints)
    
    print(len(new_names))
    
    for i in range(0,len(paired_teammates)):
        
        group = paired_teammates[i]
        
        if(len(group)>2):
            print("ERROR! More than two preferred teammates paired together. Output unreliable.")
        
        temp = group[0]+"-"+group[1]
        
        new_names.append(temp)
        
        new_constraints.append(paired_constraints[i][0])   # Assuming both teammates have same preferences, so
                                                           # only appending the preferences of the first 
        print(len(new_names))
        
    
    new_names = np.array(new_names)
    new_constraints = np.array(new_constraints)
    
    new_d1 = new_constraints[:,0].copy()
    new_d2 = new_constraints[:,1].copy()
    new_d3 = new_constraints[:,2].copy()

    new_d4 = new_constraints[:,3].copy()
    new_d5 = new_constraints[:,4].copy()
    
    print("Starting pairing")
    
    while(len(new_names)>max_groups):
        new_names, new_d1, new_d2, new_d3, new_d4, new_d5, val = create_indeterminate_groups(new_names,new_d1,new_d2,new_d3,new_d4,new_d5)
    
    print("Done pairing.")
    
    groups = []
    
    for group in new_names:
        members = group.split("-")
        groups.append(members)
    
    write_csv(names,groups,output_filename)


# In[16]:


from tkinter import *
import tkinter.messagebox as messagebox
import traceback
from tkinter import ttk
from tkinter import filedialog 

def browseFiles(): 
    filename = filedialog.askopenfilename(initialdir = "./", 
                                          title = "Select a File", 
                                          filetypes = (("Text files", 
                                                        "*.csv"), 
                                                       ("all files", 
                                                        "*.*"))) 
    # Change label contents 
    entryText.set(filename) 
       


def get_input():
    
    try:
        data = pd.read_csv(fileName.get())
        names = data["First Name"].values
        preferred_groupmate = data["Preferred Team Member (Paired)"].fillna('').values        
        
        d_array = [c1.get(),c2.get(),c3.get(),c4.get(),c5.get()]
        
        constraints = []
        
        for element in d_array:
            if(len(element)!=0):
                constraints.append(data[element].values)
        
        constraints = np.array(constraints)
        
        
        d1 = data["Project Preference 1"].values
        d2 = data["Project Preference 2"].values
        d3 = data["Project Preference 3"].values

        d4 = data["Project Preference 4"].values
        d5 = data["Project Preference 5"].values
        
        
        button = v.get()
        
        max_groups = int(max_groups_entry.get())
        
        output_filename = output_file.get()

        if button == 1:
            if(len(names)%4!=0):
                messagebox.showerror("Work in progress!","Currently this only works when total number of students is a multiple of 4. Edit your input file.",detail="Hopefully should be done in a couple of days.")
            else:
                run_groups_of_four(names,preferred_groupmate,constraints,output_filename)
        elif button == 2:
            if(len(names)%2!=0):
                messagebox.showerror("Work in progress!","Currently this only works when total number of students is an even number. Edit your input file.",detail="Hopefully should be done in a couple of days.")
            else:
                run_groups_of_two(names,preferred_groupmate,constraints,output_filename)
        elif button == 3:
            #run_beta_groups_of_four()
            messagebox.showerror("Work in progress!","I'm working on how to do this.",detail="Hopefully should be done in a couple of days.")
        elif button == 4:
            if(len(constraints)!=5):
                messagebox.showerror("Work in progress!","Currently all five preferences are needed for groups of indeterminate sizes.",detail="Hopefully should be done in a couple of days.")
            else:
                run_indeterminate_groups(names,preferred_groupmate,constraints,max_groups,output_filename)
        
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

#root.configure(bg='green')
root.title("ELM Team Formation Tool")

f1 = Frame(root, relief=GROOVE, width=50,height=50,borderwidth=0)
f1.pack()



label1 = Label(f1,text = 'Raw Data File (example.csv)')
label1.pack(pady=5)
label1.config(justify = CENTER)


entryText = StringVar(value='Biased_Data.csv')
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



label2 = Label(root, text="Criterion 1")
label2.pack(pady=(10,0))
label2.config(justify = CENTER)

c1 = Entry(root, width = 50)
c1.insert(END,'Project Preference 1')
c1.pack(pady=(0,5))

label3 = Label(root, text="Criterion 2")
label3.pack(pady=(10,0))
label3.config(justify = CENTER)

c2 = Entry(root, width = 50)
c2.insert(END,'Project Preference 2')
c2.pack(pady=(0,5))

label4 = Label(root, text="Criterion 3")
label4.pack(pady=(10,0))
label4.config(justify = CENTER)

c3 = Entry(root, width = 50)
c3.insert(END,'Project Preference 3')
c3.pack(pady=(0,5))

label5 = Label(root, text="Criterion 4")
label5.pack(pady=(10,0))
label5.config(justify = CENTER)

c4 = Entry(root, width = 50)
c4.insert(END,'Project Preference 4')
c4.pack(pady=(0,5))

label6 = Label(root, text="Criterion 5")
label6.pack(pady=(10,0))
label6.config(justify = CENTER)

c5 = Entry(root, width = 50)
c5.insert(END,'Project Preference 5')
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





# In[ ]:




