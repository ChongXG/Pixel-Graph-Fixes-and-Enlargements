import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSlider, QPushButton, QFileDialog, QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image

class ImageResizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("像素风图片修复工具")
        self.setGeometry(100, 100, 600, 500)
        
        # 初始化UI
        self.initUI()
        
        # 初始化变量
        self.original_image = None
        self.modified_image = None
        self.image_path = ""
        
    def initUI(self):
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 第一行：图片预览框
        preview_layout = QHBoxLayout()
        
        # 原图预览框
        self.original_preview = QLabel()
        self.original_preview.setAlignment(Qt.AlignCenter)
        self.original_preview.setStyleSheet("""
            border: 2px solid #3498db; 
            background-color: #f0f0f0;
            border-radius: 5px;
        """)
        self.original_preview.setText("原图预览")
        self.original_preview.setMinimumSize(300, 300)
        self.original_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 处理后预览框
        self.modified_preview = QLabel()
        self.modified_preview.setAlignment(Qt.AlignCenter)
        self.modified_preview.setStyleSheet("""
            border: 2px solid #e74c3c; 
            background-color: #f0f0f0;
            border-radius: 5px;
        """)
        self.modified_preview.setText("处理后预览")
        self.modified_preview.setMinimumSize(300, 300)
        self.modified_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        preview_layout.addWidget(self.original_preview)
        preview_layout.addWidget(self.modified_preview)
        main_layout.addLayout(preview_layout, stretch=1)
        
        # 控制面板区域
        control_panel = QWidget()
        control_panel.setStyleSheet("""
            background-color: #ecf0f1; 
            padding: 10px;
            border-radius: 5px;
        """)
        control_layout = QVBoxLayout(control_panel)
        
        # 宽度调节条 (8-256)
        width_control = QWidget()
        width_layout = QHBoxLayout(width_control)
        
        width_label = QLabel("缩小宽度 (8-256):")
        width_label.setFixedWidth(120)
        
        
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(8, 256)
        self.width_slider.setValue(128)
        self.width_slider.valueChanged.connect(self.update_image)
        self.width_slider.setStyleSheet("""
            QSlider {
                min-height: 25px;  /* 滑块轨道最小高度 */
            }
            /* 滑槽样式 */
            QSlider::groove:horizontal {
                height: 10px;       /* 滑槽高度 */
                background: #d3d3d3; /* 默认滑槽颜色 */
            }
            /* 滑块手柄样式 */
            QSlider::handle:horizontal {
                width: 15px;       /* 手柄宽度 */
                height: 10px;      /* 手柄高度 */
                margin: -5px 0;    /* 垂直居中 */
                background: white;
                border: 2px solid #3498db; /* 蓝色边框 */
                border-radius: 8px; /* 圆形手柄 */
            }
            /* 手柄悬停效果 */
            QSlider::handle:horizontal:hover {
                background: #f0f0f0;
                border: 2px solid #2980b9; /* 深蓝色 */
            }
        """)
        
        self.width_value = QLabel(str(self.width_slider.value()))
        self.width_value.setFixedWidth(40)
        self.width_slider.valueChanged.connect(lambda v: self.width_value.setText(str(v)))
        
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_slider)
        width_layout.addWidget(self.width_value)
        
        control_layout.addWidget(width_control)
        
        # 信息显示区域
        info_panel = QWidget()
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(0, 0, 0, 10)
        
        self.original_res_label = QLabel("原图分辨率: 未导入")
        self.original_res_label.setStyleSheet("""
            color: #2980b9; 
            font-weight: bold;
            padding: 2px;
        """)
        
        self.process_info_label = QLabel("处理流程: 未开始")
        self.process_info_label.setStyleSheet("""
            color: #f39c12; 
            font-weight: bold;
            padding: 2px;
        """)
        
        info_layout.addWidget(self.original_res_label)
        info_layout.addWidget(self.process_info_label)
        
        control_layout.addWidget(info_panel)
        
        # 按钮区域（水平排列）
        button_panel = QWidget()
        button_layout = QHBoxLayout(button_panel)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 按钮统一样式
        button_style = """
            QPushButton {
                padding: 8px 15px;
                min-width: 80px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #95a5a6;
            }
        """
        
        # 导入按钮
        self.import_btn = QPushButton("导入图片")
        self.import_btn.setStyleSheet(button_style + """
            background-color: #3498db;
            color: white;
        """)
        self.import_btn.clicked.connect(self.import_image)
        
        # 四个导出按钮
        self.export_btn_1080 = QPushButton("导出 1080px")
        self.export_btn_1080.setStyleSheet(button_style)
        self.export_btn_1080.clicked.connect(lambda: self.export_image(1080))
        self.export_btn_1080.setEnabled(False)
        
        self.export_btn_2160 = QPushButton("导出 2160px")
        self.export_btn_2160.setStyleSheet(button_style)
        self.export_btn_2160.clicked.connect(lambda: self.export_image(2160))
        self.export_btn_2160.setEnabled(False)
        
        self.export_btn_3240 = QPushButton("导出 3240px")
        self.export_btn_3240.setStyleSheet(button_style)
        self.export_btn_3240.clicked.connect(lambda: self.export_image(3240))
        self.export_btn_3240.setEnabled(False)
        
        self.export_btn_4320 = QPushButton("导出 4320px")
        self.export_btn_4320.setStyleSheet(button_style)
        self.export_btn_4320.clicked.connect(lambda: self.export_image(4320))
        self.export_btn_4320.setEnabled(False)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.export_btn_1080)
        button_layout.addWidget(self.export_btn_2160)
        button_layout.addWidget(self.export_btn_3240)
        button_layout.addWidget(self.export_btn_4320)
        button_layout.addStretch()
        
        control_layout.addWidget(button_panel)
        
        main_layout.addWidget(control_panel)
    
    def import_image(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", script_dir, "图片文件 (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image_path = file_path
            try:
                self.original_image = Image.open(file_path).convert("RGB")
                width, height = self.original_image.size
                self.original_res_label.setText(f"原图分辨率: {width}×{height}")
                self.process_info_label.setText("处理流程: 已导入原图")
                self.display_original_image()
                self.update_image()
                # 启用所有导出按钮
                self.export_btn_1080.setEnabled(True)
                self.export_btn_2160.setEnabled(True)
                self.export_btn_3240.setEnabled(True)
                self.export_btn_4320.setEnabled(True)
            except Exception as e:
                print(f"加载图片失败: {e}")
    
    def display_original_image(self):
        if self.original_image:
            qimage = QImage(self.original_image.tobytes(), 
                          self.original_image.width, 
                          self.original_image.height, 
                          self.original_image.width * 3, 
                          QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            scaled_pixmap = pixmap.scaled(self.original_preview.size(), Qt.KeepAspectRatio)
            self.original_preview.setPixmap(scaled_pixmap)
    
    def update_image(self):
        if not self.original_image:
            return
            
        downscale_width = self.width_slider.value()
        original_width, original_height = self.original_image.size
        downscale_height = int(original_height * (downscale_width / original_width))
        
        try:
            downscaled_img = self.original_image.resize((downscale_width, downscale_height), Image.NEAREST)
            self.modified_image = downscaled_img
            
            qimage = QImage(downscaled_img.tobytes(), 
                          downscaled_img.width, 
                          downscaled_img.height, 
                          downscaled_img.width * 3, 
                          QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            
            scaled_pixmap = pixmap.scaled(
                self.modified_preview.size(), 
                Qt.KeepAspectRatio, 
                Qt.FastTransformation
            )
            self.modified_preview.setPixmap(scaled_pixmap)
            
            process_text = f"处理流程: {original_width}×{original_height} → {downscale_width}×{downscale_height}"
            self.process_info_label.setText(process_text)
            
        except Exception as e:
            print(f"处理图片失败: {e}")
    
    def export_image(self, target_width):
        if not self.modified_image:
            return
            
        # 计算目标高度（保持宽高比）
        original_width, original_height = self.original_image.size
        downscale_width = self.width_slider.value()
        downscale_height = int(original_height * (downscale_width / original_width))
        target_height = int(downscale_height * (target_width / downscale_width))
        
        # 使用NEAREST插值放大到目标尺寸
        upscaled_img = self.modified_image.resize((target_width, target_height), Image.NEAREST)
        
        # 生成默认文件名：原文件名_分辨率.扩展名
        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        ext = os.path.splitext(self.image_path)[1]
        default_name = f"{base_name}_{target_width}x{target_height}{ext}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            f"保存图片 ({target_width}×{target_height})", 
            default_name,  # 设置默认文件名
            "PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg)"
        )
        
        if file_path:
            try:
                # 修复导出的图片质量问题，强制最高质量
                if file_path.lower().endswith(('.png')):
                    upscaled_img.save(file_path, 'PNG', compress_level=0)  # 无压缩
                elif file_path.lower().endswith(('.jpg', '.jpeg')):
                    upscaled_img.save(file_path, 'JPEG', quality=100, subsampling=0)
                self.process_info_label.setText(
                    f"{self.process_info_label.text()} → 已导出 {target_width}×{target_height}"
                )
            except Exception as e:
                print(f"保存图片失败: {e}")
    
    def resizeEvent(self, event):
        if self.original_image:
            self.display_original_image()
            self.update_image()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageResizerApp()
    window.show()
    sys.exit(app.exec_())