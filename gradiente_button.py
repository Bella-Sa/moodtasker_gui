import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

def create_rounded_gradient_button_image(text, width, height, gradient_image_path, font_path, font_size, corner_radius, text_color="white"):
    """
    Cria uma imagem de botão com fundo gradiente e cantos arredondados.
    """
    try:
        base_gradient = Image.open(gradient_image_path).convert("RGBA").resize((width, height))
        
        mask = Image.new("L", (width, height), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle((0, 0, width, height), corner_radius, fill=255)
        
        base_gradient.putalpha(mask)

        draw_text = ImageDraw.Draw(base_gradient)
        font = ImageFont.truetype(font_path, font_size)
        
        text_bbox = draw_text.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (width - text_width) / 2
        text_y = (height - text_height) / 2 - (font_size / 4.5)
        # Desenhar o texto na imagem
        draw_text.text((text_x, text_y), text, font=font, fill=text_color)
        # Aplicar a máscara de arredondamento
        return ctk.CTkImage(light_image=base_gradient, dark_image=base_gradient, size=(width, height))

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado! Verifique os caminhos: {gradient_image_path}, {font_path}")
        fallback_img = Image.new("RGBA", (width, height), color="purple")
        draw = ImageDraw.Draw(fallback_img)
        draw.text((10, 10), "Error", fill="white")
        return ctk.CTkImage(light_image=fallback_img, dark_image=fallback_img, size=(width, height))
    except Exception as e:
        print(f"Erro ao criar imagem de botão: {e}")
        return None