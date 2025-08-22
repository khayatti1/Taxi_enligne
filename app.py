from flask import  Flask, render_template, request, jsonify, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.utils import secure_filename
from sqlalchemy import desc, false, true
from datetime import datetime
from sqlalchemy.orm import Session

import hashlib, os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','pdf'}  

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= "postgresql"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.secret_key = 'ZOLDYCK'

def md5_hash(data: str) -> str:
    md5_hash_object = hashlib.md5()
    md5_hash_object.update(data.encode())
    return md5_hash_object.hexdigest()

############################################---MODELS--###########################################################
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200))
    img = db.Column(db.String(200))
    type = db.Column(db.String(200), default='passager')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'img': self.img
        }

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voiture = db.Column(db.String(200))
    permis = db.Column(db.String(200))
    carte = db.Column(db.String(200))
    mat = db.Column(db.String(200))
    typev = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accepte = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('drivers', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'voiture': self.voiture,
            'permis': self.permis,
            'carte': self.carte,
            'mat': self.mat,
            'typev': self.typev,
        }

class Trajet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_conducteur = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=True)
    id_passager = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_latitude = db.Column(db.Float)
    start_longitude = db.Column(db.Float)
    end_latitude = db.Column(db.Float)
    end_longitude = db.Column(db.Float)
    conducteur_latitude = db.Column(db.Float, nullable=True)
    conducteur_longitude = db.Column(db.Float, nullable=True)
    etat = db.Column(db.Boolean, default=False)
    start_location = db.Column(db.String(255), nullable=True)
    end_location = db.Column(db.String(255), nullable=True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)

    passager = db.relationship('User', foreign_keys=[id_passager])
    conducteur = db.relationship('Driver', foreign_keys=[id_conducteur])

    def to_dict(self):
        return {
            'id': self.id,
            'id_conducteur': self.id_conducteur,
            'id_passager': self.id_passager,
            'start_latitude': self.start_latitude,
            'start_longitude': self.start_longitude,
            'end_latitude': self.end_latitude,
            'end_longitude': self.end_longitude,
            'conducteur_latitude': self.conducteur_latitude,
            'conducteur_longitude': self.conducteur_longitude,
            'etat': self.etat,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'datetime': self.datetime.strftime('%Y-%m-%d %H:%M') 
        }

with app.app_context():
    db.create_all()

############################################---INSCRIPTION--###########################################################

@app.route('/user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = md5_hash(request.form['password'])

        check_mail = User.query.filter_by(email=email).first()

        if check_mail:
            return jsonify({'error': 'Email already exist'}), 401
        
        if 'img' in request.files:
            img = request.files['img']
            if img.filename == '':
                img = None 
        else:
            return jsonify({'error': 'permis invalide'}), 401
        user = User(name=name, email=email, phone=phone, password=password)
        if img:
            img_filename = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
            user.img = img_filename
        db.session.add(user)
        db.session.commit()

        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_type'] = user.type
            session['user_phone'] = user.phone
            session['user_img'] = user.img

            return redirect(url_for('check'))
        else:
            return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/driver', methods=['POST'])
def create_driver():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        mat = request.form.get('mat')
        typev = request.form.get('typev')
        password = md5_hash(request.form.get('password'))
        if not all([name, email, phone, mat, typev, password]):
            return jsonify({'error': 'Some attributes are missing'}), 400
        img = request.files.get('img')
        voiture = request.files.get('car')
        permis = request.files.get('permis')
        carte = request.files.get('carte')

        check_mail = User.query.filter_by(email=email).first()

        if check_mail:
            return jsonify({'error': 'Email already exist'}), 401
        
        if not voiture:
            return jsonify({'error': 'voiture invalide'}), 401

        if not permis:
            return jsonify({'error': 'permis invalide'}), 401

        if not carte:
            return jsonify({'error': 'carte invalide'}), 401



        user = User(name=name, email=email, phone=phone, password=password, img=img.filename, type='conducteur')

        db.session.add(user)
        db.session.commit()

        driver = Driver(user_id=user.id, mat=mat, typev=typev)

        if img:
            img_filename = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
            user.img = img_filename

        if voiture:
            voiture_filename = secure_filename(voiture.filename)
            voiture.save(os.path.join(app.config['UPLOAD_FOLDER'], voiture_filename))
            driver.voiture = voiture_filename

        if permis:
            permis_filename = secure_filename(permis.filename)
            permis.save(os.path.join(app.config['UPLOAD_FOLDER'], permis_filename))
            driver.permis = permis_filename

        if carte:
            carte_filename = secure_filename(carte.filename)
            carte.save(os.path.join(app.config['UPLOAD_FOLDER'], carte_filename))
            driver.carte = carte_filename

        db.session.add(user)
        db.session.add(driver)
        db.session.commit()

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_type'] = user.type
        session['user_phone'] = user.phone
        session['user_img'] = user.img

        return jsonify({'success': 'Driver created successfully'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': 'Couldn\'t create your account, Try again later!'}), 500


############################################---LOGIN--###########################################################

@app.route('/auth-callback', methods=['POST'])
def loginCallback():
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form

        if 'email' not in data:
            return jsonify({'error': 'Missing email'}), 400
        
        if 'password' not in data:
            return jsonify({'error': 'Missing password'}), 400

        email = data.get('email')
        password = md5_hash(data.get('password'))

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_type'] = user.type
            session['user_phone'] = user.phone
            session['user_img'] = user.img

            return redirect(url_for('check'))
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/check')
def check():
    if 'user_id' in session:
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))

