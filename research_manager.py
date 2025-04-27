import sys
import os
import json
import markdown
from datetime import datetime
import zipfile
from io import BytesIO
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QMessageBox, QFileDialog,
    QInputDialog, QLabel, QPlainTextEdit, QLineEdit, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from reportlab.pdfgen import canvas
from laboratory import AgentLaboratory
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

class ConsoleOutput(QPlainTextEdit):
    """Widget to display console output."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumHeight(150)
        self.setMaximumHeight(200)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: Consolas, monospace;
                font-size: 10pt;
                border: 1px solid #333333;
                padding: 5px;
            }
        """)

class ResearchThread(QThread):
    """Thread for running research to keep GUI responsive."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    console_output = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, api_key, topic, focus_areas):
        super().__init__()
        self.api_key = api_key
        self.topic = topic
        self.focus_areas = focus_areas
    
    def emit_output(self, text):
        """Helper to emit output in chunks."""
        self.console_output.emit(text)
        self.progress.emit(text)
    
    def run(self):
        try:
            # Create a custom stdout to capture output
            class CustomStdout:
                def __init__(self, callback):
                    self.callback = callback
                    self.buffer = ""
                
                def write(self, text):
                    self.buffer += text
                    if '\n' in self.buffer:
                        lines = self.buffer.split('\n')
                        for line in lines[:-1]:
                            self.callback(line + '\n')
                        self.buffer = lines[-1]
                
                def flush(self):
                    if self.buffer:
                        self.callback(self.buffer)
                        self.buffer = ""
            
            # Redirect stdout
            old_stdout = sys.stdout
            sys.stdout = CustomStdout(self.emit_output)
            
            try:
                # Initialize and run research
                self.emit_output("Initializing research process...\n")
                lab = AgentLaboratory(api_key=self.api_key, model_name="gpt-4o")
                
                self.emit_output(f"Starting research on topic: {self.topic}\n")
                task_notes = {
                    "focus_areas": [area.strip() for area in self.focus_areas.split(",")],
                    "experiment_preferences": {
                        "dataset_size": "small",
                        "model_complexity": "medium",
                        "evaluation_metrics": ["accuracy", "perplexity"]
                    }
                }
                
                results = lab.conduct_research(self.topic, task_notes)
                self.emit_output("\nResearch completed successfully!\n")
                self.finished.emit(results)
                
            finally:
                # Restore stdout
                sys.stdout = old_stdout
                
        except Exception as e:
            self.error.emit(str(e))

class ResearchManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dirk's Agent Laboratory Research Lab")
        self.setGeometry(100, 100, 1200, 800)
        
        # Load saved research results
        self.results_file = "research_results.json"
        self.results = self.load_results()
        
        self.init_ui()
    
    def init_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        # Add logo
        logo_label = QLabel()
        pixmap = QPixmap("agentlabsmall.png")
        scaled_pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setStyleSheet("padding: 5px;")
        header_layout.addWidget(logo_label)
        
        # Add title and subtitle in a vertical layout
        title_layout = QVBoxLayout()
        
        # Add title
        title = QLabel("Dirk's Agent Laboratory Research Lab")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24pt;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title)
        
        # Add subtitle
        subtitle = QLabel("Advanced Research Assistant")
        subtitle.setStyleSheet("QLabel { color: #CCCCCC; font-size: 12pt; }")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()  # Add stretch to push everything to the left
        
        main_layout.addWidget(header)
        
        # Create horizontal layout for panels
        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(10)
        
        # Left panel for list of research entries
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title for left panel
        left_title = QLabel("Research Projects")
        left_title.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 5px;")
        left_layout.addWidget(left_title)
        
        # Add "New Research" button
        new_research_btn = QPushButton("New Research")
        new_research_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        new_research_btn.clicked.connect(self.start_new_research)
        left_layout.addWidget(new_research_btn)
        
        # Add list widget for research entries
        self.research_list = QListWidget()
        self.research_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: black;
            }
        """)
        self.research_list.currentRowChanged.connect(self.show_research)
        left_layout.addWidget(self.research_list)
        
        # Right panel for research content
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title for content area
        content_title = QLabel("Research Results")
        content_title.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 5px;")
        right_layout.addWidget(content_title)
        
        # Add text display area
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 10px;
                background-color: white;
            }
        """)
        right_layout.addWidget(self.content_display)
        
        # Add export and delete buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        for btn_text, slot, color in [
            ("Export as Markdown", lambda: self.export_research("md"), "#2196F3"),
            ("Export as Text", lambda: self.export_research("txt"), "#2196F3"),
            ("Export as PDF", lambda: self.export_research("pdf"), "#2196F3"),
            ("Export All as ZIP (MD)", lambda: self.export_all_research("md"), "#009688"),
            ("Export All as ZIP (TXT)", lambda: self.export_all_research("txt"), "#009688"),
            ("Export All as ZIP (PDF)", lambda: self.export_all_research("pdf"), "#009688"),
            ("Delete Research", self.delete_research, "#F44336")
        ]:
            btn = QPushButton(btn_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 8px;
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {color.replace(')', ', 0.8)')};
                }}
            """)
            btn.clicked.connect(slot)
            button_layout.addWidget(btn)
        
        right_layout.addLayout(button_layout)
        
        # Add panels to horizontal layout
        panels_layout.addWidget(left_panel, 1)
        panels_layout.addWidget(right_panel, 2)
        
        # Add panels layout to main layout
        main_layout.addLayout(panels_layout)
        
        # Add footer
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        footer_layout = QHBoxLayout(footer)
        
        # Add company info
        company_info = QLabel(
            "© 2024 AI Engineering | "
            "<a href='https://ai-engineering.ai'>ai-engineering.ai</a>"
        )
        company_info.setOpenExternalLinks(True)
        company_info.setStyleSheet("""
            QLabel {
                color: #666666;
            }
            QLabel a {
                color: #2196F3;
                text-decoration: none;
            }
        """)
        footer_layout.addWidget(company_info)
        
        # Add author info
        author_info = QLabel(
            "Created by Dirk Wonhoefer | "
            "<a href='mailto:dirk.wonhoefer@ai-engineering.ai'>dirk.wonhoefer@ai-engineering.ai</a>"
        )
        author_info.setOpenExternalLinks(True)
        author_info.setStyleSheet("""
            QLabel {
                color: #666666;
            }
            QLabel a {
                color: #2196F3;
                text-decoration: none;
            }
        """)
        footer_layout.addWidget(author_info, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addWidget(footer)
        
        # Add console title
        console_title = QLabel("Research Progress")
        console_title.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 5px;")
        main_layout.addWidget(console_title)
        
        # Add console output area at the bottom
        self.console_output = ConsoleOutput()
        main_layout.addWidget(self.console_output)
        
        # Update research list
        self.update_research_list()
        
        # Initial console message
        self.console_output.appendPlainText("Welcome to Dirk's Agent Laboratory Research Lab\n")
        self.console_output.appendPlainText("Developed by AI Engineering (ai-engineering.ai)\n")
        self.console_output.appendPlainText("Click 'New Research' to start a new research project\n")

    def load_results(self):
        """Load saved research results from file."""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_results(self):
        """Save research results to file."""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f)
    
    def update_research_list(self):
        """Update the list of research entries."""
        self.research_list.clear()
        for result in self.results:
            self.research_list.addItem(f"Research #{result['id']}: {result['topic']}")
    
    def show_research(self, row):
        """Display selected research content."""
        if row >= 0 and row < len(self.results):
            result = self.results[row]
            content = f"# Research #{result['id']}: {result['topic']}\n\n"
            content += f"Date: {result['date']}\n\n"
            content += f"Focus Areas: {', '.join(result['focus_areas'])}\n\n"
            content += "## Research Results\n\n"
            content += result['final_report']
            self.content_display.setMarkdown(content)
    
    def start_new_research(self):
        """Start a new research project."""
        # Get API key from config first
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('api_key', '')
        except:
            api_key = ''
        
        # Get API key
        api_key, ok = QInputDialog.getText(
            self, "API Key", "Enter your OpenAI API key:", 
            QLineEdit.EchoMode.Password,
            api_key
        )
        if not ok or not api_key:
            return
            
        # Get research topic
        topic, ok = QInputDialog.getText(
            self, "Research Topic", "Enter your research topic:"
        )
        if not ok or not topic:
            return
            
        # Get focus areas
        focus_areas, ok = QInputDialog.getText(
            self, "Focus Areas", "Enter focus areas (comma-separated):"
        )
        if not ok or not focus_areas:
            return
        
        # Clear console output
        self.console_output.clear()
        self.console_output.appendPlainText("Starting new research project...\n")
        
        # Create and start research thread
        self.research_thread = ResearchThread(api_key, topic, focus_areas)
        self.research_thread.finished.connect(lambda results: self.research_completed(
            results, topic, focus_areas
        ))
        self.research_thread.error.connect(self.research_error)
        self.research_thread.console_output.connect(self.update_console)
        self.research_thread.progress.connect(lambda msg: self.console_output.appendPlainText(msg))
        self.research_thread.start()
        
        self.console_output.appendPlainText("Research process initialized. Please wait...\n")
    
    def update_console(self, text):
        """Update the console output."""
        self.console_output.appendPlainText(text)
        # Scroll to bottom
        scrollbar = self.console_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def research_completed(self, results, topic, focus_areas):
        """Handle completed research."""
        # Create new research entry
        new_id = len(self.results) + 1
        entry = {
            "id": new_id,
            "topic": topic,
            "focus_areas": [area.strip() for area in focus_areas.split(",")],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "final_report": results["final_report"]
        }
        
        # Add to results and save
        self.results.append(entry)
        self.save_results()
        self.update_research_list()
        
        # Show the new research
        self.research_list.setCurrentRow(len(self.results) - 1)
        
        QMessageBox.information(
            self, "Research Complete",
            "Research has been completed and saved."
        )
    
    def research_error(self, error_msg):
        """Handle research errors."""
        QMessageBox.critical(
            self, "Research Error",
            f"An error occurred during research:\n{error_msg}"
        )
    
    def export_research(self, format_type):
        """Export research in specified format."""
        current_row = self.research_list.currentRow()
        if current_row < 0:
            return
            
        result = self.results[current_row]
        content = f"# Research #{result['id']}: {result['topic']}\n\n"
        content += f"Date: {result['date']}\n\n"
        content += f"Focus Areas: {', '.join(result['focus_areas'])}\n\n"
        content += "## Research Results\n\n"
        content += result['final_report']
        
        # Get save location
        file_filter = {
            "md": "Markdown Files (*.md)",
            "txt": "Text Files (*.txt)",
            "pdf": "PDF Files (*.pdf)"
        }[format_type]
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Research", "", file_filter
        )
        
        if not filename:
            return
            
        try:
            if format_type in ["md", "txt"]:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            elif format_type == "pdf":
                # Create PDF document
                doc = SimpleDocTemplate(
                    filename,
                    pagesize=letter,
                    rightMargin=72,
                    leftMargin=72,
                    topMargin=72,
                    bottomMargin=72
                )
                
                # Create styles
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    spaceAfter=30
                )
                heading_style = ParagraphStyle(
                    'CustomHeading',
                    parent=styles['Heading2'],
                    fontSize=14,
                    spaceAfter=20
                )
                normal_style = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=12
                )
                
                # Build content
                story = []
                
                # Add title and metadata
                story.append(Paragraph(f"Research #{result['id']}: {result['topic']}", title_style))
                story.append(Paragraph(f"Date: {result['date']}", normal_style))
                story.append(Paragraph(f"Focus Areas: {', '.join(result['focus_areas'])}", normal_style))
                story.append(Spacer(1, 20))
                
                # Add research results with proper formatting
                story.append(Paragraph("Research Results", heading_style))
                
                # Split content into paragraphs and add them
                paragraphs = result['final_report'].split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        # Check if it's a heading (starts with ##)
                        if para.startswith('##'):
                            story.append(Paragraph(para.replace('#', '').strip(), heading_style))
                        else:
                            story.append(Paragraph(para, normal_style))
                
                # Build the PDF
                doc.build(story)
            
            QMessageBox.information(
                self, "Export Complete",
                f"Research has been exported as {format_type.upper()}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error",
                f"Error exporting research:\n{str(e)}"
            )
    
    def delete_research(self):
        """Delete selected research entry."""
        current_row = self.research_list.currentRow()
        if current_row < 0:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this research?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.results.pop(current_row)
            self.save_results()
            self.update_research_list()
            self.content_display.clear()
    
    def export_all_research(self, format_type):
        """Export all research entries as a ZIP file."""
        if not self.results:
            QMessageBox.warning(self, "No Research", "There are no research entries to export.")
            return
        
        # Get save location for ZIP file
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save All Research", "", "ZIP Files (*.zip)"
        )
        
        if not filename:
            return
        
        try:
            # Create ZIP file
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for result in self.results:
                    # Generate content
                    content = f"# Research #{result['id']}: {result['topic']}\n\n"
                    content += f"Date: {result['date']}\n\n"
                    content += f"Focus Areas: {', '.join(result['focus_areas'])}\n\n"
                    content += "## Research Results\n\n"
                    content += result['final_report']
                    
                    # Create safe filename
                    safe_topic = "".join(c for c in result['topic'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    base_filename = f"research_{result['id']}_{safe_topic[:30]}"
                    
                    if format_type in ["md", "txt"]:
                        # Add text file directly to ZIP
                        zipf.writestr(
                            f"{base_filename}.{format_type}",
                            content
                        )
                    elif format_type == "pdf":
                        # Create PDF in memory
                        pdf_buffer = BytesIO()
                        doc = SimpleDocTemplate(
                            pdf_buffer,
                            pagesize=letter,
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=72
                        )
                        
                        # Create styles
                        styles = getSampleStyleSheet()
                        title_style = ParagraphStyle(
                            'CustomTitle',
                            parent=styles['Heading1'],
                            fontSize=16,
                            spaceAfter=30
                        )
                        heading_style = ParagraphStyle(
                            'CustomHeading',
                            parent=styles['Heading2'],
                            fontSize=14,
                            spaceAfter=20
                        )
                        normal_style = ParagraphStyle(
                            'CustomNormal',
                            parent=styles['Normal'],
                            fontSize=11,
                            spaceAfter=12
                        )
                        
                        # Build content
                        story = []
                        story.append(Paragraph(f"Research #{result['id']}: {result['topic']}", title_style))
                        story.append(Paragraph(f"Date: {result['date']}", normal_style))
                        story.append(Paragraph(f"Focus Areas: {', '.join(result['focus_areas'])}", normal_style))
                        story.append(Spacer(1, 20))
                        story.append(Paragraph("Research Results", heading_style))
                        
                        # Split content into paragraphs
                        paragraphs = result['final_report'].split('\n\n')
                        for para in paragraphs:
                            if para.strip():
                                if para.startswith('##'):
                                    story.append(Paragraph(para.replace('#', '').strip(), heading_style))
                                else:
                                    story.append(Paragraph(para, normal_style))
                        
                        # Build PDF
                        doc.build(story)
                        
                        # Add PDF to ZIP
                        zipf.writestr(f"{base_filename}.pdf", pdf_buffer.getvalue())
                        pdf_buffer.close()
            
            QMessageBox.information(
                self, "Export Complete",
                f"All research entries have been exported as {format_type.upper()} files in the ZIP archive."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error",
                f"Error exporting research:\n{str(e)}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = ResearchManager()
    manager.show()
    sys.exit(app.exec()) 