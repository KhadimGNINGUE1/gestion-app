#Importation
from flask import Flask, render_template, url_for, request, flash,redirect, session
import psycopg2 as psy
import datetime

#Création de l'application avec la variable app
app = Flask (__name__)
app.secret_key = "message"

def connectionDB():
    try:
        #connection a la base de donnee
        connection=psy.connect(host= "localhost",
                                database="GestionApprenantSA",
                                user="postgres",
                                password="gningue1991",
                                port ="5432"
                            )
        return connection
    except (Exception) as error:
        print(" Probléme de connection au serveur ",error)
con=connectionDB()
curseur=con.cursor()
#@app.route permet de préciser à quelle adresse ce qui suit va s’appliquer
@app.route('/page_accueil') #demande de la page d'accueil
def accueil(): #Permet d'ajouter des méta-données:information supplémentaire pour configurer la fonction
    return render_template('pages/accueil.html')

#---------------------------------- Insérer un nouveau apprenant ---------------------------------------------
@app.route('/formulaire', methods=['GET', 'POST'])
def formulaire():
    curseur.execute("SELECT id_promo, nom_promo FROM promotion")
    apprenant=curseur.fetchall()
    curseur.execute("SELECT apprenant.email FROM apprenant")
    ver_email=curseur.fetchall()
    if request.method == "POST":
        details = request.form
        nom_app = details['nom_ap']
        prenom_app = details['prenom_ap']
        email_app = details['email']
        date_naissance = details['date']
        requete_liste_matricule = "SELECT max(id_ap) FROM apprenant"
        sexe = details['sexe']
        idpromo = int(details['promo'])
        #Gérer la matricule par la base de données
        curseur.execute(requete_liste_matricule)
        result_matricule = curseur.fetchall()
        for mat in result_matricule:                
            matricule=mat[0]

        if matricule == None:
            num=1
            val='-'+str(num)+'-'
            sa = "SA"+val+"Code"
        else:
            num=matricule+1
            val='-'+str(num)+'-'
            sa="SA"+val+"Code"
        #Verification de l'email si l'apprenant existe ou pas
        control_email = False
        for l in ver_email:
            if l[0].lower()== email_app.lower():
                control_email = True
                break
        if control_email == True:
            flash('L\'apprenant existe déja dans la base')
            return render_template('pages/formulaire.html', ap=apprenant, em=ver_email)
        else:
            requete_ajouter_ap="INSERT INTO apprenant(nom_ap,prenom_ap,email,date_naissance,matricule,sexe,id_promo) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            curseur.execute(requete_ajouter_ap,(nom_app, prenom_app, email_app, date_naissance, sa, sexe, idpromo ))
            con.commit()
            flash('Apprenant ajouté avec succés!')
            return render_template('pages/formulaire.html', ap=apprenant, em=ver_email)
    return render_template('pages/formulaire.html', ap=apprenant, em=ver_email)

#---------------------------------Insérer nouveau référent --------------------------------------------
@app.route('/nouveau_ref', methods=['GET', 'POST'])
def nouveau_ref():
    if request.method == "POST":
        flash('Insertion réussit')
        details = request.form
        nom_ref = details['nom']
        requete_ajouter_ref="INSERT INTO referentiel(nom_ref) VALUES (%s)"
        curseur.execute(requete_ajouter_ref,(nom_ref,))
        con.commit()
    return render_template('pages/nouveau_ref.html')
#------------------------------------------Insérer nouveau promo --------------------------------------
@app.route('/nouveau_promo', methods=['GET', 'POST'])
def nouveau_promo():
    #Selection des promos
    curseur.execute("SELECT id_ref, nom_ref FROM referentiel")
    promos = curseur.fetchall()
    if request.method == "POST":
        flash('Insertion réussit')
        details = request.form
        nom_promo = details['nom']
        datedebut = details['debut']
        datefin = details['fin']
        idref = int(details['referent'])
        requete_ajouter_promo="INSERT INTO promotion(nom_promo,date_deb,date_fin, id_ref) VALUES (%s,%s,%s,%s)"
        curseur.execute(requete_ajouter_promo,(nom_promo, datedebut, datefin,idref))
        con.commit()
    return render_template('pages/nouveau_promo.html',p = promos)

#Page mére hérité par les autres pages
@app.route('/nav')
def nav():
    return render_template('partials/_nav.html')

