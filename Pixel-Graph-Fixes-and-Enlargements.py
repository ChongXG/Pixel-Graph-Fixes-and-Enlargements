import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSlider, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image
import numpy as np

class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片分辨率调节工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化变量
        self.original_image = None
        self.processed_image = None
        self.current_resolution = 64  # 默认分辨率
        
        # 创建主控件和布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        # 创建顶部控制区域
        self.create_controls()
        
        # 创建图片显示区域
        self.create_image_display()
        
        # 创建信息标签
        self.create_info_labels()
        
        # 初始化UI状态
        self.update_ui_state()
    
    def create_controls(self):
        """创建控制按钮和滑块"""
        control_layout = QHBoxLayout()
        
        # 导入按钮
        self.import_btn = QPushButton("导入图片")
        self.import_btn.clicked.connect(self.import_image)
        control_layout.addWidget(self.import_btn)
        
        # 导出按钮
        self.export_btn = QPushButton("导出图片")
        self.export_btn.clicked.connect(self.export_image)
        control_layout.addWidget(self.export_btn)
        
        # 分辨率滑块
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("目标分辨率:"))
        
        self.resolution_slider = QSlider(Qt.Horizontal)
        self.resolution_slider.setMinimum(32)
        self.resolution_slider.setMaximum(128)
        self.resolution_slider.setValue(64)
        self.resolution_slider.setTickInterval(16)
        self.resolution_slider.setTickPosition(QSlider.TicksBelow)
        self.resolution_slider.valueChanged.connect(self.update_resolution)
        resolution_layout.addWidget(self.resolution_slider)
        
        self.resolution_label = QLabel("64")
        resolution_layout.addWidget(self.resolution_label)
        
        control_layout.addLayout(resolution_layout)
        
        self.main_layout.addLayout(control_layout)
    
    def create_image_display(self):
        """创建图片显示区域"""
        image_layout = QHBoxLayout()
        
        # 原始图片预览
        self.original_image_label = QLabel()
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setStyleSheet("border: 2px solid gray;")
        self.original_image_label.setFixedSize(500, 500)
        image_layout.addWidget(self.original_image_label)
        
        # 处理后的图片预览
        self.processed_image_label = QLabel()
        self.processed_image_label.setAlignment(Qt.AlignCenter)
        self.processed_image_label.setStyleSheet("border: 2px solid gray;")
        self.processed_image_label.setFixedSize(500, 500)
        image_layout.addWidget(self.processed_image_label)
        
        self.main_layout.addLayout(image_layout)
    
    def create_info_labels(self):
        """创建信息显示标签"""
        info_layout = QVBoxLayout()
        
        # 原始图片信息
        self.original_info_label = QLabel("原始图片: 未加载")
        info_layout.addWidget(self.original_info_label)
        
        # 处理后图片信息
        self.processed_info_label = QLabel("处理后图片: 无")
        info_layout.addWidget(self.processed_info_label)
        
        # 处理信息
        self.process_info_label = QLabel("")
        info_layout.addWidget(self.process_info_label)
        
        self.main_layout.addLayout(info_layout)
    
    def update_ui_state(self):
        """根据当前状态更新UI元素"""
        has_image = self.original_image is not None
        self.export_btn.setEnabled(has_image)
        self.resolution_slider.setEnabled(has_image)
    
    def import_image(self):
        """导入图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # 使用Pillow打开图片
                self.original_image = Image.open(file_path)
                
                # 显示原始图片
                self.display_original_image()
                
                # 处理图片
                self.process_image()
                
                # 更新UI状态
                self.update_ui_state()
                
                # 更新原始图片信息
                width, height = self.original_image.size
                self.original_info_label.setText(
                    f"原始图片: {width}×{height} ({file_path.split('/')[-1]})"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法加载图片: {str(e)}")
    
    def export_image(self):
        """导出处理后的图片"""
        if self.processed_image is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图片", "", "PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg)"
        )
        
        if file_path:
            try:
                self.processed_image.save(file_path)
                QMessageBox.information(self, "成功", "图片已成功导出!")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存图片: {str(e)}")
    
    def update_resolution(self, value):
        """更新分辨率设置并重新处理图片"""
        self.current_resolution = value
        self.resolution_label.setText(str(value))
        
        if self.original_image is not None:
            self.process_image()
    
    def display_original_image(self):
        """显示原始图片"""
        if self.original_image is None:
            return
            
        # 将Pillow图像转换为QPixmap
        qimage = self.pillow_to_qimage(self.original_image)
        pixmap = QPixmap.fromImage(qimage)
        
        # 缩放以适应预览框，保持宽高比
        scaled_pixmap = pixmap.scaled(
            self.original_image_label.width() - 10,
            self.original_image_label.height() - 10,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.original_image_label.setPixmap(scaled_pixmap)
    
    def display_processed_image(self):
        """显示处理后的图片"""
        if self.processed_image is None:
            return
            
        # 将Pillow图像转换为QPixmap
        qimage = self.pillow_to_qimage(self.processed_image)
        pixmap = QPixmap.fromImage(qimage)
        
        # 缩放以适应预览框，保持宽高比
        scaled_pixmap = pixmap.scaled(
            self.processed_image_label.width() - 10,
            self.processed_image_label.height() - 10,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.processed_image_label.setPixmap(scaled_pixmap)
        
        # 更新处理后图片信息
        width, height = self.processed_image.size
        self.processed_info_label.setText(
            f"处理后图片: {width}×{height} (降低到{self.current_resolution}px后放大到1080×1080)"
        )
    
    def process_image(self):
        if self.original_image is None:
            return
            
        try:
            # 计算新的尺寸，保持宽高比
            original_width, original_height = self.original_image.size
            aspect_ratio = original_width / original_height
            
            if original_width > original_height:
                new_width = self.current_resolution
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = self.current_resolution
                new_width = int(new_height * aspect_ratio)
            
            # 降低分辨率
            resized_img = self.original_image.resize(
                (new_width, new_height),
                Image.Resampling.NEAREST
            )
            
            # 放大到1080×1080
            final_width, final_height = 1080, 1080
            if aspect_ratio > 1:  # 宽大于高
                final_height = int(final_width / aspect_ratio)
            else:  # 高大于宽
                final_width = int(final_height * aspect_ratio)
            
            self.processed_image = resized_img.resize(
                (final_width, final_height),
                Image.Resampling.NEAREST
            )
            
            # 显示处理后的图片
            self.display_processed_image()
            
            # 更新处理信息
            self.process_info_label.setText(
                f"处理过程: {original_width}×{original_height} → "
                f"{new_width}×{new_height} → "
                f"{final_width}×{final_height}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"图片处理失败: {str(e)}")
    
    def pillow_to_qimage(self, pil_image):
        """将Pillow图像转换为QImage（修复颜色问题）"""
        # 转换为RGB模式（如果是RGBA，会丢弃alpha通道）
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        elif pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 获取图像数据
        data = pil_image.tobytes('raw', 'RGB')
        
        # 创建QImage
        qimage = QImage(data, pil_image.size[0], pil_image.size[1], QImage.Format_RGB888)
        
        # 确保数据在QImage生命周期内保持有效
        qimage.data = data
        
        return qimage

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec_())