@app.route('/main')
def main():
    if 'user_id' in session:
        user_type = session.get('user_type')
        if user_type == 'admin':
            return redirect(url_for('admin'))
        elif user_type == 'passager':
            return redirect(url_for('passager'))
        elif user_type == 'conducteur':
            return redirect(url_for('conducteur'))
    return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('login.html')

############################################---ADMIN--###########################################################

@app.route('/admin/refus', methods=['POST'])
def adminRefus():
    if 'user_id' in session and session.get('user_type') == 'admin':
        user_id = session['user_id']
        data = request.form

        if 'id' not in data:
            return jsonify({'error': 'Missing parameters'}), 400
        
        d_user_id = data.get('id')

        user_to_delete = User.query.filter_by(id=d_user_id).first()
        driver_to_delete = Driver.query.filter_by(user_id=d_user_id).first()
        trajets_to_delete = Trajet.query.filter_by(id_conducteur=driver_to_delete.id).all()

        if not (user_to_delete and driver_to_delete):
            return jsonify({'error': 'Something went wrong!'}), 401
        
        try:
            for trajet in trajets_to_delete:
                db.session.delete(trajet)
            
            db.session.delete(user_to_delete)
            db.session.delete(driver_to_delete)
            db.session.commit()
            results = db.session.query(Driver, User)\
            .join(User, Driver.user_id == User.id)\
            .filter(Driver.accepte == false())\
            .all()
            drivers_with_users = []

            for driver, user in results:
                driver_dict = driver.to_dict()
                user_dict = user.to_dict()
                combined_dict = {**driver_dict, 'user': user_dict}
                drivers_with_users.append(combined_dict)

            return drivers_with_users

        except Exception as e:
            print(f"Error during deletion: {e}")
            return jsonify({'error': f'Something went wrong! {str(e)}'}), 500
    else:
        return jsonify({'error': 'You cant access this endpoint'}), 401
    

