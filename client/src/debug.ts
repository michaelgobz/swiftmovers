import debugPkg from "debug";

/**
 * Will console log prefixed message with timestamp, controlled via env
 * Eg. DEBUG=swiftmovers-dashboard:* - enable all
 *     DEUBG=swiftmovers-dashboard:apps:* - enable apps debugger
 */
export const createDebug = (namespace: string) =>
  debugPkg.debug(`swiftmovers-dashboard:${namespace}`);
