// frontend/app/components/ui/chat/utils/localization.ts
/**
 * Frontend localization utilities for the chatbot.
 * Provides lightweight translation support for UI elements.
 */

export interface SiteIndexTranslations {
  text: string;
  linkText: string;
}

/**
 * Site Index translations for different languages.
 * These match the backend translations to ensure consistency.
 */
const SITE_INDEX_TRANSLATIONS: Record<string, SiteIndexTranslations> = {
  en: {
    text: "If I was unable to give you the information you needed, try searching the Missionary Services Site Index for your topic.",
    linkText: "Site Index",
  },
  es: {
    text: "Si no pude darte la información que necesitabas, intenta buscar en el Índice del Sitio de Servicios Misioneros tu tema.",
    linkText: "Índice del Sitio",
  },
  fr: {
    text: "Si je n'ai pas pu vous donner les informations dont vous aviez besoin, essayez de rechercher votre sujet dans l'Index du Site des Services Missionnaires.",
    linkText: "Index du Site",
  },
  de: {
    text: "Falls ich Ihnen nicht die benötigten Informationen geben konnte, versuchen Sie, Ihr Thema im Site-Index der Missionsdienste zu suchen.",
    linkText: "Site-Index",
  },
  it: {
    text: "Se non sono riuscito a darti le informazioni di cui avevi bisogno, prova a cercare il tuo argomento nell'Indice del Sito dei Servizi Missionari.",
    linkText: "Indice del Sito",
  },
  pt: {
    text: "Se não consegui te dar as informações que você precisava, tente procurar seu tópico no Índice do Site de Serviços Missionários.",
    linkText: "Índice do Site",
  },
  ru: {
    text: "Если я не смог предоставить вам нужную информацию, попробуйте найти вашу тему в Индексе Сайта Миссионерских Служб.",
    linkText: "Индекс Сайта",
  },
  zh: {
    text: "如果我无法为您提供所需的信息，请尝试在传教士服务网站索引中搜索您的主题。",
    linkText: "网站索引",
  },
  ja: {
    text: "必要な情報をお伝えできなかった場合は、宣教師サービスサイトインデックスでトピックを検索してみてください。",
    linkText: "サイトインデックス",
  },
  ko: {
    text: "필요한 정보를 제공해드리지 못했다면, 선교사 서비스 사이트 색인에서 주제를 검색해보세요.",
    linkText: "사이트 색인",
  },
};

/**
 * Simple language detection patterns for frontend use.
 * Based on common words and patterns in different languages.
 */