@app.route('/admin/accept', methods=['POST'])
def adminAccept():
    if 'user_id' in session and session.get('user_type') == 'admin':
        user_id = session['user_id']
        data = request.form

        if 'id' not in data:
            return jsonify({'error': 'Missing parameters'}), 400
        
        d_user_id = data.get('id')

        user_to_accept = Driver.query.filter_by(user_id=d_user_id).first()

        if not (user_to_accept):
            return jsonify({'error': 'Something went wrong!'}), 401
        
        user_to_accept.accepte = True;

        try:
            db.session.commit()

            results = db.session.query(Driver, User)\
            .join(User, Driver.user_id == User.id)\
            .filter(Driver.accepte == false())\
            .all()

            drivers_with_users = []

            for driver, user in results:
                driver_dict = driver.to_dict()
                user_dict = user.to_dict()
                combined_dict = {**driver_dict, 'user': user_dict}
                drivers_with_users.append(combined_dict)

            return drivers_with_users

        except Exception as e:
            print(f"Error during deletion: {e}")
            return jsonify({'error': f'Something went wrong! {str(e)}'}), 500
    else:
        return jsonify({'error': 'You cant access this endpoint'}), 401

@app.route('/admin')
def admin():
    if 'user_id' in session and session.get('user_type') == 'admin':
        user_id = session['user_id']
        user = User.query.get(user_id)  # Récupérez l'utilisateur actuel
        if user:
            conducteurs_inactifs = db.session.query(Driver, User)\
                .join(User, Driver.user_id == User.id)\
                .filter(Driver.accepte == False)\
                .all()
            conducteurs_actifs = Driver.query.filter_by(accepte=True).all()
            passagers = User.query.filter_by(type='passager').all()

            return render_template('admin/admin.html', user=user, conducteurs_inactifs=conducteurs_inactifs,conducteurs_actifs=conducteurs_actifs, passagers=passagers)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/nos_conducteur')
def nos_conducteur():
    if 'user_id' in session and session.get('user_type') == 'admin':
        user_id = session['user_id']
        user = User.query.get(user_id)  # Récupérez l'utilisateur actuel

        # Vérifiez si l'utilisateur existe et est bien un administrateur
        if user:
            conducteurs_inactifs = db.session.query(Driver, User)\
                .join(User, Driver.user_id == User.id)\
                .filter(Driver.accepte == False)\
                .all()
            conducteurs_actifs = Driver.query.filter_by(accepte=True).all()
            passagers = User.query.filter_by(type='passager').all()

            return render_template('admin/nos_conducteur.html', user=user, conducteurs_inactifs=conducteurs_inactifs,conducteurs_actifs=conducteurs_actifs, passagers=passagers)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route('/nos_passager')
def nos_passager():
    if 'user_id' in session and session.get('user_type') == 'admin':
        user_id = session['user_id']
        user = User.query.get(user_id)  # Récupérez l'utilisateur actuel

        # Vérifiez si l'utilisateur existe et est bien un administrateur
        if user:
            conducteurs_inactifs = db.session.query(Driver, User)\
                .join(User, Driver.user_id == User.id)\
                .filter(Driver.accepte == False)\
                .all()
            conducteurs_actifs = Driver.query.filter_by(accepte=True).all()
            passagers = User.query.filter_by(type='passager').all()

            return render_template('admin/nos_passager.html', user=user, conducteurs_inactifs=conducteurs_inactifs,conducteurs_actifs=conducteurs_actifs, passagers=passagers)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

############################################---FORM-INSCRIPTION--######################################################

@app.route('/inscription')
def inscription():
    return render_template('inscription.html')

@app.route('/incription_conducteur')
def incription_conducteur():
    return render_template('incription_conducteur.html')


############################################---PASSAGER--###########################################################

