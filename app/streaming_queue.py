"""
Streaming Queue Implementation for DoqToq

This module implements a producer-consumer pattern for smooth streaming animations
in Streamlit, acting as a "shock absorber" between fast LLM responses and 
controlled UI animations.
"""

import threading
import queue
import time
from typing import Dict, Any, Optional, Iterator, Callable
from dataclasses import dataclass
from enum import Enum

class StreamingMode(Enum):
    CHARACTER = "character"
    WORD = "word"
    INSTANT = "instant"

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
                            # Character mode - animate each character
                            for char in chunk_text:
                                display_text += char
                                message_placeholder.markdown(
                                    display_text + f"<img src='data:image/png;base64,{quill_icon}' style='width: 40px; height: 40px; display: inline; vertical-align: bottom; transform: translateY(-5px);'>",
                                    unsafe_allow_html=True
                                )
                                if streaming_delay > 0:
                                    time.sleep(streaming_delay)
                        elif mode == StreamingMode.WORD:
                            # Word mode - animate each word
                            words = chunk_text.split()
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
