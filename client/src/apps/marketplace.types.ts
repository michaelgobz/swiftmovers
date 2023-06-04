// eslint-disable-next-line @typescript-eslint/no-namespace
export namespace GetV2swiftmoversAppsResponse {
  export interface swiftmoversAppBase {
    name: {
      en: string;
    };
    description: {
      en: string;
    };
    logo: {
      source: string | null;
      color: string;
    };
    integrations: Array<{
      name: string;
      logo: {
        light: {
          source: string;
        };
        dark: {
          source: string;
        };
      };
    }>;
  }

  export type ReleasedswiftmoversApp = swiftmoversAppBase & {
    repositoryUrl: string;
    supportUrl: string;
    privacyUrl: string;
    manifestUrl: string | null;
    githubForkUrl?: string;
  };

  export type ComingSoonswiftmoversApp = swiftmoversAppBase & {
    releaseDate: string;
  };

  export type swiftmoversApp = ReleasedswiftmoversApp | ComingSoonswiftmoversApp;
}
