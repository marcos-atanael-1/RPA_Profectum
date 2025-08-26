#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do RPA Profectum
"""

from app import app, db, User, SystemSettings

def init_database():
    """Inicializa o banco de dados e cria o usuário admin"""
    print("🗃️ Criando banco de dados SQLite...")
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("✅ Tabelas criadas com sucesso")
        
        # Criar configurações padrão se não existirem
        if not SystemSettings.query.first():
            print("⚙️ Criando configurações padrão...")
            default_settings = [
                ('primary_color', '#2563eb', 'Cor primária do sistema'),
                ('logo_type', 'icon', 'Tipo de logo (icon/url)'),
                ('logo_url', '', 'URL da logo personalizada'),
                ('system_name', 'RPA Profectum', 'Nome do sistema'),
                # Configurações de login
                ('login_bg_type', 'color', 'Tipo de fundo da página de login'),
                ('login_bg_color', '#f8fafc', 'Cor de fundo da página de login'),
                ('login_gradient_color1', '#2563eb', 'Primeira cor do gradiente de login'),
                ('login_gradient_color2', '#1d4ed8', 'Segunda cor do gradiente de login'),
                ('login_bg_image_url', '', 'URL da imagem de fundo do login'),
                ('login_height', 'normal', 'Altura da página de login'),
                ('login_title', 'Bem-vindo de volta!', 'Título da página de login'),
            ]
            
            for key, value, description in default_settings:
                setting = SystemSettings(
                    key=key,
                    value=value,
                    description=description
                )
                db.session.add(setting)
            
            db.session.commit()
            print("✅ Configurações padrão criadas!")
        
        # Verificar se já existe o usuário admin
        admin = User.query.filter_by(username='profectum').first()
        
        if not admin:
            print("👤 Criando usuário administrador...")
            admin = User(
                username='profectum',
                email='admin@profectum.com',
                full_name='Administrador Geral',
                role='admin'
            )
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário administrador criado com sucesso!")
            print("🔑 Credenciais:")
            print("   Usuário: profectum")
            print("   Senha: 123456")
        else:
            print("👤 Usuário administrador já existe")
    
    print("🎉 Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_database() 