@app.route('/passager')
def passager():
    if 'user_id' in session and session.get('user_type') == 'passager':
        user_id = session['user_id']
        user = User.query.get(user_id)  
        
        if user:
            trajet = Trajet.query.filter_by(id_passager=user_id).order_by(desc(Trajet.id)).first()
            
            if trajet:
                if trajet.etat:
                    trip_status = "Accepté"
                    css_class = "text-green-500"
                else:
                    trip_status = "En Attente"
                    css_class = "text-red-500"

                return render_template('passager/passager.html', user=user, trip_status=trip_status, css_class=css_class)
            else:
                return render_template('passager/passager.html', user=user, trip_status="Aucun trajet trouvé", css_class="text-red-500")
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/save_trajet', methods=['POST'])
def save_trajet():
    try:
        data = request.get_json()
        start_latitude = data.get('start_latitude')
        start_longitude = data.get('start_longitude')
        end_latitude = data.get('end_latitude')
        end_longitude = data.get('end_longitude')
        start_location = data.get('start_location')
        end_location = data.get('end_location')
        datetime = data.get('datetime')
        user_id = session.get('user_id')

        app.logger.debug(f'Start Location received: {start_location}')
        app.logger.debug(f'End Location received: {end_location}')

        if not user_id:
            app.logger.error('Utilisateur non connecté')
            return jsonify({'success': False, 'error': 'Utilisateur non connecté'})

        if None in [start_latitude, start_longitude, end_latitude, end_longitude, start_location, end_location]:
            app.logger.error('Données manquantes')
            return jsonify({'success': False, 'error': 'Données manquantes'})

        new_trajet = Trajet(
            id_passager=user_id,
            start_latitude=start_latitude,
            start_longitude=start_longitude,
            end_latitude=end_latitude,
            end_longitude=end_longitude,
            start_location=start_location,
            end_location=end_location,
            datetime=datetime,
            id_conducteur=None 
        )
        db.session.add(new_trajet)
        db.session.commit()

        app.logger.info('Trajet enregistré avec succès')
        return jsonify({'success': True, 'trajet_id': new_trajet.id})
    
    except Exception as e:
        app.logger.error(f'Erreur lors de l\'enregistrement du trajet: {e}')
        return jsonify({'success': False, 'error': str(e)})
        flash('Aucun trajet trouvé ou accès non autorisé', 'error')
    return redirect(url_for('home'))

@app.route('/details')
def details():
    if 'user_id' in session and session.get('user_type') == 'passager':
        user_id = session['user_id']
        trajet = Trajet.query.filter_by(id_passager=user_id).order_by(Trajet.id.desc()).first()
        if trajet:
            return redirect(url_for('trajet_reserve', trajet_id=trajet.id))
        else:
            return redirect(url_for('choisir_trajet'))

@app.route('/choisir_trajet')
def choisir_trajet():
    return render_template('passager/choisir_trajet.html')

@app.route('/trajetReserver/<int:trajet_id>')
def trajet_reserve(trajet_id):
    if 'user_id' in session and session.get('user_type') == 'passager':
        trajet = Trajet.query.get(trajet_id)
        if trajet:
            user = User.query.get(trajet.id_passager)
            conducteur = None

            if trajet.id_conducteur:
                driver = Driver.query.get(trajet.id_conducteur)
                if driver:
                    conducteur = {
                        'name': driver.user.name,
                        'email': driver.user.email,
                        'phone': driver.user.phone,
                        'voiture': driver.voiture,
                        'typev': driver.typev,
                    }

            return render_template('passager/trajetReserver.html', user=user, trajet=trajet, conducteur=conducteur)

    flash('Trajet non trouvé ou accès non autorisé', 'error')
    return redirect(url_for('home'))



############################################---DRIVER--###########################################################


@app.route('/conducteur')
def conducteur():
    if 'user_id' in session and session.get('user_type') == 'conducteur':
        current_driver = Driver.query.filter_by(user_id=session['user_id']).first()
        if current_driver and current_driver.accepte:
            user_id = session['user_id']
            user = User.query.get(user_id)

            if user:
                trips_with_passengers = db.session.query(Trajet, User, Driver) \
                    .join(User, Trajet.id_passager == User.id) \
                    .outerjoin(Driver, Trajet.id_conducteur == Driver.id) \
                    .filter(Trajet.etat == False) \
                    .all()

                return render_template('conducteur/conducteur.html', user=user, current_driver=current_driver, trips_with_passengers=trips_with_passengers)
            else:
                return redirect(url_for('home'))
        else:
            return render_template('conducteur/f_conducteur.html')
    else:
        return redirect(url_for('home'))

