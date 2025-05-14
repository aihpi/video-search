import { http, HttpResponse } from 'msw';
import type { TranscriptionResponse } from '../../types/api.types';

// Mock response for auto language detection
const mockAutoDetectResponse: TranscriptionResponse = {
  id: 'mock-id-123',
  audioUrl: '/audio/mock-id-123.mp3',
  language: 'en', // Auto-detected language (English)
  text: "This is a mock transcription text in English.",
  segments: [
    { id: 0, start: 0, end: 5, text: "This is a mock" },
    { id: 1, start: 5, end: 10, text: "transcription text in English." }
  ]
};

// Mock response for specific language selection
const mockGermanResponse: TranscriptionResponse = {
  id: 'mock-id-456',
  audioUrl: '/audio/mock-id-456.mp3',
  language: 'de',
  text: "Dies ist ein Mock-Transkriptionstext auf Deutsch.",
  segments: [
    { id: 0, start: 0, end: 5, text: "Dies ist ein" },
    { id: 1, start: 5, end: 10, text: "Mock-Transkriptionstext auf Deutsch." }
  ]
};

export const handlers = [
  // Handler for auto language detection
  http.post('http://localhost:9091/transcribe-video', async ({ request }) => {
    const body = await request.json() as { 
      videoUrl: string; 
      model?: string;
      language?: string | null;
    };
    
    // If language is null or empty string, return auto-detected response
    if (body.language === null || body.language === '') {
      return HttpResponse.json(mockAutoDetectResponse);
    }
    
    // If language is specifically set to German
    if (body.language === 'de') {
      return HttpResponse.json(mockGermanResponse);
    }
    
    // Default response
    return HttpResponse.json(mockAutoDetectResponse);
  }),
];