from flask import Flask, request, flash, url_for, redirect, render_template  
from flask_sqlalchemy import SQLAlchemy  
from path import add_nodes,add_edges,critical_path
from sqlalchemy.orm import relationship

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nodes.sqlite3'  
app.config['SECRET_KEY'] = "secret key"  
  
db = SQLAlchemy(app)  

# class Nodes(db.Model):
#     id=db.Column('node_id',db.Integer,primary_key = True)
#     name = db.Column(db.String(2))
#     duration = db.Column(db.Integer)

#     def __init__(self,name,duration):
#         self.name=name
#         self.duration=duration

class Nodes(db.Model):  
   id = db.Column('id', db.Integer, primary_key = True)  
   nodename = db.Column(db.String(10))  
   duration = db.Column(db.Integer)
  
   def __init__(self, nodename, duration):  
      self.nodename = nodename  
      self.duration = duration  
      
class Edges(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   edgename=db.Column(db.String(10)) #endnode
   nodeid=db.Column(db.Integer, db.ForeignKey(Nodes.id)) #startnode
   # nodes = relationship(Nodes, cascade = "all,delete", backref = "edges")

   def __init__(self,edgename,nodeid):
      self.edgename=edgename
      self.nodeid=nodeid

@app.route('/')
def cpm():
   get_nodes()
   flash('SUCCESS') 
   return render_template('success.html')

@app.route('/add', methods = ['GET', 'POST'])  
def addNode():  
   if request.method == 'POST':  
    #   if not request.form['name'] or not request.form['salary'] or not request.form['age']:  
    #      flash('Please enter all the fields', 'error')  
    #   else:  
         node=Nodes(request.form['nodename'],request.form['duration'])
        #  node=Nodes('A',2)
           
         db.session.add(node)  
         db.session.commit()  
         flash('Record was successfully added')  
         return redirect(url_for('list_nodes'))  
   print("NOT POST")
   return render_template('add_node.html')

@app.route('/addedge',methods=['GET','POST'])
def addEdge():
   if request.method=='POST':
      node_is=request.form['edge']
      edges_are=request.form.getlist("edge_keys")
      node_id=Nodes.query.with_entities(Nodes.id).filter_by(nodename=node_is).first()
      for e in edges_are:
        edge=Edges(e,node_id[0])
        db.session.add(edge)
        db.session.commit()

      flash("Edges added successfully")
      return redirect(url_for('list_edges'))
   print("NOT POST")
   return render_template('add_edges.html',nodes=Nodes.query.all())

@app.route('/list')  
def list_nodes():  
   return render_template('list_nodes.html', nodes = Nodes.query.all() )

@app.route('/listedges')
def list_edges():
   return render_template('list_edges.html',edges=Edges.query.all())

@app.route('/delete',methods=['GET','POST'])
def del_node():
   if request.method=='POST':
      if not request.form['node_name']:
        flash('Please enter the name to delete','error')
      else:
         node_id=Nodes.query.with_entities(Nodes.id).filter_by(nodename=request.form['node_name']).first()  
         end_nodes=Edges.query.filter_by(edgename=request.form['node_name']).all() #delete the edges with end edge is node
         for n in end_nodes:
            db.session.delete(n)
         
         print("NODE_ID",node_id)

         if node_id is not None:
            start_nodes=Edges.query.filter_by(nodeid=node_id[0]).all() #delete the edges with start edge is node
            for n in start_nodes:
               db.session.delete(n)
         node=Nodes.query.filter_by(nodename=request.form['node_name']).first() #deleted the node from Nodes
         if node is not None:
            db.session.delete(node)
         db.session.commit()
         flash("Record was successfully deleted")
         return redirect(url_for('list_nodes'))
   return render_template('delete_node.html')

tasks=[]
dependencies=[]
crit_path=[]
def get_nodes():
   nodes=Nodes.query.all()
   for node in nodes:
      add_nodes(tasks,node.nodename,node.duration)
   edges=Edges.query.all()
   for edge in edges:
      node1=Nodes.query.with_entities(Nodes.nodename).filter_by(id=edge.nodeid).first()
      add_edges(dependencies,node1[0],edge.edgename)
   critical_path(crit_path,dependencies,tasks)


if __name__ == '__main__':  
   y=db.create_all() 
   app.run(debug = True)  