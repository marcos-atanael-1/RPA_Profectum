from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import subprocess
import threading
import os
from pathlib import Path
import sqlite3
import secrets
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rpa-profectum-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rpa_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

# Modelos do banco de dados
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    reset_token = db.Column(db.String(100))
    reset_token_expires = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        self.reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def is_admin(self):
        return self.role == 'admin'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(500))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default_value=None):
        setting = SystemSettings.query.filter_by(key=key).first()
        return setting.value if setting else default_value
    
    @staticmethod
    def set_setting(key, value, description=None, user_id=None):
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_by = user_id
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(
                key=key,
                value=value,
                description=description,
                updated_by=user_id
            )
            db.session.add(setting)
        db.session.commit()
        return setting

class RecebimentoNF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_compra = db.Column(db.String(100), nullable=False)
    nota_fiscal = db.Column(db.String(100), nullable=False)
    chave_acesso = db.Column(db.String(44), nullable=False)  # Chave NFe tem 44 caracteres
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pendente')  # pendente, processado, erro
    error_message = db.Column(db.Text)  # Mensagem de erro caso ocorra
    
    creator = db.relationship('User', backref=db.backref('recebimentos_nf', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'pedido_compra': self.pedido_compra,
            'nota_fiscal': self.nota_fiscal,
            'chave_acesso': self.chave_acesso,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None,
            'status': self.status,
            'error_message': self.error_message
        }

class BotExecution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # running, completed, failed, stopped
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Float)  # em segundos
    parameters = db.Column(db.Text)  # JSON string
    result = db.Column(db.Text)
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bot_name': self.bot_name,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'parameters': self.parameters,
            'result': self.result,
            'error_message': self.error_message
        }

class BotLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.Integer, db.ForeignKey('bot_execution.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    level = db.Column(db.String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(100))  # qual módulo gerou o log
    
    execution = db.relationship('BotExecution', backref=db.backref('logs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'module': self.module
        }

# Configuração dos bots disponíveis
AVAILABLE_BOTS = {
    'sic_full': {
        'name': 'SIC - Processo Completo',
        'description': 'Login no SIC + Acesso ao módulo contábil/fiscal',
        'script': 'entrada-nf/bot.py',
        'estimated_duration': 300  # segundos
    },
    'sic_login': {
        'name': 'SIC - Apenas Login',
        'description': 'Realiza apenas o login no sistema SIC',
        'script': 'entrada-nf/Sic_Login.py',
        'estimated_duration': 60
    },
    'sic_inserir_nfs': {
        'name': 'SIC - Inserir NFs Pendentes',
        'description': 'Busca todas as NFs com status pendente no banco e insere no sistema SIC',
        'script': 'entrada-nf/Sic_Inserir_NF.py',
        'estimated_duration': 180
    },
    'rm_login': {
        'name': 'RM - Login',
        'description': 'Realiza login no sistema TOTVS RM',
        'script': 'entrada-nf/RM_Login.py',
        'estimated_duration': 60
    },
    'consulta_nfe': {
        'name': 'Consulta NFe',
        'description': 'Consulta nota fiscal eletrônica via API',
        'script': 'entrada-nf/Consulta_nfe.py',
        'estimated_duration': 30
    }
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and user.check_password(password) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Página de cadastro de usuários (apenas admins)"""
    if not current_user.is_admin():
        flash('Acesso negado. Apenas administradores podem cadastrar usuários.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'user')
        
        # Validações
        if not all([username, email, password, full_name]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('auth/register.html')
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('E-mail já está em uso.', 'error')
            return render_template('auth/register.html')
        
        # Criar novo usuário
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Usuário {username} cadastrado com sucesso!', 'success')
        return redirect(url_for('users_management'))
    
    return render_template('auth/register.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Solicitar reset de senha"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Por favor, digite seu e-mail.', 'error')
            return render_template('auth/reset_request.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.is_active:
            token = user.generate_reset_token()
            db.session.commit()
            
            # Aqui você implementaria o envio de e-mail
            # Por enquanto, vamos mostrar o token na tela (apenas para desenvolvimento)
            flash(f'Token de reset gerado: {token} (válido por 1 hora)', 'info')
            return redirect(url_for('reset_password_with_token', token=token))
        else:
            flash('E-mail não encontrado.', 'error')
    
    return render_template('auth/reset_request.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    """Reset de senha com token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        flash('Token inválido ou expirado.', 'error')
        return redirect(url_for('reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        flash('Senha alterada com sucesso! Faça login com sua nova senha.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_password.html', token=token)

@app.route('/users')
@login_required
def users_management():
    """Página de gerenciamento de usuários (apenas admins)"""
    if not current_user.is_admin():
        flash('Acesso negado. Apenas administradores podem gerenciar usuários.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/users.html', users=users)

@app.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """Ativar/desativar usuário"""
    if not current_user.is_admin():
        return jsonify({'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Você não pode desativar sua própria conta'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'ativado' if user.is_active else 'desativado'
    return jsonify({'message': f'Usuário {user.username} {status} com sucesso'})

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Excluir usuário"""
    if not current_user.is_admin():
        return jsonify({'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Você não pode excluir sua própria conta'}), 400
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': f'Usuário {username} excluído com sucesso'})

@app.route('/settings')
@login_required
def settings():
    if not current_user.is_admin():
        flash('Acesso negado. Apenas administradores podem acessar as configurações.', 'error')
        return redirect(url_for('dashboard'))
    
    # Buscar configurações atuais
    current_settings = {
        'primary_color': SystemSettings.get_setting('primary_color', '#2563eb'),
        'logo_url': SystemSettings.get_setting('logo_url', ''),
        'logo_type': SystemSettings.get_setting('logo_type', 'icon'),  # icon, image, url
        'system_name': SystemSettings.get_setting('system_name', 'RPA Profectum'),
        # Configurações de login
        'login_bg_type': SystemSettings.get_setting('login_bg_type', 'color'),
        'login_bg_color': SystemSettings.get_setting('login_bg_color', '#f8fafc'),
        'login_gradient_color1': SystemSettings.get_setting('login_gradient_color1', '#2563eb'),
        'login_gradient_color2': SystemSettings.get_setting('login_gradient_color2', '#1d4ed8'),
        'login_bg_image_url': SystemSettings.get_setting('login_bg_image_url', ''),
        'login_height': SystemSettings.get_setting('login_height', 'normal'),
        'login_title': SystemSettings.get_setting('login_title', 'Bem-vindo de volta!'),
    }
    
    return render_template('settings.html', settings=current_settings)

@app.route('/settings', methods=['POST'])
@login_required
def update_settings():
    if not current_user.is_admin():
        flash('Acesso negado. Apenas administradores podem modificar as configurações.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        settings_type = request.form.get('settings_type', 'system')
        
        if settings_type == 'login':
            # Configurações de login
            SystemSettings.set_setting('login_bg_type', request.form.get('login_bg_type', 'color'), 'Tipo de fundo da página de login', current_user.id)
            SystemSettings.set_setting('login_bg_color', request.form.get('login_bg_color', '#f8fafc'), 'Cor de fundo da página de login', current_user.id)
            SystemSettings.set_setting('login_gradient_color1', request.form.get('login_gradient_color1', '#2563eb'), 'Primeira cor do gradiente de login', current_user.id)
            SystemSettings.set_setting('login_gradient_color2', request.form.get('login_gradient_color2', '#1d4ed8'), 'Segunda cor do gradiente de login', current_user.id)
            SystemSettings.set_setting('login_bg_image_url', request.form.get('login_bg_image_url', ''), 'URL da imagem de fundo do login', current_user.id)
            SystemSettings.set_setting('login_height', request.form.get('login_height', 'normal'), 'Altura da página de login', current_user.id)
            SystemSettings.set_setting('login_title', request.form.get('login_title', 'Bem-vindo de volta!'), 'Título da página de login', current_user.id)
            flash('Configurações de login atualizadas com sucesso!', 'success')
        else:
            # Configurações do sistema
            primary_color = request.form.get('primary_color', '#2563eb')
            SystemSettings.set_setting('primary_color', primary_color, 'Cor primária do sistema', current_user.id)
            
            system_name = request.form.get('system_name', 'RPA Profectum')
            SystemSettings.set_setting('system_name', system_name, 'Nome do sistema', current_user.id)
            
            logo_type = request.form.get('logo_type', 'icon')
            SystemSettings.set_setting('logo_type', logo_type, 'Tipo de logo (icon/image/url)', current_user.id)
            
            if logo_type in ['image', 'url']:
                logo_url = request.form.get('logo_url', '')
                SystemSettings.set_setting('logo_url', logo_url, 'URL da logo personalizada', current_user.id)
            
            flash('Configurações do sistema atualizadas com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao atualizar configurações: {str(e)}', 'error')
    
    return redirect(url_for('settings'))

@app.route('/')
@login_required
def dashboard():
    """Dashboard principal com estatísticas"""
    # Estatísticas gerais
    total_executions = BotExecution.query.count()
    running_executions = BotExecution.query.filter_by(status='running').count()
    completed_today = BotExecution.query.filter(
        BotExecution.start_time >= datetime.now().replace(hour=0, minute=0, second=0)
    ).filter_by(status='completed').count()
    
    failed_today = BotExecution.query.filter(
        BotExecution.start_time >= datetime.now().replace(hour=0, minute=0, second=0)
    ).filter_by(status='failed').count()
    
    # Últimas execuções
    recent_executions = BotExecution.query.order_by(BotExecution.start_time.desc()).limit(10).all()
    
    # Execuções por bot (últimos 7 dias)
    week_ago = datetime.now() - timedelta(days=7)
    executions_by_bot = db.session.query(
        BotExecution.bot_name,
        db.func.count(BotExecution.id).label('count')
    ).filter(BotExecution.start_time >= week_ago).group_by(BotExecution.bot_name).all()
    
    stats = {
        'total_executions': total_executions,
        'running_executions': running_executions,
        'completed_today': completed_today,
        'failed_today': failed_today,
        'recent_executions': [ex.to_dict() for ex in recent_executions],
        'executions_by_bot': [{'bot_name': name, 'count': count} for name, count in executions_by_bot]
    }
    
    return render_template('dashboard.html', stats=stats, bots=AVAILABLE_BOTS)

@app.route('/bots')
@login_required
def bots_management():
    """Página de gerenciamento de bots"""
    return render_template('bots.html', bots=AVAILABLE_BOTS)

@app.route('/recebimento-nf')
@login_required
def recebimento_nf():
    """Página de gerenciamento de recebimento de NF"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filtros
    pedido_filter = request.args.get('pedido', '')
    nf_filter = request.args.get('nf', '')
    status_filter = request.args.get('status', '')
    
    # Query base
    query = RecebimentoNF.query
    
    # Aplicar filtros
    if pedido_filter:
        query = query.filter(RecebimentoNF.pedido_compra.contains(pedido_filter))
    if nf_filter:
        query = query.filter(RecebimentoNF.nota_fiscal.contains(nf_filter))
    if status_filter:
        query = query.filter(RecebimentoNF.status == status_filter)
    
    # Ordenar por data de criação (mais recente primeiro)
    query = query.order_by(RecebimentoNF.created_at.desc())
    
    # Paginação
    recebimentos = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('recebimento_nf.html', 
                         recebimentos=recebimentos,
                         pedido_filter=pedido_filter,
                         nf_filter=nf_filter,
                         status_filter=status_filter)

@app.route('/recebimento-nf/add', methods=['POST'])
@login_required
def add_recebimento_nf():
    """Adicionar novo recebimento de NF"""
    try:
        pedido_compra = request.form.get('pedido_compra', '').strip()
        nota_fiscal = request.form.get('nota_fiscal', '').strip()
        chave_acesso = request.form.get('chave_acesso', '').strip()
        
        # Validações
        if not pedido_compra:
            flash('Pedido de Compra é obrigatório', 'error')
            return redirect(url_for('recebimento_nf'))
            
        if not nota_fiscal:
            flash('Nota Fiscal é obrigatória', 'error')
            return redirect(url_for('recebimento_nf'))
            
        if not chave_acesso:
            flash('Chave de Acesso é obrigatória', 'error')
            return redirect(url_for('recebimento_nf'))
            
        if len(chave_acesso) != 44:
            flash('Chave de Acesso deve ter 44 caracteres', 'error')
            return redirect(url_for('recebimento_nf'))
        
        # Verificar se já existe
        existing = RecebimentoNF.query.filter_by(chave_acesso=chave_acesso).first()
        if existing:
            flash('Já existe um recebimento com esta Chave de Acesso', 'error')
            return redirect(url_for('recebimento_nf'))
        
        # Criar novo recebimento
        recebimento = RecebimentoNF(
            pedido_compra=pedido_compra,
            nota_fiscal=nota_fiscal,
            chave_acesso=chave_acesso,
            created_by=current_user.id
        )
        
        db.session.add(recebimento)
        db.session.commit()
        
        flash('Recebimento de NF adicionado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar recebimento: {str(e)}', 'error')
    
    return redirect(url_for('recebimento_nf'))

@app.route('/logs')
@login_required
def logs_view():
    """Página de visualização de logs"""
    page = request.args.get('page', 1, type=int)
    execution_id = request.args.get('execution_id', type=int)
    level = request.args.get('level', '')
    
    query = BotLog.query
    
    if execution_id:
        query = query.filter_by(execution_id=execution_id)
    if level:
        query = query.filter_by(level=level)
    
    logs = query.order_by(BotLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    executions = BotExecution.query.order_by(BotExecution.start_time.desc()).limit(20).all()
    
    return render_template('logs.html', logs=logs, executions=executions, 
                         current_execution_id=execution_id, current_level=level)

@app.route('/execute/<bot_id>', methods=['POST'])
@login_required
def execute_bot(bot_id):
    """Executa um bot específico"""
    if bot_id not in AVAILABLE_BOTS:
        return jsonify({'error': 'Bot não encontrado'}), 404
    
    bot_config = AVAILABLE_BOTS[bot_id]
    parameters = request.json.get('parameters', {})
    
    # Criar registro de execução
    execution = BotExecution(
        bot_name=bot_config['name'],
        status='running',
        parameters=json.dumps(parameters)
    )
    db.session.add(execution)
    db.session.commit()
    
    # Log inicial
    log_entry = BotLog(
        execution_id=execution.id,
        level='INFO',
        message=f'Iniciando execução do bot {bot_config["name"]}',
        module='orchestrator'
    )
    db.session.add(log_entry)
    db.session.commit()
    
    # Executar bot em thread separada
    def run_bot():
        try:
            # Executar o script do bot
            script_path = Path(bot_config['script'])
            if script_path.exists():
                # Configurar variáveis de ambiente para o bot
                env = os.environ.copy()
                env['RPA_EXECUTION_ID'] = str(execution.id)
                
                result = subprocess.run(
                    ['python', str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd(),
                    env=env
                )
                
                # Atualizar execução
                execution.status = 'completed' if result.returncode == 0 else 'failed'
                execution.end_time = datetime.utcnow()
                execution.duration = (execution.end_time - execution.start_time).total_seconds()
                execution.result = result.stdout
                if result.stderr:
                    execution.error_message = result.stderr
                
                # Log final
                log_level = 'INFO' if result.returncode == 0 else 'ERROR'
                log_message = 'Execução concluída com sucesso' if result.returncode == 0 else f'Execução falhou: {result.stderr}'
                
                final_log = BotLog(
                    execution_id=execution.id,
                    level=log_level,
                    message=log_message,
                    module='orchestrator'
                )
                db.session.add(final_log)
            else:
                execution.status = 'failed'
                execution.end_time = datetime.utcnow()
                execution.duration = (execution.end_time - execution.start_time).total_seconds()
                execution.error_message = f'Script não encontrado: {script_path}'
                
                error_log = BotLog(
                    execution_id=execution.id,
                    level='ERROR',
                    message=f'Script não encontrado: {script_path}',
                    module='orchestrator'
                )
                db.session.add(error_log)
            
            db.session.commit()
            
        except Exception as e:
            execution.status = 'failed'
            execution.end_time = datetime.utcnow()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            execution.error_message = str(e)
            
            error_log = BotLog(
                execution_id=execution.id,
                level='ERROR',
                message=f'Erro durante execução: {str(e)}',
                module='orchestrator'
            )
            db.session.add(error_log)
            db.session.commit()
    
    # Iniciar thread
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'execution_id': execution.id,
        'message': f'Bot {bot_config["name"]} iniciado com sucesso',
        'estimated_duration': bot_config['estimated_duration']
    })

@app.route('/execution/<int:execution_id>')
@login_required
def execution_details(execution_id):
    """Detalhes de uma execução específica"""
    execution = BotExecution.query.get_or_404(execution_id)
    logs = BotLog.query.filter_by(execution_id=execution_id).order_by(BotLog.timestamp.asc()).all()
    
    return render_template('execution_details.html', execution=execution, logs=logs)

@app.route('/api/execution/<int:execution_id>/status')
def execution_status(execution_id):
    """API para verificar status de execução"""
    execution = BotExecution.query.get_or_404(execution_id)
    return jsonify(execution.to_dict())

@app.route('/api/logs/<int:execution_id>')
def execution_logs_api(execution_id):
    """API para obter logs de uma execução"""
    logs = BotLog.query.filter_by(execution_id=execution_id).order_by(BotLog.timestamp.asc()).all()
    return jsonify([log.to_dict() for log in logs])

@app.route('/stop/<int:execution_id>', methods=['POST'])
def stop_execution(execution_id):
    """Para uma execução em andamento"""
    execution = BotExecution.query.get_or_404(execution_id)
    
    if execution.status == 'running':
        execution.status = 'stopped'
        execution.end_time = datetime.utcnow()
        execution.duration = (execution.end_time - execution.start_time).total_seconds()
        
        stop_log = BotLog(
            execution_id=execution.id,
            level='WARNING',
            message='Execução interrompida pelo usuário',
            module='orchestrator'
        )
        db.session.add(stop_log)
        db.session.commit()
        
        flash('Execução interrompida com sucesso', 'warning')
    else:
        flash('Execução não está em andamento', 'error')
    
    return redirect(url_for('execution_details', execution_id=execution_id))

def create_admin_user():
    """Cria o usuário administrador padrão se não existir"""
    try:
        admin = User.query.filter_by(username='profectum').first()
        if not admin:
            admin = User(
                username='profectum',
                email='admin@profectum.com',
                full_name='Administrador Geral',
                role='admin'
            )
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print("👤 Usuário administrador criado: profectum / 123456")
        else:
            print("👤 Usuário administrador já existe")
    except Exception as e:
        print(f"⚠️ Erro ao verificar/criar usuário admin: {e}")
        print("💡 Execute: python init_database.py")

@app.context_processor
def inject_settings():
    """Injetar configurações do sistema nos templates"""
    return dict(
        system_settings={
            'primary_color': SystemSettings.get_setting('primary_color', '#2563eb'),
            'logo_url': SystemSettings.get_setting('logo_url', ''),
            'logo_type': SystemSettings.get_setting('logo_type', 'icon'),
            'system_name': SystemSettings.get_setting('system_name', 'RPA Profectum'),
        },
        login_settings={
            'bg_type': SystemSettings.get_setting('login_bg_type', 'color'),
            'bg_color': SystemSettings.get_setting('login_bg_color', '#f8fafc'),
            'gradient_color1': SystemSettings.get_setting('login_gradient_color1', '#2563eb'),
            'gradient_color2': SystemSettings.get_setting('login_gradient_color2', '#1d4ed8'),
            'bg_image_url': SystemSettings.get_setting('login_bg_image_url', ''),
            'height': SystemSettings.get_setting('login_height', 'normal'),
            'title': SystemSettings.get_setting('login_title', 'Bem-vindo de volta!'),
        }
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    app.run(debug=True, host='0.0.0.0', port=5000)