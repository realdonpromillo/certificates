from flask import jsonify, request, url_for, abort, g, make_response
from flask_login import current_user
from OpenSSL import crypto
from datetime import datetime
import base64
from app import db
from app.models import User, Certificate
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request

# Eigenentwicklung
@bp.route('/generate_csr', methods=['POST'])
@token_auth.login_required
def generate_csr():
    if not request.json:
        return bad_request('Invalid request data')

    # Get data from request
    data = request.json
    country = data.get('country', "CH")
    state = data.get('state', "Bern")
    locality = data.get('locality', "Bern")
    organization = data.get('organization')
    organizational_unit = data.get('organizational_unit', '')
    common_name = data.get('common_name')
    subject_alternative_name = data.get('subject_alternative_name', [])

    # Check if common_name is present
    if not common_name:
        return bad_request('Common name is required')

    # Check if country is valid
    if not country or len(country) != 2:
        return bad_request('Invalid Country')

    # Check if common name has less than 64 characters
    if len(common_name) > 64:
        return bad_request('Common name must be 64 characters or fewer')

    # Check if common name has less than 64 characters
    if len(organization) > 64:
        return bad_request('organization must be 64 characters or fewer')

    # Check if CSR with common name already exists
    existing_csr = Certificate.query.filter_by(cn=common_name).first()
    if existing_csr:
        return bad_request(f"A certificate with common name '{common_name}' already exists.")

    #Create Keypair
    keypair = crypto.PKey()
    keypair.generate_key(crypto.TYPE_RSA, 2048)

    # Create a certificate request
    req = crypto.X509Req()
    req.get_subject().CN = common_name
    req.get_subject().C = country
    req.get_subject().ST = state
    req.get_subject().L = locality
    req.get_subject().O = organization
    # Check if organizational unit is present
    if organizational_unit:
        req.get_subject().OU = organizational_unit
    x509_extensions = []
    # Check if subject alternative name is present and add it to the CSR
    for san in subject_alternative_name:
        x509_extensions.append(crypto.X509Extension("subjectAltName".encode(), False, f"DNS:{san}".encode()))

    # Add extensions to CSR
    req.add_extensions(x509_extensions)
    req.set_pubkey(keypair)
    req.sign(keypair, "sha256")

    # Dump the keypair and CSR
    key = crypto.dump_privatekey(crypto.FILETYPE_PEM, keypair)
    csr = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)

    certificate = Certificate(csr=csr, author=g.user, cn=common_name, organization=organization, key=key)
    db.session.add(certificate)
    db.session.commit()

    # Return the CSR and the keypair
    return jsonify({
        'status': 'success',
        'data': {
            'common_name': common_name,
            'csr': csr.decode('utf-8'),
            'key': key.decode('utf-8'),
        }
    })

# Übernommen aus den Beispielen von Miguel Grinberg
# Eigenentwicklung user_id = g.user.id
@bp.route('/certificates', methods=['GET'])
@token_auth.login_required
def get_certificates():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    user_certificates = Certificate.query.filter_by(user_id=g.user.id).order_by(Certificate.id.desc())
    certificates = user_certificates.paginate(page=page, per_page=per_page, error_out=False)
    data = {
        'items': [cert.to_dict() for cert in certificates.items],
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': certificates.pages,
            'total_items': certificates.total
        },
        '_links': {
            'self': url_for('api.get_certificates', page=page, per_page=per_page),
            'next': url_for('api.get_certificates', page=certificates.next_num, per_page=per_page) if certificates.has_next else None,
            'prev': url_for('api.get_certificates', page=certificates.prev_num, per_page=per_page) if certificates.has_prev else None
        }
    }
    return jsonify(data)

# Eigenentwicklung
@bp.route('/download/key/<cn>', methods=['GET'])
@token_auth.login_required
def get_certificate_key(cn):
    # Get corresponding key from database
    certificate = Certificate.query.filter_by(cn=cn, user_id=g.user.id).first_or_404()
    # Return the key
    return jsonify({
        'key': certificate.key.decode(),
        '_links': {
            'self': url_for('api.get_certificate_key', cn=cn)
        }
    })

# Eigenentwicklung
@bp.route('/download/csr/<cn>', methods=['GET'])
@token_auth.login_required
def get_certificate_csr(cn):
    # Get corresponding CSR from database
    certificate = Certificate.query.filter_by(cn=cn, user_id=g.user.id).first_or_404()
    # Return the CSR
    return jsonify({
        'csr': certificate.csr.decode(),
        '_links': {
            'self': url_for('api.get_certificate_csr', cn=cn)
        }
    })

# Eigenentwicklung
@bp.route('/download/pfx/<cn>', methods=['GET'])
@token_auth.login_required
def download_pfx(cn):
    # Get corresponding PFX from database
    cert = Certificate.query.filter_by(cn=cn, user_id=g.user.id).first_or_404()

    # Check if PFX is present
    if not cert.pfx:
        return bad_request('No PFX file found for this certificate.')

    # Return the PFX
    pfx_data_b64 = base64.b64encode(cert.pfx).decode('utf-8')

    return jsonify({
        'status': 'success',
        'data': {
            'pfx': pfx_data_b64,
        }
    })

# Eigenentwicklung
@bp.route('/convert_certificate', methods=['POST'])
def convert_certificate():
    # Check if request is valid
    if not request.json:
        return bad_request('Invalid request data')

    # Get data from request
    data = request.json
    private_key = data.get('private_key')
    public_key = data.get('public_key')
    passphrase = data.get('passphrase')

    # Check if required fields are present
    if not all([private_key, public_key, passphrase]):
       return bad_request('Missing required fields')
    
    # Convert certificate and private key to PFX
    try:
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key)
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, public_key)
        pfx = crypto.PKCS12()
        pfx.set_privatekey(pkey)
        pfx.set_certificate(cert)
        pfxdata = pfx.export(passphrase=passphrase)
        # Convert pfx_data to a Base64-encoded string
        pfx_data_b64 = base64.b64encode(pfxdata).decode('utf-8')
    # Return error if conversion fails
    except Exception as e:
        return bad_request(f'Invalid certificate or private key: {e}')
    
    # Return the PFX
    return jsonify({
        'status': 'success',
        'data': {
            'pfx': pfx_data_b64,
        }
    })

# Eigenentwicklung
@bp.route('/download/pfx', methods=['POST'])
@token_auth.login_required
def download_pfx_from_cert():
    # Check if request is valid
    if not request.json:
        return bad_request('Invalid request data')
    
    # Get data from request
    data = request.json
    cn = data.get('cn')
    certificate = data.get('certificate')
    passphrase = data.get('passphrase')

    # Check if key exists in database
    existing_key = Certificate.query.filter_by(cn=cn, user_id=g.user.id).first()
    private_key = existing_key.key
    # Return error if key does not exist
    if not existing_key:
        return bad_request('The Private Key for the Common Name in the CSR does not exist in the database')

    # Convert certificate and private key to PFX
    try:
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key)
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
        pfx = crypto.PKCS12()
        pfx.set_privatekey(pkey)
        pfx.set_certificate(cert)
        pfx_data = pfx.export(passphrase=passphrase)
        existing_key.pfx = pfx_data
        db.session.commit()
        # Convert pfx_data to a Base64-encoded string
        pfx_data_b64 = base64.b64encode(pfx_data).decode('utf-8')

    # Return error if conversion fails
    except Exception as e:
        return bad_request(f'Invalid certificate or private key: {e}')

    # Return the PFX
    return jsonify({
        'status': 'success',
        'data': {
            'pfx': pfx_data_b64,
        }
    })