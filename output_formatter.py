"""
Output Formatter module for presenting batch prediction results.

This module handles the formatting and presentation of batch prediction results
in a clear and structured manner.
"""

import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

logger = logging.getLogger(__name__)

class OutputFormatter:
    """
    Handles formatting and presentation of batch prediction results.
    """
    
    def __init__(self):
        """Initialize the output formatter."""
        self.console = Console()
        logger.debug("Initialized OutputFormatter")
    
    def format_batch_results(self, questions, answers):
        """
        Format batch results into a structured representation.
        
        Args:
            questions (List[str]): The list of input questions
            answers (List[Dict]): The list of answer dictionaries
            
        Returns:
            rich.table.Table: A formatted table of results
        """
        # Create a Rich table with improved formatting
        table = Table(title="Batch Prediction Results", expand=True)
        
        # Add columns
        table.add_column("#", style="cyan", no_wrap=True, width=4)
        table.add_column("Question", style="green", width=30, ratio=2)
        table.add_column("Answer", style="yellow", width=50, ratio=3)
        table.add_column("Metadata", style="blue", width=20, ratio=1)
        table.add_column("Status", style="magenta", width=8)
        
        # Add rows
        for i, (question, answer) in enumerate(zip(questions, answers), 1):
            # Truncate long answers for display
            answer_text = answer.get("answer", "No answer")
            if len(answer_text) > 500:
                answer_text = answer_text[:497] + "..."
            
            # Get metadata
            metadata = {}
            if "response_metadata" in answer:
                metadata = answer["response_metadata"]
            elif "metadata" in answer:  # Fallback for older format
                metadata = answer["metadata"]
            
            # Format metadata for display
            metadata_str = ""
            if metadata:
                if "processing_time" in metadata:
                    metadata_str += f"Time: {metadata['processing_time']:.2f}s\n"
                if "context_length" in metadata:
                    metadata_str += f"Context: {metadata['context_length']} chars\n"
                if "cache_hit" in metadata and metadata["cache_hit"]:
                    metadata_str += f"[bold green]Cache hit[/]\n"
                if "related_indices" in metadata and metadata["related_indices"]:
                    metadata_str += f"Related: {', '.join(str(idx+1) for idx in metadata['related_indices'])}\n"
                if "model" in metadata:
                    model_name = metadata["model"].split('-')[-1] if '-' in metadata["model"] else metadata["model"]
                    metadata_str += f"Model: {model_name}\n"
                if "timestamp" in answer and answer["timestamp"]:
                    metadata_str += f"[bold]TS: {answer['timestamp']}[/]\n"
            
            # Determine status with improved indicators
            status = "[bold green]✓[/]"
            if "error" in answer:
                error_msg = answer["error"]
                status = f"[bold red]✗[/]"
                if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    status = "[bold yellow]⚠[/]"
            
            # Add row to table with improved formatting
            table.add_row(
                str(i),
                question[:100] + "..." if len(question) > 100 else question,
                answer_text,
                metadata_str,
                status
            )
        
        # Add a summary row with batch statistics
        successful = sum(1 for a in answers if "error" not in a)
        table.add_section()
        table.add_row(
            "[bold]Total[/]",
            f"{len(questions)} questions", 
            f"[green]{successful}[/]/[red]{len(questions) - successful}[/] successful/failed",
            f"Cache hits: {sum(1 for a in answers if a.get('response_metadata', {}).get('cache_hit', False))}",
            f"{(successful/len(questions))*100:.0f}%"
        )
        
        # Display the table
        self.console.print(table)
        
        return table
    
    def format_detail_view(self, question, answer):
        """
        Format a detailed view of a single question and answer.
        
        Args:
            question (str): The question
            answer (Dict): The answer dictionary
            
        Returns:
            rich.panel.Panel: A formatted panel with the details
        """
        if "error" in answer:
            # Format error response
            content = f"[bold red]Error:[/] {answer['error']}\n\n"
            content += f"[bold]Question:[/] {question}\n\n"
            if "answer" in answer:
                content += f"[bold]Partial Answer:[/] {answer['answer']}"
            panel = Panel(content, title="Error Response", border_style="red")
        else:
            # Format successful response
            content = f"[bold]Question:[/] {question}\n\n"
            content += f"[bold]Answer:[/] {answer['answer']}\n"
            
            # Add timestamp if available
            if answer.get("timestamp"):
                content += f"\n[bold]Video Timestamp:[/] {answer['timestamp']}"
            
            panel = Panel(content, title="Detailed Response", border_style="green")
        
        return panel
    
    def format_qa_output(self, questions, answers):
        """
        Format results as a simple Question/Answer format with each on a new line.
        
        Args:
            questions (List[str]): The list of input questions
            answers (List[Dict]): The list of answer dictionaries
            
        Returns:
            str: Formatted Q&A text
        """
        output = ""
        
        for question, answer in zip(questions, answers):
            # Get the answer text or error message
            answer_text = "No answer generated."
            if "answer" in answer:
                answer_text = answer["answer"]
            elif "error" in answer:
                answer_text = f"Error: {answer['error']}"
            
            # Format as Question/Answer pair with each on a new line
            output += f"Question: {question}\n"
            output += f"Answer: {answer_text}\n\n"
        
        return output
    
    def format_markdown_output(self, questions, answers):
        """
        Format results as markdown text.
        
        Args:
            questions (List[str]): The list of input questions
            answers (List[Dict]): The list of answer dictionaries
            
        Returns:
            str: Markdown formatted results
        """
        import datetime
        
        # Generate title with timestamp
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        markdown = f"# Batch Prediction Results\n\n"
        markdown += f"*Generated on: {current_time}*\n\n"
        
        # Add summary statistics
        total_questions = len(questions)
        successful = sum(1 for a in answers if "error" not in a)
        cached = sum(1 for a in answers if a.get("response_metadata", {}).get("cache_hit", False) or 
                                          a.get("metadata", {}).get("cache_hit", False))
        
        markdown += "## Summary\n\n"
        markdown += f"- **Total Questions:** {total_questions}\n"
        markdown += f"- **Successfully Answered:** {successful} ({(successful/total_questions)*100:.1f}%)\n"
        markdown += f"- **Cache Hits:** {cached} ({(cached/total_questions)*100:.1f}%)\n"
        
        # Calculate average processing time
        processing_times = []
        for answer in answers:
            metadata = answer.get("response_metadata", answer.get("metadata", {}))
            if "processing_time" in metadata:
                processing_times.append(metadata["processing_time"])
        
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            markdown += f"- **Average Processing Time:** {avg_time:.2f}s\n"
            
        markdown += "\n---\n\n"
        
        # Detail section with all questions and answers
        markdown += "## Detailed Results\n\n"
        
        for i, (question, answer) in enumerate(zip(questions, answers), 1):
            # Get metadata for this answer
            metadata = {}
            if "response_metadata" in answer:
                metadata = answer["response_metadata"]
            elif "metadata" in answer:
                metadata = answer["metadata"]
            
            # Add question header with additional context
            markdown += f"### {i}. {question}\n\n"
            
            # Add metadata section
            markdown += "<details>\n<summary>Metadata</summary>\n\n"
            
            # Print all available metadata in a table format
            markdown += "| Property | Value |\n"
            markdown += "|----------|-------|\n"
            
            # Add special metadata fields
            if answer.get("timestamp"):
                markdown += f"| Video Timestamp | {answer['timestamp']} |\n"
                
            # Include all metadata
            for key, value in metadata.items():
                # Format special metadata items
                if key == "processing_time":
                    markdown += f"| Processing Time | {value:.2f}s |\n"
                elif key == "context_length":
                    markdown += f"| Context Length | {value} chars |\n"
                elif key == "related_indices" and value:
                    related_qs = [str(idx+1) for idx in value]
                    markdown += f"| Related Questions | {', '.join(related_qs)} |\n"
                elif key == "cache_hit" and value:
                    markdown += f"| Cache Hit | ✓ |\n"
                elif key not in ["error", "error_message"]:  # Skip duplicated error info
                    # For any other metadata, just add as is
                    markdown += f"| {key.replace('_', ' ').title()} | {value} |\n"
            
            markdown += "\n</details>\n\n"
            
            # Add the answer or error message
            if "error" in answer:
                markdown += f"**Error:** {answer['error']}\n\n"
            
            if "answer" in answer:
                markdown += f"{answer['answer']}\n\n"
            
            # Include context excerpt if available
            if "context_used" in answer and answer["context_used"]:
                context = answer["context_used"]
                # Truncate long contexts
                if len(context) > 500:
                    context = context[:500] + "..."
                
                markdown += "<details>\n<summary>Context Used</summary>\n\n"
                markdown += f"```\n{context}\n```\n\n"
                markdown += "</details>\n\n"
            
            markdown += "---\n\n"
        
        return markdown
