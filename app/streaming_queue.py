"""
Streaming Queue Implementation for DoqToq

This module implements a producer-consumer pattern for smooth streaming animations
in Streamlit, acting as a "shock absorber" between fast LLM responses and 
controlled UI animations.
"""

import threading
import queue
import time
import re
from typing import Dict, Any, Optional, Iterator, Callable
from dataclasses import dataclass
from enum import Enum

class StreamingMode(Enum):
    CHARACTER = "character"
    WORD = "word"
    INSTANT = "instant"

class LaTeXBuffer:
    """
    Smart buffer for LaTeX mathematical expressions during streaming.
    Prevents partial LaTeX from being rendered during character-by-character streaming.
    """
    
    def __init__(self):
        self.buffer = ""
        self.in_block_math = False
        self.in_inline_math = False
        self.block_math_pattern = re.compile(r'\$\$.*?\$\$', re.DOTALL)
        self.inline_math_pattern = re.compile(r'\$[^$]+\$')
        
    def add_character(self, char: str) -> tuple[str, bool]:
        """
        Add a character to the buffer and return (text_to_display, should_display)
        
        Returns:
            tuple: (text_to_display, should_display_now)
        """
        self.buffer += char
        
        # Check for block math delimiters
        if char == '$':
            if self.buffer.endswith('$$'):
                if not self.in_block_math:
                    # Starting block math
                    self.in_block_math = True
                    return "", False  # Don't display yet
                else:
                    # Ending block math
                    self.in_block_math = False
                    # Return the complete block math expression
                    result = self.buffer
                    self.buffer = ""
                    return result, True
            elif not self.in_block_math:
                if not self.in_inline_math:
                    # Starting inline math
                    self.in_inline_math = True
                    return "", False  # Don't display yet
                else:
                    # Ending inline math
                    self.in_inline_math = False
                    # Return the complete inline math expression
                    result = self.buffer
                    self.buffer = ""
                    return result, True
        
        # If we're inside math, buffer everything
        if self.in_block_math or self.in_inline_math:
            return "", False
        
        # Not in math, return the character immediately
        result = self.buffer
        self.buffer = ""
        return result, True
    
    def add_text(self, text: str) -> str:
        """
        Add text and return what should be displayed immediately.
        For word-by-word streaming, we process complete words.
        """
        self.buffer += text
        
        # Check if we have complete math expressions
        display_text = ""
        remaining_text = self.buffer
        
        # Process block math first
        while True:
            match = self.block_math_pattern.search(remaining_text)
            if not match:
                break
            
            # Add text before the math
            display_text += remaining_text[:match.start()]
            # Add the complete math expression
            display_text += match.group()
            # Continue with remaining text
            remaining_text = remaining_text[match.end():]
        
        # Process inline math
        while True:
            match = self.inline_math_pattern.search(remaining_text)
            if not match:
                break
                
            # Add text before the math
            display_text += remaining_text[:match.start()]
            # Add the complete math expression
            display_text += match.group()
            # Continue with remaining text
            remaining_text = remaining_text[match.end():]
        
        # Check if remaining text contains partial math
        has_partial_block = '$$' in remaining_text and remaining_text.count('$$') % 2 == 1
        has_partial_inline = '$' in remaining_text and not has_partial_block and remaining_text.count('$') % 2 == 1
        
        if has_partial_block or has_partial_inline:
            # Keep partial math in buffer
            self.buffer = remaining_text
        else:
            # No partial math, display everything
            display_text += remaining_text
            self.buffer = ""
            
        return display_text
    
    def flush(self) -> str:
        """Return any remaining buffered content"""
        result = self.buffer
        self.buffer = ""
        return result

@dataclass
class StreamingConfig:
    """Configuration for streaming behavior"""
    mode: StreamingMode
    delay: float  # Delay between characters/words in seconds
    queue_size: int = 100  # Maximum queue size
    polling_interval: float = 0.01  # How often to check queue in main thread
    producer_timeout: float = 30.0  # How long to wait for producer to finish
    queue_timeout: float = 5.0  # Timeout for individual queue operations

