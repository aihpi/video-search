import React, { useState } from "react";
import type {
  TranscriptionRequest,
  TranscriptionResponse,
} from "../types/api.types";

interface TranscriptionResultProps {
  result: TranscriptionResponse;
  onNewTranscription: () => void;
}
