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
