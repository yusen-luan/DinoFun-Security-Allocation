import datetime
from multiprocessing import Value
from tkinter import END
import tkinter
from Imports import *
#from New_page import *
class App(tk.Tk):
    def __init__(self,title,size):
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        
        self.main=Head(self)
        self.switch=Switch(self)
        self.menu=Menu(self, self.switch)
        self.home_pg=self.switch.add_frame('Home', Home)
        self.da_pg=self.switch.add_frame('DA', DA)
        self.hr_pg=self.switch.add_frame('HR', HR)
        #self.home=Home(self)
        self.mainloop()

    

class Switch:
    def __init__(self, app):
        self.app = app
        self.frames = {}
        self.current_frame = None

    def add_frame(self, name, frame_class):
        frame = frame_class(self.app)
        self.frames[name] = frame
    
    def show_frame(self, name):
        frame = self.frames.get(name)
        if frame:
            if self.current_frame:
                self.current_frame.place_forget()  # Hide the current frame
            frame.place(x=0, y=100, relwidth=1, relheight=0.8) # Show the new frame
            self.current_frame = frame


class Head(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        title=ttk.Label(self, text="DinoFun HR Management & Deployment",background="#085b10",
                       foreground="white", font=("Calibri", 20)).place(x=0,y=0,relwidth=1, relheight=1)
        
        self.place(x=0,y=0, relwidth=1, relheight=0.05)
        
 
class Menu(ttk.Frame):
    def __init__(self, parent, switch):
        super().__init__(parent)
        self.switch=switch
        home_btn=tk.Button(self, text='Home',bd=0,
                       font=("Calibri", 20), command=lambda: self.switch.show_frame('Home')).place(x=50,y=0)

        home_on_lb=tk.Label(self).place(x=0,y=60, width=180, height=5)

        da_btn=tk.Button(self, text='Data Analysis',bd=0,
                       font=("Calibri", 20), command=lambda: self.switch.show_frame('DA')).place(x=180,y=0)

        da_on_lb=tk.Label(self).place(x=172,y=60, width=180, height=5)

        hr_btn=tk.Button(self, text='HR Management',bd=0,
                       font=("Calibri", 20),command=lambda: self.switch.show_frame('HR')).place(x=360,y=0)

        hr_on_lb=tk.Label(self).place(x=370,y=60, width=180, height=5)

        self.place(x=0,y=50, relwidth=1, relheight=0.1)

class Home(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        home_lb=tk.Label(self, text="Welcome to DinoFun HR & Deployment Manager", font=('Calibri', 30, 'bold')).pack()
        #self.place(x=0, y=100, relwidth=1, relheight=0.8)
        
class DA(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.saved_files=[]
        
        self.file_listbox = tk.Listbox(self, selectmode=tk.SINGLE, font=("Calibri", 15))
        self.file_listbox.pack(side='top',padx=20, pady=20, fill='both', expand=True)

        '''scrollbar = tk.Scrollbar(self, orient="vertical", command=file_listbox.yview)
        file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left')'''
        upload_btn=tk.Button(self, text="Upload Data", font=("Calibri",20,"bold"), bd=0, bg="#085b10", 
                         fg="white",activebackground="green",activeforeground="white", command=self.openFile).pack(side='right', padx=20,pady=20)

        create_plan_btn=tk.Button(self, text="Create Plan", font=("Calibri", 20, "bold"), bg="#085b10",
                                    fg="white", activebackground="green", activeforeground="white", command=self.analyse).pack(side='right', padx=20,pady=20)

        self.checkbox_var=tk.BooleanVar()
        save_checkbox=tk.Checkbutton(self, text='Save as Excel', font=('Calibri', 15), variable=self.checkbox_var).pack(side='right',padx=10, pady=20)
        
        self.bind("<Visibility>", lambda event:self.update_file_list())
        self.directory="External Uploads"
        self.error_displayed=False
        #self.schedule_present=False
        self.schedule_table=None
    def openFile(self):
        filepath = filedialog.askopenfilename(title="Open files",
                                                filetypes= [("all files","*.*")])

        if filepath:
            self.saved_files.append(filepath)
        
            # Automatically save the opened file
            save_path =r'External Uploads'+ '\\'+os.path.basename(filepath)
            shutil.copyfile(filepath, save_path)
            self.saved_files.append(save_path)
        
            try:
                file = open(filepath,'r')
                filedir=tk.Label(self, text=filepath)
                filedir.pack()
                file.close()

            except FileNotFoundError:
                pass




    def list_files(self, directory):
        files = os.listdir(directory)
        return files

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        files = self.list_files(self.directory)
        for file in files:
            self.file_listbox.insert(tk.END, file)

    def analyse(self):
        
        try:
            if self.schedule_table is not None:
                self.schedule_table.destroy()
            selected_file = self.file_listbox.get(self.file_listbox.curselection())        
            file_path = os.path.join(self.directory, selected_file)
        
            
            df = pd.read_csv(file_path)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            date=None


            filtered_df = df[df['Timestamp'].dt.minute % 30 == 0]

           
            def distance(x1, y1, x2, y2):
                    x_diff=x2-x1
                    y_diff=y2-y1
                    return math.sqrt(x_diff**2+y_diff**2)


            grouped = filtered_df.groupby('Timestamp')
            
            eps_values = np.linspace(0.1, 1.0, num=15)
            min_samples_values = np.arange(20, 60, step=5)
            combinations=list(itertools.product(eps_values,min_samples_values))
            teams=['A','B','C','D','E']

            self.conn=sqlite3.connect('Masterlist.db')
            self.c=self.conn.cursor()
            self.c.execute('''UPDATE Masterlist
                              SET X= (CASE
                                  WHEN team='A' THEN 65
                                  WHEN team='B' THEN 0
                                  WHEN team='C' THEN 7
                                  WHEN team='D' THEN 92
                                  WHEN team='E' THEN 50
                                  ELSE X
                              END), 

                                  Y= (CASE
                                  WHEN team='A' THEN 95
                                  WHEN team='B' THEN 67
                                  WHEN team='C' THEN 11
                                  WHEN team='D' THEN 81
                                  WHEN team='E' THEN 57
                                  ELSE Y
                             END)

                             WHERE team IN ('A','B','C','D','E');
                              ''')
            self.conn.commit()
            self.schedule_table=Schedule(self, ('Time', 'Team', 'X', 'Y'))
            
            for timestamp, group in grouped:
                grouped_dfs = []
                time=timestamp.time()
                date=timestamp.date()
                X = group[['X', 'Y']].to_numpy()
                
                def get_scores_and_labels(combinations,X):
                    scores = []
                    labels_list=[]

                    for i, (eps, min_sample) in enumerate(combinations):
                        dbscan = DBSCAN(eps=eps, min_samples=min_sample).fit(X)
                        labels = dbscan.labels_
                        labels_set = set(labels)
                        num_clusters = len(labels_set)
                        if -1 in labels_set:
                            num_clusters -= 1
    
                        if (num_clusters < 2) or (num_clusters > 15):
                            scores.append(-10)
                            labels_list.append('bad')
                            continue
           
           
    
                        scores.append(ss(X, labels))
                        labels_list.append(labels)
        

                    best_index = np.argmax(scores)
                    best_parameters = combinations[best_index]
                    best_score = scores[best_index]
                    best_labels = labels_list[best_index]
   
                    return {'best_epsilon': best_parameters[0],
                            'best_min_samples': best_parameters[1], 
                            'best_labels': best_labels,
                            'best_score': best_score}

                best_dict=get_scores_and_labels(combinations, X)

                group['Cluster Labels']=best_dict['best_labels']
                grouped_dfs.append(group)
                clustered_df = pd.concat(grouped_dfs)
                grouped_label=clustered_df.groupby('Cluster Labels')
                Labels=[]
                x_mean_coordinates=[]
                y_mean_coordinates=[]
                cluster_sizes=[]
                teams_count=[]
                for cluster_label, group_label in grouped_label:
                    if cluster_label==-1:
                        continue
                
                
                    Labels.append(cluster_label)
                
                    x_mean_coordinates.append(int(group_label['X'].mean()))
                    y_mean_coordinates.append(int(group_label['Y'].mean()))
                    size=len(group_label)
                    cluster_sizes.append(size)
                    teams_count.append(0)
                cluster_info_df=pd.DataFrame({'Labels':Labels,
                                              'X':x_mean_coordinates,
                                              'Y':y_mean_coordinates,
                                              'Size':cluster_sizes,
                                              'Teams already patrolling':teams_count})

            

                previous_row_team=None
                for team in teams:
                

                    if time!=datetime.time(8,0):
                        score=[]
                        self.conn=sqlite3.connect('Masterlist.db')
                        self.c=self.conn.cursor()
            
                        self.c.execute("SELECT * FROM Masterlist")
                        assigned_cluster=None
                        assigned_X=None
                        assigned_Y=None
                        if (time>=datetime.time(10,0) and time<=datetime.time(11,30)) and team=='A':
                            self.c.execute('''UPDATE Masterlist
                              SET X= (CASE

                                  WHEN team='A' THEN 65   
                                  
                                  ELSE X
                              END), 

                                  Y= (CASE
                            
                                  WHEN team='A' THEN 95
                              
                                  ELSE Y
                             END)

                             WHERE team IN ('A','B','C','D','E');
                              ''')
                            self.conn.commit()
                            #print(f'At {timestamp}, Team {team} is having a lunch break')
                            self.schedule_table.insert('', 'end', values=(timestamp, team, '-', '-'))
                            continue
                        if (time>=datetime.time(10,30) and time<=datetime.time(12,0)) and team=='B':
                            self.c.execute('''UPDATE Masterlist
                              SET X= (CASE

                                  WHEN team='B' THEN 0   
                                  
                                  ELSE X
                              END), 

                                  Y= (CASE
                            
                                  WHEN team='B' THEN 67
                              
                                  ELSE Y
                             END)

                             WHERE team IN ('A','B','C','D','E');
                              ''')
                            self.conn.commit()
                            #print(f'At {timestamp}, Team {team} is having a lunch break')
                            self.schedule_table.insert('', 'end', values=(timestamp, team, '-', '-'))
                            continue
                        if (time>=datetime.time(11,0) and time<=datetime.time(12,30)) and team=='C':
                            self.c.execute('''UPDATE Masterlist
                              SET X= (CASE

                                  WHEN team='C' THEN 7   
                                  
                                  ELSE X
                              END), 

                                  Y= (CASE
                            
                                  WHEN team='C' THEN 11
                              
                                  ELSE Y
                             END)

                             WHERE team IN ('A','B','C','D','E');
                              ''')
                            self.conn.commit()
                            #print(f'At {timestamp}, Team {team} is having a lunch break')
                            self.schedule_table.insert('', 'end', values=(timestamp, team, '-', '-'))
                            continue
                        if (time>=datetime.time(11,30) and time<=datetime.time(13,0)) and team=='D':
                            self.c.execute('''UPDATE Masterlist
                              SET X= (CASE

                                  WHEN team='D' THEN 92   
                                  
                                  ELSE X
                              END), 

                                  Y= (CASE
                            
                                  WHEN team='D' THEN 81
                              
                                  ELSE Y
                             END)

                             WHERE team IN ('A','B','C','D','E');
                              ''')
                            self.conn.commit()
                            #print(f'At {timestamp}, Team {team} is having a lunch break')
                            self.schedule_table.insert('', 'end', values=(timestamp, team, '-', '-'))
                            continue
                        if (time>=datetime.time(12,0) and time<=datetime.time(13,30)) and team=='E':
                            self.c.execute('''UPDATE Masterlist
                              SET X= (CASE

                                  WHEN team='E' THEN 50   
                                  
                                  ELSE X
                              END), 

                                  Y= (CASE
                            
                                  WHEN team='E' THEN 57
                              
                                  ELSE Y
                             END)

                             WHERE team IN ('A','B','C','D','E');
                              ''')
                            self.conn.commit()
                            #print(f'At {timestamp}, Team {team} is having a lunch break')
                            self.schedule_table.insert('', 'end', values=(timestamp, team, '-', '-'))
                            continue

                        for row in self.c.fetchall():
                            if row[2]==team and row[2]!=previous_row_team and row[5]=='Present':
                                previous_row_team=row[2]
                                for index, cluster in cluster_info_df.iterrows():
                                    if distance(cluster['X'],cluster['Y'],row[3],row[4])==0:
                                        cluster_score=cluster['Size']/1-cluster['Teams already patrolling']
                                        score.append(cluster_score)
                                    else:
                                        cluster_score=cluster['Size']/distance(cluster['X'],cluster['Y'],row[3],row[4])**2-cluster['Teams already patrolling']
                                        score.append(cluster_score)
                        
                            
                            else:
                                continue
                        self.conn.close()

                        
 
                        cluster_info_df[f'Score {team}']=score 
                    
                        max_score=max(score)
                        for index, clusterr in cluster_info_df.iterrows():
                            if clusterr[f'Score {team}']==max_score:
                                clusterr[4]+=1
                                assigned_cluster=clusterr['Labels']
                                self.conn=sqlite3.connect('Masterlist.db')
                                self.c=self.conn.cursor()
            
                                self.c.execute("SELECT * FROM Masterlist")
                            
                           

                                self.c.execute("UPDATE Masterlist SET X = ?, Y = ? WHERE team = ?",
                                    (clusterr[1], clusterr[2], team))
                                self.conn.commit()
                            
                                assigned_X=clusterr[1]
                                assigned_Y=clusterr[2]
                                
                            
                                self.conn.close()



                            else:
                                continue
                        
                        self.schedule_table.insert('', 'end', values=(timestamp, team, assigned_X, assigned_Y))

                    else:
                        continue
            if self.checkbox_var.get():
                final_time=[]
                final_team=[]
                final_X=[]
                final_Y=[]
                for child in self.schedule_table.get_children():
                    final_time.append(self.schedule_table.item(child)['values'][0])
                    final_team.append(self.schedule_table.item(child)['values'][1])
                    final_X.append(self.schedule_table.item(child)['values'][2])
                    final_Y.append(self.schedule_table.item(child)['values'][3])

                full_data = {'Time': final_time, 'Team': final_team, 'X': final_X, 'Y': final_Y}
                final_df=pd.DataFrame.from_dict(full_data)
                final_df.to_excel(f'{date} Schedule.xlsx', index=False)



        except Exception as e:
            if not self.error_displayed:
                tk.Label(self, text='No file selected!', font=('Calibri', 15)).pack(side='right', padx=20,pady=20)
                self.error_displayed=True
            else:
                pass


            

class HR(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        

        self.name=tk.Entry(self, width=30)
        self.name.grid(row=0, column=1, padx=20)
        self.id_no=tk.Entry(self, width=30)
        self.id_no.grid(row=1, column=1, padx=20)
        self.team=tk.Entry(self, width=30)
        self.team.grid(row=2, column=1, padx=20)
        self.present="Present"
        self.start_X=0
        self.start_Y=0
        self.fill_error_check=False
        self.fill_error=tk.Label(self, text='', font=('Calibri', 15))
        name_lb=tk.Label(self, text='Name').grid(row=0, column=0, padx=20)
        id_no_lb=tk.Label(self, text='ID').grid(row=1, column=0, padx=20)
        team_lb=tk.Label(self, text='Team').grid(row=2, column=0, padx=20)
        self.masterlist=None
        
        

        add_btn=tk.Button(self, text='Add', background="#085b10", 
        foreground='white', font=("Calibri", 20), command=self.add).grid(row=3, column=0, columnspan=2, padx=10, pady=10, ipadx=100)
        show_btn=tk.Button(self, text='Show Records', background="#085b10", 
        foreground='white', font=("Calibri", 20), command=self.show).grid(row=4, column=0, columnspan=2, padx=10, pady=10, ipadx=55)
        delete_btn=tk.Button(self, text='Delete', background="#085b10", 
        foreground='white', font=("Calibri", 20), command=self.delete).grid(row=5, column=0, columnspan=2, padx=10, pady=10, ipadx=70)
        update_btn=tk.Button(self, text='Update', background="#085b10", 
        foreground='white', font=("Calibri", 20), command=self.update).grid(row=6, column=0, columnspan=2, padx=10, pady=10, ipadx=70)
       
    def add(self):
        self.conn=sqlite3.connect('Masterlist.db')
        self.c=self.conn.cursor()
        
        
        '''self.c.execute("""CREATE TABLE Masterlist (
               name text,
               id_no integer,
               team text,
               X integer,
               Y integer,
               present text)""")'''
        if self.name.get()!='' and self.id_no.get()!='' and self.team.get()!='':
            self.c.execute("INSERT INTO Masterlist VALUES (:name, :id_no, :team, :X,:Y,:present)",
        
                {'name':self.name.get(),
                 'id_no':self.id_no.get(),
                 'team':self.team.get(),
                 'X':self.start_X,
                 'Y':self.start_Y,
                 'present':self.present
                })

            self.conn.commit()
            
            self.name.delete(0, END)
            self.id_no.delete(0, END)
            self.team.delete(0, END)
            if self.fill_error_check==True:
                self.fill_error.destroy()
                self.fill_error_check=False

        else:
            self.fill_error.config(text='Please fill in all required fields!')
            self.fill_error.grid(row=3, column=2, padx=10, pady=10)
            self.fill_error_check=True
        self.conn.close()
        
       
    def show(self):
        if self.masterlist is not None:
            self.masterlist.destroy()

        self.masterlist=Show_manpower(self, ('Name', 'ID', 'Team', 'X', 'Y', 'Present'))
        self.conn=sqlite3.connect('Masterlist.db')
        self.c=self.conn.cursor()
        
       
        self.c.execute("SELECT * FROM Masterlist")
        self.records=self.c.fetchall()

        
        for rec in self.records:
            
            self.masterlist.insert('', 'end', values=rec)



        

        self.conn.commit()
        self.conn.close()
    def delete(self):
        self.conn=sqlite3.connect('Masterlist.db')
        self.c=self.conn.cursor()
        
        if self.id_no.get()!='':
            self.c.execute("DELETE FROM Masterlist WHERE id_no="+self.id_no.get())
            self.conn.commit()
            self.id_no.delete(0, END)
            if self.fill_error_check==True:
                self.fill_error.destroy()
                self.fill_error_check=False
        else:
            self.fill_error.config(text='Please fill a valid ID!')
            self.fill_error.grid(row=5, column=2, padx=10, pady=10)
            self.fill_error_check=True

        self.conn.close()
        
    def update(self):
        Update("Update Database", (730,500))

 

class Update(tk.Tk):
    def __init__(self,title,size):
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')

        self.input=tk.Entry(self, width=30)
        self.input.grid(row=0, column=1, padx=20)
        self.find_btn=tk.Button(self, text='Find', background="#085b10", 
        foreground='white', font=("Calibri", 20), command=self.show_current).grid(row=1, column=0, columnspan=2, padx=10, pady=10, ipadx=100)

        self.name_edit=tk.Entry(self, width=30)
        self.name_edit.grid(row=2, column=1, padx=20)
        self.team_edit=tk.Entry(self, width=30)
        self.team_edit.grid(row=3, column=1, padx=20)
        self.fill_error_check=False
        self.fill_error=tk.Label(self, text='', font=('Calibri', 15))
        input_lb=tk.Label(self, text='ID').grid(row=0, column=0, padx=20)
        name_lb=tk.Label(self, text='Name').grid(row=2, column=0, padx=20)
        team_lb=tk.Label(self, text='Team').grid(row=3, column=0, padx=20)

        
      
        self.present_optn=tk.Button(self, text='Present',background="#085b10", 
        foreground='white', font=("Calibri", 15), command=self.mark_present)
        self.present_optn.grid(row=4, column=0, padx=10, pady=10)
        self.absent_optn=tk.Button(self, text='Absent',background="#085b10", 
        foreground='white', font=("Calibri", 15) , command=self.mark_absent)
        self.absent_optn.grid(row=4, column=1, padx=10, pady=10)

        save_btn=tk.Button(self, text='Save', background="#085b10", 
        foreground='white', font=("Calibri", 20), command=self.save_edit).grid(row=5, column=0, columnspan=2, padx=10, pady=10, ipadx=100)


        self.mainloop()
    
    def show_current(self):
        self.conn=sqlite3.connect('Masterlist.db')
        self.c=self.conn.cursor()
        
        
        current_id=self.input.get()
        if current_id!='':
            self.c.execute("SELECT * FROM Masterlist WHERE id_no=" + current_id)
            self.records=self.c.fetchall()

            for rec in self.records:
                self.name_edit.insert(0,rec[0])
                self.team_edit.insert(0,rec[2])


            self.conn.commit()
            if self.fill_error_check==True:
                self.fill_error.destroy()
                self.fill_error_check=False
        else:
            self.fill_error.config(text='Please fill in a valid entry!')
            self.fill_error.grid(row=1, column=2, padx=10, pady=10)
            self.fill_error_check=True


        self.conn.close()
    
    def mark_present(self):
        self.present="Present"
   
        self.conn=sqlite3.connect('Masterlist.db')
        self.c=self.conn.cursor()
        self.c.execute("""UPDATE Masterlist SET
        present=:present
        

        WHERE id_no=:input""",
        {'present':self.present,
            'input':self.input.get()})
        self.conn.commit()
        self.conn.close()
        self.pres_lb=tk.Label(self, text='Marked as Present').grid(row=4, column=2, padx=10, pady=10)



    def mark_absent(self):
        self.absent="Absent"
        self.conn=sqlite3.connect('Masterlist.db')
        self.c=self.conn.cursor()
        self.c.execute("""UPDATE Masterlist SET
        present=:absent
        

        WHERE id_no=:input""",
        {'absent':self.absent,
            'input':self.input.get()})
        self.conn.commit()
        self.conn.close()
        self.abs_lb=tk.Label(self, text='Marked as Absent').grid(row=4, column=2, padx=10, pady=10)
        




    def save_edit(self):
        self.conn=sqlite3.connect('Masterlist.db')
        self.c=self.conn.cursor()
        
       
        self.c.execute("""UPDATE Masterlist SET
        name=:name,
        team=:team

        WHERE id_no=:input""",
        {'name':self.name_edit.get(),
         'team':self.team_edit.get(),
         'input':self.input.get()
         })
   

        self.conn.commit()
        self.conn.close()

        self.input.delete(0, END)
        self.name_edit.delete(0, END)
        self.team_edit.delete(0, END)

class Schedule(ttk.Treeview):
    def __init__(self, parent, columns, *args, **kwargs):
        kwargs["show"] = "headings"
        super().__init__(parent, columns=columns, *args, **kwargs)
        
        
        self.set_headings(columns)
        self.pack(side='left', fill = 'both', expand = True, padx=20,pady=20)

    def set_headings(self, columns):
        for column in columns:
            self.heading(column, text=column)

class Show_manpower(ttk.Treeview):
    def __init__(self, parent, columns, *args, **kwargs):
        kwargs["show"] = "headings"
        super().__init__(parent, columns=columns, *args, **kwargs)
        
       
        self.set_headings(columns)
        self.grid(row=0, column=3, rowspan=7,columnspan=6, padx=10,pady=10)

    def set_headings(self, columns):
        for column in columns:
            self.heading(column, text=column)




App("HR Control and Deployment",(1460,1000))










