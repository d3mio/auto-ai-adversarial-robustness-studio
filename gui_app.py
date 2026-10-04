import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import torch
from torchvision import transforms

class AIRobustnessStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('AI Adversarial Robustness & Defense Studio')
        self.geometry('1200x800')
        self.configure(bg='#2d2d2d')
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#2d2d2d')
        self.style.configure('TLabel', background='#2d2d2d', foreground='white')
        self.style.configure('TButton', background='#4CAF50', foreground='white')
        self.style.configure('TEntry', fieldbackground='#3d3d3d', foreground='white')
        self.style.map('TButton', background=[('active', '#45a049')])

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Section
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(input_frame, text='Model Path:').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.model_path = ttk.Entry(input_frame, width=50)
        self.model_path.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text='Browse', command=self.browse_model).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text='Input Image:').grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.input_image = ttk.Entry(input_frame, width=50)
        self.input_image.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text='Browse', command=self.browse_image).grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(input_frame, text='Generate Adversarial Example', command=self.generate_adversarial).grid(row=2, column=1, padx=5, pady=10)

        # Visualization Section
        vis_frame = ttk.Frame(main_frame)
        vis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.figure = plt.Figure(figsize=(10, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=vis_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def browse_model(self):
        file_path = filedialog.askopenfilename(filetypes=[('Model Files', '*.pt')])
        self.model_path.delete(0, tk.END)
        self.model_path.insert(0, file_path)

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[('Image Files', '*.png *.jpg *.jpeg')])
        self.input_image.delete(0, tk.END)
        self.input_image.insert(0, file_path)

    def generate_adversarial(self):
        model_path = self.model_path.get()
        image_path = self.input_image.get()

        if not model_path or not image_path:
            messagebox.showerror('Error', 'Please provide both model path and input image.')
            return

        model = torch.load(model_path)
        model.eval()

        # Load and preprocess image
        image = plt.imread(image_path)
        if image.ndim == 3 and image.shape[2] == 4:
            image = image[:, :, :3]
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        image_tensor = transform(image).unsqueeze(0)

        # Generate adversarial example (simple FGSM attack)
        epsilon = 0.1
        image_tensor.requires_grad = True
        output = model(image_tensor)
        loss = torch.nn.functional.cross_entropy(output, torch.argmax(output, dim=1))
        loss.backward()
        adversarial_image = image_tensor + epsilon * image_tensor.grad.sign()
        adversarial_image = torch.clamp(adversarial_image, -1, 1)

        # Plot original vs adversarial
        self.figure.clear()
        ax1 = self.figure.add_subplot(121)
        ax1.imshow(image)
        ax1.set_title('Original Image')
        ax1.axis('off')

        ax2 = self.figure.add_subplot(122)
        adversarial_image_np = np.transpose(adversarial_image.detach().numpy()[0], (1, 2, 0))
        ax2.imshow((adversarial_image_np + 1) / 2)
        ax2.set_title('Adversarial Image')
        ax2.axis('off')

        self.canvas.draw()

if __name__ == '__main__':
    app = AIRobustnessStudio()
    app.mainloop()