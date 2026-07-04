// French phone number, optionally with +33 prefix and common separators.
const PHONE_RE = /^(?:\+33|0)[1-9]\d{8}$/;

/** Whether `value` is a valid French phone number (separators allowed). */
export function isValidPhone(value: string): boolean {
  return PHONE_RE.test(value.replace(/[\s.\-()]/g, ""));
}

export const PHONE_HINT = "Format attendu : 06 12 34 56 78";