const LANGUAGE_PATTERNS = {
  es: [
    /\b(el|la|los|las|un|una|de|del|en|con|por|para|que|no|sí|es|son|está|están|pero|como|muy|más|todo|todos|hacer|ver|poder|decir|ir|venir|dar|tener|ser|estar)\b/gi,
    /\b(hola|gracias|por favor|disculpe|perdón|adiós|bueno|malo|grande|pequeño|nuevo|viejo)\b/gi,
    /[ñáéíóúü]/gi,
  ],
  fr: [
    /\b(le|la|les|un|une|de|du|des|en|dans|avec|pour|que|qui|ne|pas|est|sont|être|avoir|faire|aller|voir|savoir|pouvoir|vouloir|dire|donner|prendre)\b/gi,
    /\b(bonjour|merci|s'il vous plaît|excusez-moi|pardon|au revoir|bon|mauvais|grand|petit|nouveau|vieux)\b/gi,
    /[àâäçéèêëïîôùûüÿ]/gi,
  ],
  de: [
    /\b(der|die|das|ein|eine|und|oder|aber|mit|von|zu|auf|für|in|ist|sind|haben|sein|werden|können|müssen|sollen|wollen|gehen|kommen|sehen|sagen|machen)\b/gi,
    /\b(hallo|danke|bitte|entschuldigung|auf wiedersehen|gut|schlecht|groß|klein|neu|alt)\b/gi,
    /[äöüß]/gi,
  ],
  it: [
    /\b(il|la|lo|gli|le|un|una|di|del|della|in|con|per|che|non|è|sono|essere|avere|fare|andare|vedere|sapere|potere|volere|dire|dare|prendere)\b/gi,
    /\b(ciao|grazie|prego|scusi|arrivederci|buono|cattivo|grande|piccolo|nuovo|vecchio)\b/gi,
    /[àèéìíîòóù]/gi,
  ],
  pt: [
    /\b(o|a|os|as|um|uma|de|do|da|em|com|por|para|que|não|é|são|ser|estar|ter|haver|fazer|ir|ver|saber|poder|querer|dizer|dar)\b/gi,
    /\b(olá|obrigado|obrigada|por favor|desculpe|tchau|bom|ruim|grande|pequeno|novo|velho)\b/gi,
    /[àáâãçéêíóôõú]/gi,
  ],
  ru: [
    /[а-яё]/gi,
    /\b(и|в|не|на|я|быть|что|он|с|а|как|это|она|по|но|они|к|у|его|то|из|за|её|до|вы|под|над|при|о|об|от|для)\b/gi,
  ],
  zh: [
    /[\u4e00-\u9fff]/g,
    /[，。！？；：""''（）【】]/g,
  ],
  ja: [
    /[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]/g,
    /[。、！？]/g,
  ],
  ko: [
    /[\uac00-\ud7af]/g,
    /[，。！？]/g,
  ],
};

/**
 * Simple client-side language detection based on text patterns.
 * This is a lightweight alternative to full language detection libraries.
 * @param text - Text to analyze for language detection
 * @param fallback - Fallback language code if detection fails
 * @returns Detected language code or fallback
 */
export function detectLanguage(text: string, fallback = "en"): string {
  if (!text || text.trim().length < 10) {
    return fallback;
  }

  const cleanText = text.toLowerCase();
  const scores: Record<string, number> = {};

  // Initialize scores
  Object.keys(LANGUAGE_PATTERNS).forEach(lang => {
    scores[lang] = 0;
  });

  // Score each language based on pattern matches
  Object.entries(LANGUAGE_PATTERNS).forEach(([lang, patterns]) => {
    patterns.forEach(pattern => {
      const matches = cleanText.match(pattern);
      if (matches) {
        scores[lang] += matches.length;
      }
    });
  });

  // Find the language with the highest score
  let maxScore = 0;
  let detectedLang = fallback;

  Object.entries(scores).forEach(([lang, score]) => {
    if (score > maxScore && score > 2) { // Minimum threshold
      maxScore = score;
      detectedLang = lang;
    }
  });

  return detectedLang;
}

/**
 * Normalize language code to handle variants.
 * @param langCode - Raw language code (e.g., 'zh-cn', 'en-US')
 * @returns Normalized language code (e.g., 'zh', 'en')
 */
function normalizeLanguageCode(langCode?: string): string {
  if (!langCode) {
    return "en";
  }

  // Convert to lowercase and extract base language
  const baseLang = langCode.toLowerCase().split("-")[0].split("_")[0];

  // Handle special cases
  if (baseLang === "zh" || baseLang === "chinese") {
    return "zh";
  }

  return baseLang;
}

/**
 * Get localized Site Index text based on language code.
 * @param languageCode - ISO language code (e.g., 'en', 'es', 'fr')
 * @returns Localized site index translations
 */
export function getSiteIndexTranslations(
  languageCode?: string,
): SiteIndexTranslations {
  const normalizedCode = normalizeLanguageCode(languageCode);

  // Return the translation if available, otherwise fall back to English
  return SITE_INDEX_TRANSLATIONS[normalizedCode] || SITE_INDEX_TRANSLATIONS.en;
}

/**
 * Get localized Site Index text by detecting language from text content.
 * @param text - Text to analyze for language detection
 * @returns Localized site index translations based on detected language
 */
export function getSiteIndexTranslationsFromText(
  text: string,
): SiteIndexTranslations {
  const detectedLanguage = detectLanguage(text);
  return getSiteIndexTranslations(detectedLanguage);
}

/**
 * Check if a language is supported for Site Index translations.
 * @param languageCode - Language code to check
 * @returns True if supported, false otherwise
 */
export function isSiteIndexLanguageSupported(languageCode?: string): boolean {
  if (!languageCode) {
    return false;
  }

  const normalizedCode = normalizeLanguageCode(languageCode);
  return normalizedCode in SITE_INDEX_TRANSLATIONS;
}

/**
 * Get list of all supported languages for Site Index.
 * @returns Array of supported language codes
 */
export function getSupportedSiteIndexLanguages(): string[] {
  return Object.keys(SITE_INDEX_TRANSLATIONS);
}
