import { GetV2swiftmoversAppsResponse } from "@dashboard/apps/marketplace.types";
import { AppInstallation, InstalledApp } from "@dashboard/apps/types";
import {
  AppInstallationFragment,
  AppListItemFragment,
} from "@dashboard/graphql";

import { AppListPageSections } from "./types";

export const resolveSectionsAvailability = ({
  appsInstallations,
  installedApps,
  installableMarketplaceApps,
  comingSoonMarketplaceApps,
}: AppListPageSections) => ({
  installed:
    !installedApps ||
    !!installedApps.length ||
    !appsInstallations ||
    !!appsInstallations.length,
  all: !installableMarketplaceApps || !!installableMarketplaceApps.length,
  comingSoon: !comingSoonMarketplaceApps || !!comingSoonMarketplaceApps.length,
});

const findAppInMarketplace = (
  manifestUrl: string | null,
  installableMarketplaceApps?: GetV2swiftmoversAppsResponse.ReleasedswiftmoversApp[],
) => {
  if (!manifestUrl) {
    return undefined;
  }

  return installableMarketplaceApps?.find(
    app => app.manifestUrl === manifestUrl,
  );
};

export const getVerifiedInstalledApps = (
  installedApps?: AppListItemFragment[],
  installableMarketplaceApps?: GetV2swiftmoversAppsResponse.ReleasedswiftmoversApp[],
): InstalledApp[] | undefined =>
  installedApps?.map(app => {
    const marketplaceApp = findAppInMarketplace(
      app.manifestUrl,
      installableMarketplaceApps,
    );

    return {
      app,
      isExternal: !marketplaceApp,
      logo: marketplaceApp?.logo,
    };
  });

export const getVerifiedAppsInstallations = (
  appsInstallations?: AppInstallationFragment[],
  installableMarketplaceApps?: GetV2swiftmoversAppsResponse.ReleasedswiftmoversApp[],
): AppInstallation[] | undefined =>
  appsInstallations?.map(appInstallation => {
    const marketplaceApp = findAppInMarketplace(
      appInstallation.manifestUrl,
      installableMarketplaceApps,
    );

    return {
      appInstallation,
      isExternal: !marketplaceApp,
      logo: marketplaceApp?.logo,
    };
  });

/*
 * Temporary solution for checking if app is not installed.
 * Installed app list is paginated, it needs to be replace in the future with proper solution,
 * not relying on one page of installed apps list.
 */
const isAppNotInstalled = (
  manifestUrl: string,
  installedApps?: AppListItemFragment[],
) => installedApps?.every(app => app.manifestUrl !== manifestUrl);

export const getVerifiedInstallableMarketplaceApps = (
  installedApps?: AppListItemFragment[],
  installableMarketplaceApps?: GetV2swiftmoversAppsResponse.ReleasedswiftmoversApp[],
): GetV2swiftmoversAppsResponse.ReleasedswiftmoversApp[] | undefined =>
  installableMarketplaceApps?.filter(app =>
    isAppNotInstalled(app.manifestUrl, installedApps),
  );
