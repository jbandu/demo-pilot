'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Pause, Play, MessageCircle, Send, Mic, StopCircle } from 'lucide-react';

interface DemoStatus {
  session_id: string;
  status: string;
  current_step: number;
  total_steps: number;
  progress_percentage: number;
  messages: Array<{
    role: string;
    content: string;
    timestamp: string;
  }>;
}

export default function DemoPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  // Get backend URL from environment (production) or use localhost (development)
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  const wsUrl = backendUrl.replace('https://', 'wss://').replace('http://', 'ws://');

  const [status, setStatus] = useState<DemoStatus | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState('');

  const wsRef = useRef<WebSocket | null>(null);
  const videoRef = useRef<HTMLCanvasElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket(`${wsUrl}/ws/demo/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'video_frame') {
        // Render video frame
        if (videoRef.current) {
          const ctx = videoRef.current.getContext('2d');
          const img = new Image();
          img.onload = () => {
            ctx?.drawImage(img, 0, 0);
          };
          img.src = `data:image/png;base64,${data.data}`;
        }
      } else if (data.type === 'status_update') {
        fetchStatus();
      } else if (data.type === 'message') {
        fetchStatus();
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    // Initial status fetch
    fetchStatus();

    // Poll for status updates
    const interval = setInterval(fetchStatus, 2000);

    return () => {
      ws.close();
      clearInterval(interval);
    };
  }, [sessionId]);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/demo/${sessionId}/status`);
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const handlePauseResume = async () => {
    const action = isPaused ? 'resume' : 'pause';

    try {
      await fetch(`${backendUrl}/api/demo/${sessionId}/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, action }),
      });
      setIsPaused(!isPaused);
    } catch (error) {
      console.error('Error controlling demo:', error);
    }
  };

  const handleStop = async () => {
    try {
      await fetch(`${backendUrl}/api/demo/${sessionId}/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, action: 'stop' }),
      });
      window.location.href = '/';
    } catch (error) {
      console.error('Error stopping demo:', error);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      await fetch(`${backendUrl}/api/demo/${sessionId}/question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, question }),
      });
      setQuestion('');
      setShowChat(true);
    } catch (error) {
      console.error('Error asking question:', error);
    } finally {
      setLoading(false);
    }
  };

  const startVoiceInput = async () => {
    try {
      setRecordingStatus('Requesting microphone access...');

      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Collect audio chunks
      mediaRecorder.addEventListener('dataavailable', (event) => {
        audioChunksRef.current.push(event.data);
      });

      // Handle recording stop
      mediaRecorder.addEventListener('stop', async () => {
        setRecordingStatus('Processing...');

        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

        // Send to backend
        const formData = new FormData();
        formData.append('audio', audioBlob, 'voice-input.webm');

        try {
          const response = await fetch(`${backendUrl}/api/demo/${sessionId}/voice-input`, {
            method: 'POST',
            body: formData,
          });

          const result = await response.json();
          console.log('Voice input processed:', result);

          setRecordingStatus(`You said: "${result.transcribed_text}"`);

          // Clear status after 3 seconds
          setTimeout(() => setRecordingStatus(''), 3000);

        } catch (error) {
          console.error('Error processing voice input:', error);
          setRecordingStatus('Error processing voice input');
          setTimeout(() => setRecordingStatus(''), 3000);
        }

        // Stop all audio tracks
        stream.getTracks().forEach(track => track.stop());
        setIsRecording(false);
      });

      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingStatus('Listening... Click again to stop');

    } catch (error) {
      console.error('Error accessing microphone:', error);
      setRecordingStatus('Microphone access denied');
      setTimeout(() => setRecordingStatus(''), 3000);
    }
  };

  const stopVoiceInput = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setRecordingStatus('Processing your input...');
    }
  };

  const toggleVoiceInput = () => {
    if (isRecording) {
      stopVoiceInput();
    } else {
      startVoiceInput();
    }
  };

  if (!status) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing demo...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">Demo Copilot</h1>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={handlePauseResume}>
                {isPaused ? <Play className="w-4 h-4 mr-2" /> : <Pause className="w-4 h-4 mr-2" />}
                {isPaused ? 'Resume' : 'Pause'}
              </Button>
              <Button variant="outline" size="sm" onClick={handleStop}>
                <StopCircle className="w-4 h-4 mr-2" />
                Stop
              </Button>
            </div>
          </div>

          {/* Progress */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
              <span>Step {status.current_step + 1} of {status.total_steps}</span>
              <span>{status.progress_percentage.toFixed(0)}%</span>
            </div>
            <Progress value={status.progress_percentage} />
          </div>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Video Player */}
          <div className="lg:col-span-2">
            <Card className="p-0 overflow-hidden">
              <div className="bg-black aspect-video relative">
                <canvas
                  ref={videoRef}
                  width={1920}
                  height={1080}
                  className="w-full h-full object-contain"
                />

                {/* Agent Indicator */}
                <div className="absolute bottom-4 left-4 bg-black/70 text-white px-4 py-2 rounded-full flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
                  <span className="text-sm">Demo Copilot is demonstrating...</span>
                </div>
              </div>
            </Card>

            {/* Question Input */}
            <Card className="mt-4 p-4">
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Input
                    placeholder="Ask a question or request a feature..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
                    disabled={isRecording}
                  />
                  <Button onClick={handleAskQuestion} disabled={loading || isRecording}>
                    <Send className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={isRecording ? "default" : "outline"}
                    onClick={toggleVoiceInput}
                    disabled={loading}
                    className={isRecording ? "bg-red-600 hover:bg-red-700 animate-pulse" : ""}
                  >
                    <Mic className="w-4 h-4" />
                  </Button>
                </div>
                {recordingStatus && (
                  <div className="text-sm text-gray-600 flex items-center">
                    {isRecording && (
                      <div className="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse" />
                    )}
                    {recordingStatus}
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Chat Messages */}
            <Card className="p-4">
              <h3 className="font-semibold mb-4 flex items-center">
                <MessageCircle className="w-4 h-4 mr-2" />
                Conversation
              </h3>
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {status.messages.map((msg, idx) => (
                  <div key={idx} className={`${msg.role === 'assistant' ? 'bg-blue-50' : 'bg-gray-50'} p-3 rounded-lg`}>
                    <p className="text-sm font-medium mb-1">
                      {msg.role === 'assistant' ? '🤖 Demo Copilot' : '👤 You'}
                    </p>
                    <p className="text-sm text-gray-700">{msg.content}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
