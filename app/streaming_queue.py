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

class StreamingQueue:
    """
    Producer-Consumer pattern implementation for streaming text with controlled delays.
    
    This class acts as a "shock absorber" between fast LLM streaming and controlled
    UI animations, allowing immediate response start while maintaining smooth animation.
    """
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.queue = queue.Queue(maxsize=config.queue_size)
        self.producer_thread = None
        self.producer_active = False
        self.producer_error = None
        self.completion_metadata = None
        self._lock = threading.Lock()
        
    def start_producer(self, stream_source: Iterator[Dict[str, Any]]) -> None:
        """
        Start the producer thread that consumes from the LLM stream.
        
        Args:
            stream_source: Iterator yielding chunk data from LLM
        """
        if self.producer_thread and self.producer_thread.is_alive():
            raise RuntimeError("Producer already running")
            
        self.producer_active = True
        self.producer_error = None
        self.completion_metadata = None
        
        def producer_worker():
            try:
                for chunk_data in stream_source:
                    if not self.producer_active:
                        break
                        
                    # Handle answer chunks
                    if chunk_data.get("answer_chunk"):
                        try:
                            self.queue.put(chunk_data, timeout=1.0)
                        except queue.Full:
                            # Handle backpressure - could implement different strategies here
                            print("Warning: Streaming queue full, dropping chunk")
                            continue
                    
                    # Handle completion
                    if chunk_data.get("is_complete"):
                        with self._lock:
                            self.completion_metadata = chunk_data
                        # Signal completion
                        self.queue.put({"_completion": True})
                        break
                        
            except Exception as e:
                with self._lock:
                    self.producer_error = e
                self.queue.put({"_error": str(e)})
            finally:
                self.producer_active = False
                
        self.producer_thread = threading.Thread(target=producer_worker, daemon=True)
        self.producer_thread.start()
    
    def consume_with_animation(self, ui_callback: Callable[[str, str], None]) -> Dict[str, Any]:
        """
        Consume from queue with controlled animation timing.
        
        Args:
            ui_callback: Function to call for UI updates, receives (new_chunk, accumulated_text)
            
        Returns:
            Final response metadata
        """
        accumulated_text = ""
        pending_chunks = []
        
        # First, collect chunks while they're coming in fast
        while True:
            try:
                # Check for producer error
                with self._lock:
                    if self.producer_error:
                        raise RuntimeError(f"Producer error: {self.producer_error}")
                
                # Get item from queue with short timeout for responsive collection
                try:
                    item = self.queue.get(timeout=0.05)
                except queue.Empty:
                    # If queue is empty and we have pending chunks, start animation
                    if pending_chunks:
                        break
                    # Check if producer is still active
                    if not self.producer_active and self.queue.empty():
                        break
                    continue
                
                # Handle special control messages
                if "_completion" in item:
                    break
                elif "_error" in item:
                    raise RuntimeError(f"Stream error: {item['_error']}")
                
                # Collect answer chunks
                if "answer_chunk" in item:
                    chunk_text = item["answer_chunk"]
                    accumulated_text += chunk_text
                    pending_chunks.append(chunk_text)
                    
                    # For instant mode, update immediately
                    if self.config.mode == StreamingMode.INSTANT:
                        ui_callback(chunk_text, accumulated_text)
                
            except Exception as e:
                return {
                    "error": str(e),
                    "final_text": accumulated_text
                }
        
        # Now animate the pending chunks for character/word modes
        if self.config.mode != StreamingMode.INSTANT and pending_chunks:
            self._animate_pending_chunks(pending_chunks, ui_callback)
        
        # Continue collecting any remaining chunks while animating
        while self.producer_active or not self.queue.empty():
            try:
                item = self.queue.get(timeout=0.1)
                
                if "_completion" in item:
                    break
                elif "_error" in item:
                    raise RuntimeError(f"Stream error: {item['_error']}")
                elif "answer_chunk" in item:
                    chunk_text = item["answer_chunk"]
                    accumulated_text += chunk_text
                    
                    if self.config.mode == StreamingMode.INSTANT:
                        ui_callback(chunk_text, accumulated_text)
                    else:
                        # Animate this chunk immediately
                        self._animate_chunk(chunk_text, ui_callback)
                        
            except queue.Empty:
                continue
            except Exception as e:
                return {
                    "error": str(e),
                    "final_text": accumulated_text
                }
        
        # Return completion metadata
        with self._lock:
            if self.completion_metadata:
                result = self.completion_metadata.copy()
                result["final_text"] = accumulated_text
                return result
            else:
                return {"final_text": accumulated_text}
    
    def _animate_pending_chunks(self, chunks: list, ui_callback: Callable[[str, str], None]) -> None:
        """Animate collected chunks based on mode"""
        if self.config.mode == StreamingMode.CHARACTER:
            for chunk in chunks:
                self._animate_chunk(chunk, ui_callback)
        elif self.config.mode == StreamingMode.WORD:
            # Combine chunks and split by words for word-level animation
            full_text = "".join(chunks)
            words = full_text.split()
            for word in words:
                ui_callback(word + " ", "")  # Pass word with space
                if self.config.delay > 0:
                    time.sleep(self.config.delay)
    
    def _animate_chunk(self, chunk: str, ui_callback: Callable[[str, str], None]) -> None:
        """Animate a single chunk based on current mode"""
        if self.config.mode == StreamingMode.CHARACTER:
            for char in chunk:
                ui_callback(char, "")
                if self.config.delay > 0:
                    time.sleep(self.config.delay)
        elif self.config.mode == StreamingMode.WORD:
            words = chunk.split()
            for word in words:
                ui_callback(word + " ", "")
                if self.config.delay > 0:
                    time.sleep(self.config.delay)
    
    def stop(self) -> None:
        """Stop the producer thread gracefully"""
        self.producer_active = False
        if self.producer_thread and self.producer_thread.is_alive():
            self.producer_thread.join(timeout=2.0)
    
    def is_active(self) -> bool:
        """Check if producer is still active"""
        return self.producer_active or not self.queue.empty()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status for debugging"""
        return {
            "queue_size": self.queue.qsize(),
            "producer_active": self.producer_active,
            "has_error": self.producer_error is not None,
            "thread_alive": self.producer_thread.is_alive() if self.producer_thread else False
        }

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
        chunk_queue = queue.Queue(maxsize=100)
        producer_finished = threading.Event()
        producer_error = [None]  # Use list for mutable reference
        completion_metadata = [None]
        
        def producer_worker():
            """Producer thread that feeds the queue"""
            try:
                for chunk_data in stream_source:
                    if chunk_data.get("answer_chunk"):
                        try:
                            chunk_queue.put(chunk_data, timeout=1.0)
                        except queue.Full:
                            print("Warning: Queue full, dropping chunk")
                            continue
                    
                    if chunk_data.get("is_complete"):
                        completion_metadata[0] = chunk_data
                        break
                        
            except Exception as e:
                producer_error[0] = e
            finally:
                producer_finished.set()
        
        # Start producer thread
        producer_thread = threading.Thread(target=producer_worker, daemon=True)
        producer_thread.start()
        
        # Consumer logic (runs in main thread)
        accumulated_text = ""
        display_text = ""
        
        try:
            while not producer_finished.is_set() or not chunk_queue.empty():
                try:
                    # Get chunk with timeout
                    chunk_data = chunk_queue.get(timeout=0.1)
                    
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