#---------------------------------------- Modifier un apprenant ------------------------------------------
@app.route('/modification', methods=['GET', 'POST'])
def modification():
    curseur.execute("select apprenant.id_ap, apprenant.nom_ap, apprenant.prenom_ap, apprenant.email, apprenant.date_naissance, apprenant.matricule, apprenant.sexe, apprenant.statut, promotion.nom_promo from apprenant, promotion where apprenant.id_promo = promotion.id_promo AND statut='Inscrit'")
    lister = curseur.fetchall()
    
    curseur.execute("SELECT id_promo ,nom_promo FROM promotion")
    lister1 = curseur.fetchall()
    
    if request.method == "POST":
        flash('Modification réussit')
        details = request.form
        id_ap = details['id_ap']
        nom_app = details['nom_ap']
        prenom_app = details['prenom_ap']
        email_app = details['email']
        date_naissance = details['date']
        sexe = details['sexe']
        statut = details['statut']
        id_promo = int(details['promo'])
        curseur.execute("""
               UPDATE apprenant
               SET nom_ap=%s, prenom_ap=%s, email=%s, date_naissance=%s, sexe=%s, statut=%s, id_promo=%s
               WHERE id_ap=%s
            """, (nom_app, prenom_app, email_app, date_naissance, sexe, statut, id_promo,id_ap))
        con.commit()
        curseur.execute("select apprenant.id_ap, apprenant.nom_ap, apprenant.prenom_ap, apprenant.email, apprenant.date_naissance, apprenant.matricule, apprenant.sexe, apprenant.statut, promotion.nom_promo from apprenant, promotion where apprenant.id_promo = promotion.id_promo")
        lister2 = curseur.fetchall()
        return render_template('pages/modifier.html', l=lister2, l1=lister1)
    return render_template('pages/modifier.html', l=lister, l1=lister1)   #fonction qui permet de retourner un template
#------------------------------------  Annulation  ---------------------------------------
@app.route('/annulation', methods = ['GET','POST'])
def annulation():
    curseur.execute("""select apprenant.id_ap, apprenant.nom_ap, apprenant.prenom_ap,
     apprenant.email, apprenant.date_naissance, apprenant.matricule, apprenant.sexe,
     apprenant.statut, promotion.nom_promo from apprenant,
     promotion where apprenant.id_promo = promotion.id_promo AND statut= 'Inscrit'""")
    lister = curseur.fetchall()
    return render_template('pages/annuler.html', l=lister)

@app.route('/annulation&<string:id_annul>', methods = ['POST','GET'])
def annuler(id_annul):
    curseur.execute(" UPDATE apprenant SET  statut='Annuler' WHERE id_ap=%s", (id_annul,))
    con.commit()
    return redirect(url_for('listerannule'))

@app.route('/listerannule',methods=['POST','GET'])
def listerannule(): 
    curseur.execute("""SELECT apprenant.id_ap, apprenant.nom_ap,apprenant.prenom_ap,apprenant.email,apprenant.date_naissance,apprenant.matricule,apprenant.sexe,apprenant.statut,
    promotion.nom_promo FROM apprenant, 
    promotion where apprenant.id_promo=promotion.id_promo AND apprenant.statut= 'Annuler' """)
    lister=curseur.fetchall()
    return render_template('pages/listeannuler.html', l=lister)

#----------------------------------- Suspendre un apprenant -------------------------------------------
 
@app.route('/suspension', methods = ['GET','POST'])
def suspension():
    curseur.execute("""select apprenant.id_ap, apprenant.nom_ap, apprenant.prenom_ap,
     apprenant.email, apprenant.date_naissance, apprenant.matricule, apprenant.sexe,
     apprenant.statut, promotion.nom_promo from apprenant,
     promotion where apprenant.id_promo = promotion.id_promo AND statut= 'Inscrit'""")
    lister = curseur.fetchall()
    return render_template('pages/suspendre.html', l=lister)

@app.route('/suspension&<string:id_suspendu>', methods = ['POST','GET'])
def suspendre(id_suspendu):
    curseur.execute(" UPDATE apprenant SET  statut='Suspendu' WHERE id_ap=%s", (id_suspendu,))
    con.commit()
    return redirect(url_for('listersuspendre'))

@app.route('/listersuspendre',methods=['POST','GET'])
def listersuspendre(): 
    curseur.execute("""SELECT apprenant.id_ap, apprenant.nom_ap,apprenant.prenom_ap,apprenant.email,apprenant.date_naissance,apprenant.matricule,apprenant.sexe,apprenant.statut,
    promotion.nom_promo FROM apprenant, 
    promotion where apprenant.id_promo=promotion.id_promo AND apprenant.statut= 'Suspendu' """)
    lister=curseur.fetchall()
    return render_template('pages/listesuspendre.html', l=lister)

