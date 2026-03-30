import asyncio
import base64
import json
import numpy as np
import sounddevice as sd

from voice.voicelive_client import VoiceLiveClient
from agent.farmer_agent import FarmerAgent
from tools.tool_registry import registry


class Runtime:

    def __init__(self):

        self.voice = VoiceLiveClient()
        self.agent = FarmerAgent()

        self.audio_chunks = []
        self.audio_queue = asyncio.Queue()
        
        # Track pending function calls
        self.pending_calls = {}
        
        # Track response state to avoid conflicts
        self.response_in_progress = False
        
        # Flag to pause audio capture during playback (prevent echo)
        self._is_playing = False
        
        # Flag to disconnect after final response (set by end_conversation tool)
        self._pending_disconnect = False
        
        # Flag to stop loops on shutdown
        self._running = True


    async def start(self):

        await self.voice.connect()

        instructions = self.agent.get_instructions()
        tools = registry.get_schemas()

        await self.voice.send({
            "type": "session.update",
            "session": {
                "instructions": instructions,
                "voice": "shimmer",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.8,
                    "prefix_padding_ms": 500,
                    "silence_duration_ms": 1500
                },
                "tools": tools,
                "tool_choice": "auto"
            }
        })
        
        print(f"\n🛠️  Loaded {len(tools)} tools: {[t['name'] for t in tools]}")

        print("\n🎤 Conversational agent started.\n")

        loop = asyncio.get_event_loop()
        
        # Track audio sending for feedback
        self.audio_send_count = 0

        stream = sd.InputStream(
            samplerate=24000,
            channels=1,
            dtype="int16",
            blocksize=4800,  # 200ms chunks for stability
            callback=lambda indata, frames, time, status:
                loop.call_soon_threadsafe(
                    self.audio_queue.put_nowait, indata.copy()
                )
        )

        stream.start()
        print("🎙️  Microphone active")
        
        # Trigger initial greeting - for onboarding recovery call
        await self.voice.send({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user", 
                "content": [{"type": "input_text", "text": "Start the call now. Greet the farmer warmly and ask language preference (Hindi or Marathi). After greeting, you MUST STOP and WAIT SILENTLY until farmer clearly says 'Hindi' or 'Marathi' or speaks in one of these languages. Do NOT assume their choice. Do NOT continue until you hear their clear response."}]
            }
        })
        await self.voice.send({"type": "response.create"})
        print("🗣️  Calling farmer...")

        await asyncio.gather(
            self.send_audio_loop(),
            self.listen()
        )


    async def send_audio_loop(self):

        while self._running:

            try:
                indata = await asyncio.wait_for(self.audio_queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            
            if not self._running:
                break
            
            # Skip sending audio while agent is speaking (prevents echo)
            if self._is_playing:
                continue
            
            # Visual feedback every 25 chunks (~5 seconds)
            self.audio_send_count += 1
            if self.audio_send_count % 25 == 0:
                print(".", end="", flush=True)

            audio_bytes = indata.tobytes()

            encoded = base64.b64encode(audio_bytes).decode()

            try:
                await self.voice.send({
                    "type": "input_audio_buffer.append",
                    "audio": encoded
                })
            except Exception:
                # Connection closed, stop loop
                break


    async def handle_function_call(self, call_id: str, name: str, arguments: str):
        """Execute a function call and send result back to Voice Live."""
        
        try:
            args = json.loads(arguments) if arguments else {}
            print(f"   Args: {args}")
            
            # Execute the tool
            result = registry.execute(name, args)
            result_dict = json.loads(result) if isinstance(result, str) else result
            print(f"   ✅ Result received")
            
            # Send function result back to Voice Live
            await self.voice.send({
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": result
                }
            })
            
            # Continue with the response (this is needed after function calls)
            await self.voice.send({
                "type": "response.create"
            })
            
            # Handle conversation end - wait for final response then disconnect
            if name == "end_conversation" and result_dict.get("should_disconnect"):
                print("   🔚 Conversation ending - will disconnect after final response")
                self._pending_disconnect = True
            
        except Exception as e:
            print(f"   ❌ Tool error: {e}")
            await self.voice.send({
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps({"error": str(e)})
                }
            })
            await self.voice.send({
                "type": "response.create"
            })


    async def listen(self):

        async for event in self.voice.receive():

            event_type = event.get("type")
            
            # Only log important events (not audio deltas or transcription deltas)
            if event_type not in ["response.audio.delta", "input_audio_buffer.speech_started", 
                                   "response.audio_transcript.delta", "input_audio_buffer.speech_stopped",
                                   "conversation.item.input_audio_transcription.completed"]:
                print(f"\n📨 {event_type}")

            if event_type == "session.created":
                print("✅ Session created")

            elif event_type == "session.updated":
                print("✅ Session configured")

            # Server VAD handles commit and response.create automatically
            # We just track the state
            elif event_type == "input_audio_buffer.speech_started":
                print("🎙️  [Listening...]")
                
            elif event_type == "input_audio_buffer.speech_stopped":
                print("⏳ Processing speech...")
                # Server VAD auto-commits and creates response - don't do it manually!
            
            elif event_type == "conversation.item.input_audio_transcription.completed":
                # This shows what the user actually said
                transcript = event.get("transcript", "").strip()
                
                # Common Whisper hallucinations when it hears silence/noise
                hallucination_phrases = [
                    "thank you", "thanks", "bye", "goodbye", "thanks for watching",
                    "see you", "okay", "ok", "hello", "hi", "hmm", "uh", "um"
                ]
                
                is_likely_hallucination = (
                    len(transcript) < 15 and 
                    any(h in transcript.lower() for h in hallucination_phrases)
                )
                
                if transcript:
                    if is_likely_hallucination:
                        print(f"⚠️  [Possible noise/hallucination: \"{transcript}\"]")
                    else:
                        print(f"👤 User: {transcript}")
                else:
                    print("⚠️  [No speech detected or unclear audio]")

            elif event_type == "response.created":
                self.response_in_progress = True
                print("🤖 Assistant: ", end="", flush=True)

            elif event_type == "response.done":
                self.response_in_progress = False
                print("")  # New line after response

                if self.audio_chunks:
                    # Pause mic capture during playback to prevent echo
                    self._is_playing = True
                    
                    audio_bytes = b"".join(self.audio_chunks)
                    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
                    sd.play(audio_np, samplerate=24000)
                    sd.wait()
                    self.audio_chunks = []
                    
                    # Clear any audio that was captured during playback (echo)
                    while not self.audio_queue.empty():
                        try:
                            self.audio_queue.get_nowait()
                        except:
                            break
                    
                    # Clear the input buffer on Voice Live side too
                    await self.voice.send({"type": "input_audio_buffer.clear"})
                    
                    # Longer delay after playback to let echo fade completely
                    await asyncio.sleep(0.5)
                    self._is_playing = False
                    print("🎙️  [Your turn to speak...]")
                
                # If conversation should end, disconnect gracefully
                if self._pending_disconnect:
                    print("\n👋 Conversation ended. Disconnecting...")
                    self._running = False  # Stop the audio loop
                    await asyncio.sleep(0.1)  # Give audio loop time to exit
                    await self.voice.disconnect()
                    return  # Exit the listen loop

            # Handle function calls
            elif event_type == "response.output_item.added":
                item = event.get("item", {})
                if item.get("type") == "function_call":
                    call_id = item.get("call_id")
                    name = item.get("name")
                    self.pending_calls[call_id] = {"name": name, "arguments": ""}
                    print(f"🔧 Calling: {name}")

            elif event_type == "response.function_call_arguments.delta":
                call_id = event.get("call_id")
                if call_id in self.pending_calls:
                    self.pending_calls[call_id]["arguments"] += event.get("delta", "")

            elif event_type == "response.function_call_arguments.done":
                call_id = event.get("call_id")
                if call_id in self.pending_calls:
                    call_info = self.pending_calls.pop(call_id)
                    await self.handle_function_call(
                        call_id,
                        call_info["name"],
                        call_info["arguments"]
                    )

            elif event_type == "response.audio_transcript.delta":
                print(event.get("delta", ""), end="", flush=True)

            elif event_type == "response.audio.delta":
                chunk = base64.b64decode(event["delta"])
                self.audio_chunks.append(chunk)
            
            elif event_type == "error":
                error_info = event.get("error", {})
                print(f"❌ {error_info.get('message', error_info)}")