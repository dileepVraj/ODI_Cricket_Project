/**
 * Strips emoji Unicode characters from manifest label strings.
 * The manifest retains emoji for API consumers; the UI renders clean text.   
 */
export function stripEmoji(str: string): string {
  return str
    .replace(/[\u{1F000}-\u{1FFFF}]/gu, '')
    .replace(/[\u{2600}-\u{27BF}]/gu,   '')
    .replace(/[\u{FE00}-\u{FE0F}]/gu,   '')
    .replace(/[\u{1F900}-\u{1F9FF}]/gu, '')
    .replace(/[\u{1FA00}-\u{1FAFF}]/gu, '')
    .replace(/\uFE0F/g, '')
    .replace(/\u200D/g, '')
    .trim();
}