#---------------------------------- Réinscrire un apprenant ------------------------------------------


@app.route('/reinscrire&<string:id_reinscrit>', methods = ['GET'])
def reinscrire(id_reinscrit):
        curseur.execute("UPDATE apprenant SET statut='Inscrit' WHERE id_ap=%s", (id_reinscrit,))
        con.commit()
        return redirect(url_for('modification'))

#------------------------------------ Modifier un référentiel ------------------------------------------ 
@app.route('/modifier_ref', methods=['GET','POST'])
def modifier_ref():
    curseur.execute("SELECT * FROM referentiel")
    lister = curseur.fetchall()
    if request.method == "POST":
        flash('Modification réussit')
        details = request.form
        id_ref = details['id_ref']
        nom_ref = details['nom']
        curseur.execute("""
               UPDATE referentiel
               SET nom_ref=%s
               WHERE id_ref=%s
            """, (nom_ref,id_ref))
        con.commit()
        curseur.execute("SELECT * FROM referentiel")
        lister1 = curseur.fetchall()
        return render_template('pages/modifier_ref.html', l=lister1)
    return render_template('pages/modifier_ref.html', l=lister)

#-------------------------------------- Modifier un promo -------------------------------------------
@app.route('/modifier_promo', methods=['GET','POST'])
def modifier_promo():
    curseur.execute("select promotion.id_promo, promotion.nom_promo, promotion.date_deb, promotion.date_fin, referentiel.nom_ref from promotion, referentiel where promotion.id_ref = referentiel.id_ref")
    lister = curseur.fetchall()
    
    curseur.execute("SELECT id_ref ,nom_ref FROM referentiel")
    promos = curseur.fetchall()
    if request.method == "POST":
        flash('Modification réussit')
        details = request.form
        id_promo = details['id_promo']
        nom_promo = details['nom_promo']
        debut = details['debut']
        fin = details['fin']
        id_ref = int(details['referent'])
        curseur.execute("""
               UPDATE promotion
               SET nom_promo=%s, date_deb=%s, date_fin=%s, id_ref=%s
               WHERE id_promo=%s
            """, (nom_promo, debut, fin, id_ref,id_promo))
        con.commit()
        curseur.execute("select promotion.id_promo, promotion.nom_promo, promotion.date_deb, promotion.date_fin, referentiel.nom_ref from promotion, referentiel where promotion.id_ref = referentiel.id_ref")
        lister1 = curseur.fetchall()
        return render_template('pages/modifier_promo.html', l=lister1, p=promos)
    return render_template('pages/modifier_promo.html', l=lister, p=promos)

#------------------------------------- Lister les promotions ----------------------------------------
@app.route('/lister_promo', methods=['GET', 'POST'])
def lister_promo():
    curseur.execute("SELECT * FROM promotion")
    lister = curseur.fetchall()
    return render_template('pages/lister.html', l=lister)


#------------------- Lister les apprenants par promotion ----------- 

@app.route('/liste&<string:id_liste>', methods = ['GET'])
def liste(id_liste):
       
        curseur.execute("""SELECT apprenant.id_ap, apprenant.nom_ap,apprenant.prenom_ap,apprenant.email,apprenant.date_naissance,apprenant.matricule,apprenant.sexe,apprenant.statut
         FROM apprenant 
         WHERE apprenant.id_promo=%s""", (id_liste))
        lister = curseur.fetchall()
        con.commit()
        return render_template('pages/listepromo.html',l=lister)


#-------------------------------- Gérer les erreurs avec 404 ------------------------------------------
@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

#Connection avec le login et le mot de passe

@app.route('/')
def index():
    return render_template('pages/index.html')

@app.route('/', methods= ['GET','POST'])
def identification():
    details = request.form
    username = details['nom_ap']
    password = details['prenom_ap']
    curseur.execute("SELECT * FROM utilisateur WHERE username='" + username + "' and password ='" + password + "'")
    data = curseur.fetchone()
    if data is None:
        return "Username or Password incorrecte"
    else:
        flash('Vous êtes connectés à l\'application')
        return render_template('pages/accueil.html')
#Exécution de l'application avec run()
if (__name__) == '__main__':
    app.run(debug=True, port=3000)   #acivation du serveur directement pas besoin de redémarrer l'app