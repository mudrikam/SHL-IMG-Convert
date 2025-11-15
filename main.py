import sys
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import qtawesome as qta
from PIL import Image

# Import AVIF support
try:
    import pillow_avif  # Enable AVIF support
except ImportError:
    pass

# Import HEIF/HEIC support
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

class ImageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setAcceptDrops(True)
        
        # Set window always on top automatically
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.output_dir = str(Path.home())
        
        # Remove the center_window call from here - it's too early
    
    def showEvent(self, event):
        """Override the show event to center the window when it first appears"""
        super().showEvent(event)
        # Only center on first show
        if not event.spontaneous():
            self.center_window()
    
    def center_window(self):
        """Center the window on the primary screen"""
        screen_rect = QGuiApplication.primaryScreen().availableGeometry()
        window_rect = self.frameGeometry()
        center_point = screen_rect.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())
        
    def init_ui(self):
        self.setWindowTitle("SHL Image Converter")
        # Use minimum size instead of fixed size to allow proper content display
        self.setMinimumSize(420, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        
        # Set window icon
        icon_path = Path(__file__).parent / "img_convert.ico"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
        
        # Apply rounded corners style
        self.setStyleSheet("""
            QWidget {
                border-radius: 12px;
                background-color: palette(window);
            }
            QPushButton {
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 10px 16px;
                background-color: palette(button);
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: palette(light);
            }
            QPushButton:pressed {
                background-color: palette(dark);
            }
            QComboBox {
                border: 1px solid palette(mid);
                border-radius: 6px;
                padding: 6px 10px;
                background-color: palette(base);
                min-width: 100px;
            }
            QLabel {
                color: palette(window-text);
            }
            QSlider::groove:horizontal {
                border: 1px solid palette(mid);
                height: 6px;
                background: palette(base);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: palette(button);
                border: 1px solid palette(mid);
                width: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: palette(light);
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid palette(mid);
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Source Section
        source_group = QGroupBox("Source Images")
        source_group.setStyleSheet("QGroupBox { color: #e12a61; }")
        source_layout = QVBoxLayout()
        
        # Drop area with QtAwesome icon
        drop_icon = qta.icon('fa5s.cloud-upload-alt', color='#e12a61')
        self.drop_label = QLabel("Drop images here or click to browse\nSupports all major image formats")
        self.drop_label.setAlignment(Qt.AlignCenter)
        
        # Add icon to drop area - fix icon display
        icon_label = QLabel()
        icon_label.setPixmap(drop_icon.pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignCenter)
        # Remove hardcoded height to let layout manage it
        
        drop_layout = QVBoxLayout()
        drop_layout.addWidget(icon_label)
        drop_layout.addWidget(self.drop_label)
        drop_layout.setContentsMargins(10, 10, 10, 10)
        drop_layout.setSpacing(10)
        
        drop_container = QWidget()
        drop_container.setLayout(drop_layout)
        # Apply styles only to the container, not its children
        drop_container.setObjectName("dropZone")  # Add object name for more specific styling
        drop_container.setStyleSheet("""
            #dropZone {
                border: 2px dashed rgba(225, 42, 97, 0.2);
                border-radius: 8px;
                padding: 16px;
                background-color: rgba(225, 42, 97, 0.02);
            }
            #dropZone > QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        drop_container.mousePressEvent = self.browse_files
        self.drop_container = drop_container
        
        source_layout.addWidget(self.drop_container)
        
        source_group.setLayout(source_layout)
        main_layout.addWidget(source_group)
        
        # Output Settings Section
        output_group = QGroupBox("Output Settings")
        output_group.setStyleSheet("QGroupBox { color: #e12a61; }")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)  # Add more spacing between elements
        
        # Output directory selection
        output_dir_layout = QHBoxLayout()
        output_dir_icon = QLabel()
        output_dir_icon.setPixmap(qta.icon('fa5s.folder-open', color='#e12a61').pixmap(16, 16))
        output_dir_layout.addWidget(output_dir_icon)
        output_dir_layout.addWidget(QLabel("Output Directory:"))
        output_dir_layout.addStretch()
        
        self.output_dir_btn = QPushButton("Browse")
        self.output_dir_btn.setIcon(qta.icon('fa5s.folder-open', color="#e12a61"))
        self.output_dir_btn.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(self.output_dir_btn)
        
        output_layout.addLayout(output_dir_layout)
        
        # Output path display - improve display
        self.output_path_label = QLabel(self.truncate_path(str(Path.home())))
        self.output_path_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: palette(window-text);
                padding: 6px 10px;
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 4px;
                margin-bottom: 10px;
            }
        """)
        # Remove hardcoded height and let the label adjust to content
        self.output_path_label.setWordWrap(True)
        self.output_path_label.setToolTip(str(Path.home()))
        # Add size policy to allow growing
        self.output_path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        output_layout.addWidget(self.output_path_label)
        
        # Format selection with icon
        format_layout = QHBoxLayout()
        format_icon = QLabel()
        format_icon.setPixmap(qta.icon('fa5s.file-image', color='#e12a61').pixmap(16, 16))
        format_layout.addWidget(format_icon)
        format_layout.addWidget(QLabel("Output Format:"))
        format_layout.addStretch()
        
        self.format_combo = QComboBox()
        formats = ['PNG', 'JPG', 'JPEG', 'WEBP', 'AVIF', 'BMP', 'ICO']
        self.format_combo.addItems(formats)
        self.format_combo.setCurrentText('PNG')
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        output_layout.addLayout(format_layout)
        
        # Quality slider (for JPEG, WEBP)
        self.quality_widget = QWidget()
        quality_layout = QVBoxLayout(self.quality_widget)
        quality_layout.setContentsMargins(0, 8, 0, 0)
        
        quality_header = QHBoxLayout()
        quality_icon = QLabel()
        quality_icon.setPixmap(qta.icon('fa5s.sliders-h', color='#e12a61').pixmap(16, 16))
        quality_header.addWidget(quality_icon)
        quality_header.addWidget(QLabel("Image Quality:"))
        quality_header.addStretch()
        self.quality_value_label = QLabel("100%")
        self.quality_value_label.setStyleSheet("font-weight: bold; color: #e12a61;")
        quality_header.addWidget(self.quality_value_label)
        quality_layout.addLayout(quality_header)
        
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(100)
        self.quality_slider.valueChanged.connect(lambda v: self.quality_value_label.setText(f"{v}%"))
        quality_layout.addWidget(self.quality_slider)
        
        output_layout.addWidget(self.quality_widget)
        
        # Compression slider (for PNG)
        self.compression_widget = QWidget()
        compression_layout = QVBoxLayout(self.compression_widget)
        compression_layout.setContentsMargins(0, 8, 0, 0)
        
        compression_header = QHBoxLayout()
        compression_icon = QLabel()
        compression_icon.setPixmap(qta.icon('fa5s.compress-arrows-alt', color='#e12a61').pixmap(16, 16))
        compression_header.addWidget(compression_icon)
        compression_header.addWidget(QLabel("Compression Level:"))
        compression_header.addStretch()
        self.compression_value_label = QLabel("6")
        self.compression_value_label.setStyleSheet("font-weight: bold; color: #e12a61;")
        compression_header.addWidget(self.compression_value_label)
        compression_layout.addLayout(compression_header)
        
        # Add explanation text with better dark theme support
        compression_info = QLabel("Lower = Faster processing, Larger file size\nHigher = Slower processing, Smaller file size")
        compression_info.setStyleSheet("font-size: 10px; color: rgba(122, 122, 122, 0.32); margin-left: 20px;")
        compression_layout.addWidget(compression_info)
        
        self.compression_slider = QSlider(Qt.Horizontal)
        self.compression_slider.setRange(0, 9)
        self.compression_slider.setValue(6)
        self.compression_slider.valueChanged.connect(lambda v: self.compression_value_label.setText(str(v)))
        compression_layout.addWidget(self.compression_slider)
        
        output_layout.addWidget(self.compression_widget)
        
        # ICO settings
        self.ico_widget = QWidget()
        ico_layout = QVBoxLayout(self.ico_widget)
        ico_layout.setContentsMargins(0, 8, 0, 0)
        
        ico_header = QHBoxLayout()
        ico_icon = QLabel()
        ico_icon.setPixmap(qta.icon('fa5s.th', color='#e12a61').pixmap(16, 16))
        ico_header.addWidget(ico_icon)
        ico_header.addWidget(QLabel("ICO Multiple Sizes:"))
        ico_header.addStretch()
        ico_layout.addLayout(ico_header)
        
        # ICO info text - update to clearly state it generates multiple sizes
        ico_info = QLabel("Generates a multi-size ICO with all standard sizes:\n16x16, 32x32, 48x48, 64x64, 128x128, 256x256")
        ico_info.setStyleSheet("font-size: 10px; color: rgba(122, 122, 122, 0.32); margin-left: 20px;")
        ico_layout.addWidget(ico_info)
        
        output_layout.addWidget(self.ico_widget)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Rescale Section
        rescale_group = QGroupBox("Rescale Options")
        rescale_group.setStyleSheet("QGroupBox { color: #e12a61; }")
        rescale_layout = QVBoxLayout()
        
        rescale_header = QHBoxLayout()
        rescale_icon = QLabel()
        rescale_icon.setPixmap(qta.icon('fa5s.expand-arrows-alt', color='#e12a61').pixmap(16, 16))
        rescale_header.addWidget(rescale_icon)
        rescale_header.addWidget(QLabel("Resize to:"))
        rescale_header.addStretch()
        self.rescale_value_label = QLabel("100%")
        self.rescale_value_label.setStyleSheet("font-weight: bold; color: #e12a61;")
        rescale_header.addWidget(self.rescale_value_label)
        rescale_layout.addLayout(rescale_header)
        
        # Rescale info text
        rescale_info = QLabel("100% = Original size, <100% = Smaller, >100% = Larger")
        rescale_info.setStyleSheet("font-size: 10px; color: rgba(122, 122, 122, 0.32); margin-left: 20px;")
        rescale_layout.addWidget(rescale_info)
        
        self.rescale_slider = QSlider(Qt.Horizontal)
        self.rescale_slider.setRange(10, 500)  # 10% to 500%
        self.rescale_slider.setValue(100)
        self.rescale_slider.valueChanged.connect(lambda v: self.rescale_value_label.setText(f"{v}%"))
        rescale_layout.addWidget(self.rescale_slider)
        
        rescale_group.setLayout(rescale_layout)
        main_layout.addWidget(rescale_group)
        
        # Action Buttons and Progress Bar
        action_layout = QVBoxLayout()
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v% - Processing %v of %m files")
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #e12a61;
            }
        """)
        self.progress_bar.setVisible(False)
        action_layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Browse button
        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setIcon(qta.icon('fa5s.folder-open', color="#e12a61"))
        self.browse_btn.clicked.connect(self.browse_files)
        button_layout.addWidget(self.browse_btn)
        
        # Clear button (broom icon, no text)
        self.clear_btn = QPushButton()
        self.clear_btn.setIcon(qta.icon('fa5s.broom', color="#e12a61"))
        self.clear_btn.setToolTip("Clear loaded files")
        self.clear_btn.clicked.connect(self.clear_files)
        self.clear_btn.setEnabled(False)  # Initially disabled until files are loaded
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        # Convert button
        self.convert_btn = QPushButton("Start Conversion")
        self.convert_btn.setIcon(qta.icon('fa5s.magic', color='#2F4F2F'))
        self.convert_btn.clicked.connect(self.convert_images)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #98FB98;
                color: #2F4F2F;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #78DB78;
            }
            QPushButton:disabled {
                background-color: palette(mid);
                color: palette(disabled-text);
            }
        """)
        button_layout.addWidget(self.convert_btn)
        
        action_layout.addLayout(button_layout)
        main_layout.addLayout(action_layout)
        
        self.setLayout(main_layout)
        self.image_paths = []
        self.on_format_changed('PNG')  # Initialize visibility
    
    def truncate_path(self, path, max_length=45):
        """Truncate path from the beginning to fit within max_length"""
        if len(path) <= max_length:
            return path
        
        # Keep more of the path by showing the drive and last part
        parts = path.split(os.sep)
        if len(parts) > 2:
            # For Windows paths, keep drive letter
            if ':' in parts[0]:
                return parts[0] + os.sep + "..." + os.sep + os.sep.join(parts[-2:])
            else:
                return "..." + os.sep + os.sep.join(parts[-2:])
        
        return "..." + path[-(max_length-3):]
    
    def browse_output_dir(self):
        """Open dialog to select output directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_dir)        
        if dir_path:
            self.output_dir = dir_path
            self.output_path_label.setText(self.truncate_path(dir_path))
            self.output_path_label.setToolTip(dir_path)
        
    def on_format_changed(self, format_name):
        # Show/hide quality, compression, and ICO controls based on format
        quality_formats = ['JPG', 'JPEG', 'WEBP', 'AVIF']
        self.quality_widget.setVisible(format_name in quality_formats)
        self.compression_widget.setVisible(format_name == 'PNG')
        self.ico_widget.setVisible(format_name == 'ICO')
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Same border style, just higher opacity
            self.drop_container.setStyleSheet("""
                #dropZone {
                    border: 2px dashed rgba(225, 42, 97, 0.7);
                    border-radius: 8px;
                    padding: 16px;
                    background-color: rgba(225, 42, 97, 0.15);
                }
                #dropZone > QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)
    
    def dragLeaveEvent(self, event):
        # Return to normal state
        self.drop_container.setStyleSheet("""
            #dropZone {
                border: 2px dashed rgba(225, 42, 97, 0.2);
                border-radius: 8px;
                padding: 16px;
                background-color: rgba(225, 42, 97, 0.02);
            }
            #dropZone > QLabel {
                background-color: transparent;
                border: none;
            }
        """)
    
    def dropEvent(self, event):
        self.dragLeaveEvent(event)
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        # Filter hanya file gambar yang didukung (termasuk .heic/.heif)
        supported_ext = ('.png', '.jpg', '.jpeg', '.webp', '.avif', '.bmp', '.ico', '.heic', '.heif')
        files = [f for f in files if f.lower().endswith(supported_ext)]
        self.load_images(files)
        event.acceptProposedAction()
    
    def browse_files(self, event=None):
        supported_extensions = "*.png *.jpg *.jpeg *.webp *.avif *.bmp *.ico *.heic *.heif"
        filter_parts = [
            "PNG (*.png)",
            "JPEG (*.jpg *.jpeg)",
            "WebP (*.webp)",
            "AVIF (*.avif)",
            "BMP (*.bmp)",
            "ICO (*.ico)",
            "HEIC/HEIF (*.heic *.heif)"
        ]
        file_filter = f"Supported Images ({supported_extensions});;" + ";;".join(filter_parts) + ";;All Files (*)"
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Source Images", str(Path.home()), file_filter
        )
        if files:
            self.load_images(files)
    
    def load_images(self, files):
        valid_files = []
        for file in files:
            try:
                with Image.open(file) as img:
                    valid_files.append(file)
            except Exception as e:
                continue
        
        if valid_files:
            self.image_paths = valid_files
            count = len(valid_files)
            self.drop_label.setText(f"{count} image{'s' if count > 1 else ''} ready for conversion\nClick 'Start Conversion' to proceed")
            # Green background with no border when files are loaded
            self.drop_container.setStyleSheet("""
                #dropZone {
                    border: none;
                    border-radius: 8px;
                    padding: 16px;
                    background-color: rgba(80, 200, 120, 0.2);
                }
                #dropZone > QLabel {
                    background-color: transparent;
                    border: none;
                }
            """)
            self.convert_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)  # Enable clear button when files are loaded
        else:
            QMessageBox.warning(self, "Invalid Files", "No valid images found in the selected files!")
    
    def clear_files(self):
        """Clear loaded files and reset the UI"""
        self.image_paths = []
        self.drop_label.setText("Drop images here or click to browse\nSupports all major image formats")
        self.drop_container.setStyleSheet("""
            #dropZone {
                border: 2px dashed rgba(225, 42, 97, 0.2);
                border-radius: 8px;
                padding: 16px;
                background-color: rgba(225, 42, 97, 0.02);
            }
            #dropZone > QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        self.convert_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
    
    def convert_images(self):
        if not self.image_paths:
            return
        
        target_format = self.format_combo.currentText().lower()
        # Untuk JPG/JPEG, gunakan format 'JPEG' dan ekstensi sesuai pilihan
        if target_format == 'jpg':
            save_format = 'JPEG'
            ext = 'jpg'
        elif target_format == 'jpeg':
            save_format = 'JPEG'
            ext = 'jpeg'
        else:
            save_format = target_format.upper()
            ext = target_format.lower()
        rescale_percent = self.rescale_slider.value()
        converted = 0
        total_files = len(self.image_paths)
        
        # Setup progress display
        self.progress_bar.setRange(0, total_files)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v of %m files (%p%)")
        self.progress_bar.setAlignment(Qt.AlignCenter)  # Ensure center alignment
        self.progress_bar.setVisible(True)
        
        self.convert_btn.setText("Converting...")
        self.convert_btn.setIcon(qta.icon('fa5s.spinner', color='#2F4F2F', animation=qta.Spin(self.convert_btn)))
        self.convert_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.output_dir_btn.setEnabled(False)
        
        # Get current timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            for i, img_path in enumerate(self.image_paths):
                try:
                    # Update progress
                    self.progress_bar.setValue(i)
                    QApplication.processEvents()  # Ensure UI updates
                    
                    with Image.open(img_path) as img:
                        # Rescale image if not 100%
                        if rescale_percent != 100:
                            new_width = int(img.size[0] * rescale_percent / 100)
                            new_height = int(img.size[1] * rescale_percent / 100)
                            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        rgb_only_formats = ['jpeg', 'bmp']
                        # Always convert to RGB for JPEG/JPG to avoid mode errors
                        if target_format in ['jpg', 'jpeg']:
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                        elif target_format in rgb_only_formats and img.mode in ('RGBA', 'LA', 'P'):
                            if img.mode == 'P' and 'transparency' in img.info:
                                img = img.convert('RGBA')
                            if img.mode in ('RGBA', 'LA'):
                                # Get background color from application palette instead of hardcoded white
                                bg_color = self.palette().color(QPalette.Base)
                                bg_rgb = (bg_color.red(), bg_color.green(), bg_color.blue())
                                background = Image.new('RGB', img.size, bg_rgb)
                                if img.mode == 'RGBA':
                                    background.paste(img, mask=img.split()[-1])
                                else:
                                    background.paste(img, mask=img.split()[-1])
                                img = background
                        
                        # Generate output filename with timestamp
                        base_name = Path(img_path).stem
                        if rescale_percent != 100:
                            base_name += f"_{rescale_percent}pct"
                        base_name += f"_{timestamp}"
                        output_path = Path(self.output_dir) / f"{base_name}.{ext}"
                        save_kwargs = {}
                        if save_format == 'JPEG':
                            save_kwargs['quality'] = self.quality_slider.value()
                            save_kwargs['optimize'] = True
                        elif save_format == 'WEBP':
                            save_kwargs['quality'] = self.quality_slider.value()
                            save_kwargs['method'] = 6
                        elif save_format == 'AVIF':
                            save_kwargs['quality'] = self.quality_slider.value()
                            save_kwargs['speed'] = 6
                        elif save_format == 'PNG':
                            save_kwargs['compress_level'] = self.compression_slider.value()
                            save_kwargs['optimize'] = True
                        elif save_format == 'ICO':
                            # ICO with multiple standard sizes
                            ico_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
                            
                            # Ensure image is in RGBA mode for ICO
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            
                            # Create images for each size
                            ico_images = []
                            for size in ico_sizes:
                                # Resize image maintaining aspect ratio
                                resized = img.copy()
                                resized.thumbnail(size, Image.Resampling.LANCZOS)
                                
                                # Create new image with exact size and center the resized image
                                centered = Image.new('RGBA', size, (0, 0, 0, 0))
                                paste_x = (size[0] - resized.size[0]) // 2
                                paste_y = (size[1] - resized.size[1]) // 2
                                centered.paste(resized, (paste_x, paste_y))
                                ico_images.append(centered)
                            
                            # Create direct binary ICO file according to specs
                            try:
                                print(f"Creating ICO using direct binary format implementation")
                                import io
                                import struct
                                
                                # Convert all images to PNG binary data
                                image_data = []
                                for ico_img in ico_images:
                                    # Save image as PNG
                                    png_io = io.BytesIO()
                                    ico_img.save(png_io, format='PNG')
                                    png_data = png_io.getvalue()
                                    width, height = ico_img.size
                                    
                                    # Colors in palette (0 for true color)
                                    colors = 0
                                    # Color planes (should be 1)
                                    planes = 1
                                    # Bits per pixel (32 for RGBA)
                                    bpp = 32
                                    # Size of PNG data
                                    size = len(png_data)
                                    
                                    image_data.append((width, height, colors, planes, bpp, png_data, size))
                                
                                # Create the ICO file
                                with open(output_path, 'wb') as f:
                                    # ICO header (6 bytes)
                                    # 0-1: Reserved (0)
                                    # 2-3: Image type (1 for ICO)
                                    # 4-5: Number of images
                                    f.write(struct.pack('<HHH', 0, 1, len(image_data)))
                                    
                                    # Calculate offset to start of bitmap data
                                    # Header (6 bytes) + (directory entries (16 bytes each))
                                    offset = 6 + len(image_data) * 16;
                                    
                                    # Write directory entries
                                    for width, height, colors, planes, bpp, data, size in image_data:
                                        # Write directory entry (16 bytes)
                                        # 0: Width (0-255, 0 means 256)
                                        # 1: Height (0-255, 0 means 256)
                                        # 2: Colors in palette (0 for true color)
                                        # 3: Reserved (0)
                                        # 4-5: Color planes (should be 1)
                                        # 6-7: Bits per pixel
                                        # 8-11: Size of image data
                                        # 12-15: Offset to image data
                                        width_byte = 0 if width == 256 else width
                                        height_byte = 0 if height == 256 else height
                                        f.write(struct.pack('<BBBBHHII', width_byte, height_byte, colors, 0, planes, bpp, size, offset))
                                        offset += size
                                    
                                    # Write image data
                                    for _, _, _, _, _, data, _ in image_data:
                                        f.write(data)
                                
                                print(f"Successfully created multi-size ICO file using direct binary format")
                                
                                # Check if the file was created successfully
                                try:
                                    with Image.open(output_path) as verify_img:
                                        print(f"Verified ICO has {getattr(verify_img, 'n_frames', 1)} frames")
                                except Exception as verify_error:
                                    print(f"Warning: Could not verify ICO file: {verify_error}")
                                
                                converted += 1
                                continue
                                
                            except Exception as e:
                                import traceback
                                print(f"Error creating multi-size ICO with direct binary method: {e}")
                                traceback.print_exc()
                                
                                # Last resort - just use PIL to create a single-size ICO
                                print("Falling back to single-size ICO")
                                ico_images[0].save(output_path, format='ICO')  # Save smallest size for favicon
                                converted += 1
                                continue
                        
                        # For non-ICO formats
                        img.save(output_path, format=save_format, **save_kwargs)
                        converted += 1
                        
                except Exception as e:
                    print(f"Error converting {img_path}: {e}")
                    continue
            
            # Update final progress
            self.progress_bar.setValue(total_files)
            QMessageBox.information(self, "Success", f"Converted {converted} images to {target_format.upper()}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Conversion failed: {str(e)}")
        
        finally:
            # Reset progress UI without clearing the loaded files
            self.progress_bar.setVisible(False)
            self.convert_btn.setText("Start Conversion")
            self.convert_btn.setIcon(qta.icon('fa5s.magic', color='#2F4F2F'))
            self.convert_btn.setEnabled(True)
            self.browse_btn.setEnabled(True)
            self.output_dir_btn.setEnabled(True)
            # Don't reset image_paths or drop label - keep the loaded files
            # Don't reset the drop container styling - keep the green background

def main():
    # Fix Windows taskbar grouping
    if sys.platform == "win32":
        import ctypes
        myappid = 'shl.imageconverter.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QApplication(sys.argv)
    app.setApplicationName("SHL Image Converter")
    app.setOrganizationName("SHL")
    app.setApplicationVersion("1.0")
    
    # Set application icon for taskbar
    icon_path = Path(__file__).parent / "img_convert.ico"
    if icon_path.exists():
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)
        # Also set as default icon
        QApplication.setWindowIcon(icon)
    
    # Enable native styling for automatic light/dark mode
    app.setStyle('Fusion')
    
    converter = ImageConverter()
    converter.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()