@app.route('/trajetok/<int:trajet_id>')
def trajetok(trajet_id):
    trajet = Trajet.query.get(trajet_id)
    if trajet:
        passager = User.query.get(trajet.id_passager)
        
        if passager:
            return render_template('conducteur/trajetok.html', trajet=trajet, passager=passager)
        else:
            flash('Passager non trouvé pour ce trajet', 'error')
            return redirect(url_for('home'))
    else:
        flash('Trajet non trouvé ou accès non autorisé', 'error')
        return redirect(url_for('home'))


@app.route('/trips_acceptes')
def trips_acceptes():
    if 'user_id' in session and session.get('user_type') == 'conducteur':
        current_driver = Driver.query.filter_by(user_id=session['user_id']).first()
        if current_driver.accepte:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            if user:
                print(f"Current Driver ID: {current_driver.id}")
                print(f"User ID: {user_id}")
                trips_with_passengers = db.session.query(Trajet, User) \
                    .join(User, Trajet.id_passager == User.id) \
                    .filter(Trajet.id_conducteur == current_driver.id, Trajet.etat == True) \
                    .all()

                for trajet, passager in trips_with_passengers:
                    print(f"Trajet ID: {trajet.id}, Passager: {passager.name}")

                return render_template('conducteur/trips_acceptes.html', user=user, trips_with_passengers=trips_with_passengers)
            else:
                return redirect(url_for('home'))
        else:
            return render_template('conducteur/f_conducteur.html')
    else:
        return redirect(url_for('home'))

@app.route('/conducteur-info')
def conducteur_info():
    if 'user_id' in session and session.get('user_type') == 'conducteur':
        current_driver = Driver.query.filter_by(user_id = session['user_id']).first();
        print(session)
        print(current_driver)
        return render_template('conducteur/info_conducteur.html', user = session, driver= current_driver);
    else:
        return redirect(url_for('home'))
        
@app.route('/login')
def login():
    return render_template('login.html')
    

@app.route('/detailstrajet/<int:trajet_id>')
def detailstrajet(trajet_id):
    if 'user_id' in session and session.get('user_type') == 'conducteur':
        user_id = session['user_id']
        app.logger.debug(f"Utilisateur ID: {user_id}")
        current_driver = Driver.query.filter_by(user_id=user_id).first()
        if current_driver:
            app.logger.debug(f"Conducteur trouvé: {current_driver.id}")
            trajet = Trajet.query.filter_by(id=trajet_id, id_conducteur=current_driver.id).first()
            if trajet:
                app.logger.debug(f"Trajet trouvé: {trajet.id}")
                return jsonify({
                    'success': True,
                    'trajet_id': trajet.id,
                })
            else:
                app.logger.info(f"Aucun trajet trouvé avec l'ID {trajet_id} pour ce conducteur")
                return jsonify({
                    'success': False,
                    'error': f"Aucun trajet trouvé avec l'ID {trajet_id} pour ce conducteur"
                }), 404 

        else:
            app.logger.error("Conducteur non trouvé")
            return jsonify({
                'success': False,
                'error': 'Conducteur non trouvé'
            }), 404  
    else:
        flash('Accès non autorisé', 'error')
        return jsonify({
            'success': False,
            'error': 'Accès non autorisé'
        }), 403  

@app.route('/update_route', methods=['POST'])
def update_route():
    data = request.json
    trip_id = data.get('trip_id')
    new_etat = data.get('new_etat')
    id_conducteur = data.get('id_conducteur')

    print(f"Data received: {data}")
    print(f"Trip ID: {trip_id}, New Etat: {new_etat}, ID Conducteur: {id_conducteur}")

    if not trip_id or not id_conducteur:
        return jsonify({'error': 'Données incomplètes ou incorrectes'}), 400

    trajet = Trajet.query.get(trip_id)
    if not trajet:
        return jsonify({'error': 'ID du trajet invalide'}), 404

    conducteur = Driver.query.get(id_conducteur)
    if not conducteur:
        return jsonify({'error': 'Conducteur non trouvé'}), 404

    if not new_etat:
        new_etat = True

    trajet.etat = new_etat
    trajet.id_conducteur = id_conducteur

    try:
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
