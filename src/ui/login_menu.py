"""
Menú de inicio de sesión
"""

import pygame

class LoginMenu:
    def __init__(self, config):
        self.config = config
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 24)
        
        self.state = "MAIN"  # MAIN, LOGIN, REGISTER
        self.selected_option = 0
        self.email_input = ""
        self.password_input = ""
        self.input_active = "email"  # email, password
        self.message = ""
        self.message_color = (255, 255, 255)
        
        self.main_options = ["Iniciar Sesión", "Registrarse", "Continuar sin cuenta"]
        self.action = None
        
    def handle_event(self, event):
        """Maneja eventos del menú de login"""
        if self.state == "MAIN":
            self.handle_main_menu(event)
        elif self.state in ["LOGIN", "REGISTER"]:
            self.handle_form_input(event)
    
    def handle_main_menu(self, event):
        """Maneja el menú principal de autenticación"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.main_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.main_options)
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:  # Iniciar Sesión
                    self.state = "LOGIN"
                    self.reset_form()
                elif self.selected_option == 1:  # Registrarse
                    self.state = "REGISTER"
                    self.reset_form()
                elif self.selected_option == 2:  # Continuar sin cuenta
                    self.action = "CONTINUE_OFFLINE"
    
    def handle_form_input(self, event):
        """Maneja la entrada de formularios"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "MAIN"
                self.message = ""
            elif event.key == pygame.K_TAB:
                self.input_active = "password" if self.input_active == "email" else "email"
            elif event.key == pygame.K_RETURN:
                if self.state == "LOGIN":
                    self.action = "LOGIN_EMAIL"
                elif self.state == "REGISTER":
                    self.action = "REGISTER_EMAIL"
            elif event.key == pygame.K_BACKSPACE:
                if self.input_active == "email":
                    self.email_input = self.email_input[:-1]
                else:
                    self.password_input = self.password_input[:-1]
            elif event.key == pygame.K_F1:  # Google login
                self.action = "LOGIN_GOOGLE"
            else:
                # Agregar caracteres
                if event.unicode.isprintable():
                    if self.input_active == "email":
                        if len(self.email_input) < 50:
                            self.email_input += event.unicode
                    else:
                        if len(self.password_input) < 30:
                            self.password_input += event.unicode
    
    def reset_form(self):
        """Resetea el formulario"""
        self.email_input = ""
        self.password_input = ""
        self.input_active = "email"
        self.message = ""
    
    def set_message(self, message, is_error=False):
        """Establece un mensaje"""
        self.message = message
        self.message_color = (255, 100, 100) if is_error else (100, 255, 100)
    
    def render(self, screen):
        """Renderiza el menú de login"""
        if self.state == "MAIN":
            self.render_main_menu(screen)
        elif self.state in ["LOGIN", "REGISTER"]:
            self.render_form(screen)
    
    def render_main_menu(self, screen):
        """Renderiza el menú principal"""
        # Título
        title = self.font.render("DONKEY KONG", True, self.config.COLORS['YELLOW'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 150))
        screen.blit(title, title_rect)
        
        subtitle = self.small_font.render("Autenticación", True, self.config.COLORS['WHITE'])
        subtitle_rect = subtitle.get_rect(center=(self.config.WINDOW_WIDTH//2, 190))
        screen.blit(subtitle, subtitle_rect)
        
        # Opciones
        for i, option in enumerate(self.main_options):
            color = self.config.COLORS['YELLOW'] if i == self.selected_option else self.config.COLORS['WHITE']
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, 280 + i * 60))
            screen.blit(text, text_rect)
        
        # Instrucciones
        instructions = [
            "↑↓ para navegar, ENTER para seleccionar",
            "Inicia sesión para guardar tu progreso en la nube"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.tiny_font.render(instruction, True, self.config.COLORS['WHITE'])
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, 480 + i * 25))
            screen.blit(text, text_rect)
    
    def render_form(self, screen):
        """Renderiza el formulario de login/registro"""
        # Título
        title_text = "Iniciar Sesión" if self.state == "LOGIN" else "Registrarse"
        title = self.font.render(title_text, True, self.config.COLORS['YELLOW'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 120))
        screen.blit(title, title_rect)
        
        # Campo Email
        email_label = self.small_font.render("Email:", True, self.config.COLORS['WHITE'])
        screen.blit(email_label, (200, 200))
        
        email_color = self.config.COLORS['YELLOW'] if self.input_active == "email" else self.config.COLORS['WHITE']
        email_rect = pygame.Rect(200, 230, 400, 40)
        pygame.draw.rect(screen, email_color, email_rect, 2)
        
        email_text = self.small_font.render(self.email_input, True, self.config.COLORS['WHITE'])
        screen.blit(email_text, (210, 240))
        
        # Campo Password
        password_label = self.small_font.render("Contraseña:", True, self.config.COLORS['WHITE'])
        screen.blit(password_label, (200, 290))
        
        password_color = self.config.COLORS['YELLOW'] if self.input_active == "password" else self.config.COLORS['WHITE']
        password_rect = pygame.Rect(200, 320, 400, 40)
        pygame.draw.rect(screen, password_color, password_rect, 2)
        
        password_display = "*" * len(self.password_input)
        password_text = self.small_font.render(password_display, True, self.config.COLORS['WHITE'])
        screen.blit(password_text, (210, 330))
        
        # Botones
        submit_text = "Iniciar Sesión" if self.state == "LOGIN" else "Registrarse"
        submit_button = self.small_font.render(f"ENTER - {submit_text}", True, self.config.COLORS['GREEN'])
        screen.blit(submit_button, (200, 390))
        
        google_button = self.small_font.render("F1 - Iniciar con Google", True, self.config.COLORS['BLUE'])
        screen.blit(google_button, (200, 420))
        
        # Mensaje
        if self.message:
            message_text = self.small_font.render(self.message, True, self.message_color)
            message_rect = message_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 470))
            screen.blit(message_text, message_rect)
        
        # Instrucciones
        instructions = [
            "TAB - Cambiar campo",
            "ESC - Volver al menú"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.tiny_font.render(instruction, True, self.config.COLORS['WHITE'])
            screen.blit(text, (200, 520 + i * 20))
    
    def get_action(self):
        """Obtiene y resetea la acción"""
        action = self.action
        self.action = None
        return action
    
    def get_credentials(self):
        """Obtiene las credenciales ingresadas"""
        return self.email_input, self.password_input