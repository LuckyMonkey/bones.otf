export interface AnatomyGroup { id: string; label: string; parent: string | null; }
export interface AnatomyRecord {
  id: string; label: string; category: 'bone' | 'organ' | 'tissue'; system: string;
  parent: string | null; paired: boolean; laterality_supported: boolean; laterality: 'left' | 'right' | null;
  review_required: boolean; aliases: string[]; codepoint: string; char: string; ligature: string; shortcode: string; glyph_name: string;
  glyph_base: string; svg: string; color_svg: string; external_ids: Record<string, string>; sources: string[]; accessible_label: string;
}
export const registry: AnatomyRecord[];
export const groups: AnatomyGroup[];
export function get(id: string): AnatomyRecord | null;
export function resolveShortcode(shortcode: string): AnatomyRecord | null;
export function unicodeFor(id: string): string | null;
export function search(query: string): AnatomyRecord[];