class StreamlitStreamingManager:
    """
    Streamlit-specific wrapper for StreamingQueue that handles UI state management.
    
    This class provides a simpler approach that works better with Streamlit's execution model.
    """
    
    def __init__(self):
        self.config = None
        
    def process_streamed_response(self, stream_source: Iterator[Dict[str, Any]], 
                                message_placeholder, quill_icon: str,
                                streaming_mode: str, streaming_delay: float) -> Dict[str, Any]:
        """
        Process streaming response with queue-based shock absorber pattern.
        
        This method implements the producer-consumer pattern in a Streamlit-friendly way.
        """
        # Create configuration
        mode_map = {
            "character": StreamingMode.CHARACTER,
            "word": StreamingMode.WORD,
            "instant": StreamingMode.INSTANT
        }
        mode = mode_map.get(streaming_mode, StreamingMode.CHARACTER)
        self.config = StreamingConfig(mode=mode, delay=streaming_delay)
        
        # Use queue for shock absorber pattern
        chunk_queue = queue.Queue(maxsize=1000)
        producer_finished = threading.Event()
        producer_error = [None]  # Use list for mutable reference
        completion_metadata = [None]
        
        def producer_worker():
            """Producer thread that feeds the queue"""
            try:
                for chunk_data in stream_source:
                    if chunk_data.get("answer_chunk"):
                        try:
                            chunk_queue.put(chunk_data, timeout=self.config.queue_timeout)
                        except queue.Full:
                            print("Warning: Queue full, dropping chunk")
                            continue
                    
                    if chunk_data.get("is_complete"):
                        completion_metadata[0] = chunk_data
                        break
                        
            except Exception as e:
                producer_error[0] = e
                print(f"Producer error: {e}")
            finally:
                producer_finished.set()
        
        # Start producer thread
        producer_thread = threading.Thread(target=producer_worker, daemon=True)
        producer_thread.start()
        
        # Consumer logic (runs in main thread)
        accumulated_text = ""
        display_text = ""
        latex_buffer = LaTeXBuffer()
        start_time = time.time()
        max_total_time = 300.0  # 5 minutes maximum total time
        
        try:
            while not producer_finished.is_set() or not chunk_queue.empty():
                # Check for overall timeout
                if time.time() - start_time > max_total_time:
                    producer_error[0] = Exception("Total processing time exceeded 5 minutes")
                    break
                    
                try:
                    # Get chunk with timeout
                    chunk_data = chunk_queue.get(timeout=0.5)  # Increased from 0.1 to 0.5
                    
                    if chunk_data.get("answer_chunk"):
                        chunk_text = chunk_data["answer_chunk"]
                        accumulated_text += chunk_text
                        
                        if mode == StreamingMode.INSTANT:
                            # Instant mode - update immediately
                            display_text = accumulated_text
                            message_placeholder.markdown(
                                display_text + f"<img src='data:image/png;base64,{quill_icon}' style='width: 40px; height: 40px; display: inline; vertical-align: bottom; transform: translateY(-5px);'>",
                                unsafe_allow_html=True
                            )
                        elif mode == StreamingMode.CHARACTER:
                            # Character mode - animate each character with LaTeX awareness
                            for char in chunk_text:
                                char_to_display, should_display = latex_buffer.add_character(char)
                                if should_display and char_to_display:
                                    display_text += char_to_display
                                    message_placeholder.markdown(
                                        display_text + f"<img src='data:image/png;base64,{quill_icon}' style='width: 40px; height: 40px; display: inline; vertical-align: bottom; transform: translateY(-5px);'>",
                                        unsafe_allow_html=True
                                    )
                                    if streaming_delay > 0:
                                        time.sleep(streaming_delay)
                        elif mode == StreamingMode.WORD:
                            # Word mode - animate each word with LaTeX awareness
                            words_to_display = latex_buffer.add_text(chunk_text)
                            if words_to_display:
                                words = words_to_display.split()
                                for i, word in enumerate(words):
                                    if display_text and not display_text.endswith(" "):
                                        display_text += " " + word
                                    else:
                                        display_text += word
                                        
                                    message_placeholder.markdown(
                                        display_text + f"<img src='data:image/png;base64,{quill_icon}' style='width: 40px; height: 40px; display: inline; vertical-align: bottom; transform: translateY(-5px);'>",
                                        unsafe_allow_html=True
                                    )
                                    if i < len(words) - 1 and streaming_delay > 0:
                                        time.sleep(streaming_delay)
                
                except queue.Empty:
                    continue
                except Exception as e:
                    producer_error[0] = e
                    break
            
            # Flush any remaining LaTeX content
            remaining_latex = latex_buffer.flush()
            if remaining_latex:
                display_text += remaining_latex
            
            # Wait for producer to finish
            producer_thread.join(timeout=2.0)
            
            # Check for errors
            if producer_error[0]:
                return {
                    "error": str(producer_error[0]),
                    "final_text": accumulated_text,
                    "answer": accumulated_text
                }
            
            # Return success result
            result = completion_metadata[0] if completion_metadata[0] else {}
            result.update({
                "final_text": accumulated_text,
                "answer": accumulated_text
            })
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "final_text": accumulated_text,
                "answer": accumulated_text
            }

# Utility functions for easy integration

def create_streaming_config(streaming_mode: str, streaming_delay: float) -> StreamingConfig:
    """Create StreamingConfig from chat interface parameters"""
    mode_map = {
        "character": StreamingMode.CHARACTER,
        "word": StreamingMode.WORD,
        "instant": StreamingMode.INSTANT
    }
    
    mode = mode_map.get(streaming_mode, StreamingMode.CHARACTER)
    return StreamingConfig(mode=mode, delay=streaming_delay)

def handle_streamed_response(stream_source: Iterator[Dict[str, Any]], 
                           message_placeholder, quill_icon: str,
                           streaming_mode: str, streaming_delay: float) -> Dict[str, Any]:
    """
    High-level function to handle streaming with the new queue system.
    
    This is the main integration point for the chat interface.
    """
    manager = StreamlitStreamingManager()
    return manager.process_streamed_response(
        stream_source=stream_source,
        message_placeholder=message_placeholder,
        quill_icon=quill_icon,
        streaming_mode=streaming_mode,
        streaming_delay=streaming_delay
    )
