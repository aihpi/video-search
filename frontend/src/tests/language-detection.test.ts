import { describe, test, expect } from "vitest";
import { transcribeVideo } from "../services/api";

describe("Language Auto-Detection", () => {
  test("should auto-detect language when language parameter is empty string", async () => {
    // Test with empty string as language parameter (auto-detection)
    const response = await transcribeVideo(
      "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "tiny",
      ""
    );

    // Validate response
    expect(response).toBeDefined();
    expect(response.language).toBe("en"); // Should detect English
    expect(response.text).toContain(
      "This is a mock transcription text in English"
    );
  });

  test("should respect specified language when provided", async () => {
    // Test with a specific language
    const response = await transcribeVideo(
      "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "tiny",
      "de"
    );

    // Validate response
    expect(response).toBeDefined();
    expect(response.language).toBe("de"); // Should use German
    expect(response.text).toContain(
      "Dies ist ein Mock-Transkriptionstext auf Deutsch"
    );
  });

  test("should handle edge cases with language parameter", async () => {
    // Some implementations might handle undefined differently from empty string
    // This is to ensure our implementation handles both cases as auto-detection
    const response = await transcribeVideo(
      "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "tiny",
      // @ts-ignore - We're intentionally testing with undefined
      undefined
    );

    // Validate response
    expect(response).toBeDefined();
    expect(response.language).toBe("en"); // Should default to auto-detection (English)
    expect(response.text).toContain(
      "This is a mock transcription text in English"
    );
  });
});
