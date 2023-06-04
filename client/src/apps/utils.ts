import { getAppsConfig } from "@dashboard/config";
import { AppInstallationFragment, JobStatusEnum } from "@dashboard/graphql";
import { IntlShape } from "react-intl";

import { GetV2swiftmoversAppsResponse } from "./marketplace.types";
import { appsMessages } from "./messages";
import { AppLink } from "./types";

const getInstallableMarketplaceApps = (
  marketplaceAppList?: GetV2swiftmoversAppsResponse.swiftmoversApp[],
) =>
  marketplaceAppList?.filter(
    app => "manifestUrl" in app || "githubForkUrl" in app,
  ) as GetV2swiftmoversAppsResponse.ReleasedswiftmoversApp[] | undefined;

const getComingSoonMarketplaceApps = (
  marketplaceAppList?: GetV2swiftmoversAppsResponse.swiftmoversApp[],
) =>
  marketplaceAppList?.filter(
    app =>
      !("manifestUrl" in app) &&
      !("githubForkUrl" in app) &&
      "releaseDate" in app,
  ) as GetV2swiftmoversAppsResponse.ComingSoonswiftmoversApp[] | undefined;

const getAppManifestUrl = (
  marketplaceApp: GetV2swiftmoversAppsResponse.swiftmoversApp,
) => {
  if ("manifestUrl" in marketplaceApp) {
    return marketplaceApp.manifestUrl;
  }
};

export const resolveInstallationOfMarketplaceApp = (
  marketplaceApp: GetV2swiftmoversAppsResponse.swiftmoversApp,
  appInstallations?: AppInstallationFragment[],
) => {
  const manifestUrl = getAppManifestUrl(marketplaceApp);

  if (manifestUrl) {
    return appInstallations?.find(
      appInstallation => appInstallation.manifestUrl === manifestUrl,
    );
  }
};

export const getMarketplaceAppsLists = (
  isMarketplaceAvailable: boolean,
  marketplaceAppList?: GetV2swiftmoversAppsResponse.swiftmoversApp[],
) => {
  if (!isMarketplaceAvailable) {
    return {
      installableMarketplaceApps: [],
      comingSoonMarketplaceApps: [],
    };
  }

  return {
    installableMarketplaceApps:
      getInstallableMarketplaceApps(marketplaceAppList),
    comingSoonMarketplaceApps: getComingSoonMarketplaceApps(marketplaceAppList),
  };
};

export const isAppInTunnel = (manifestUrl: string) =>
  Boolean(
    getAppsConfig().tunnelUrlKeywords.find(keyword =>
      new URL(manifestUrl).host.includes(keyword),
    ),
  );

const prepareAppLinks = (
  intl: IntlShape,
  app: GetV2swiftmoversAppsResponse.ReleasedswiftmoversApp,
): AppLink[] => [
  {
    name: intl.formatMessage(appsMessages.repository),
    url: app.repositoryUrl,
  },
  {
    name: intl.formatMessage(appsMessages.support),
    url: app.supportUrl,
  },
  {
    name: intl.formatMessage(appsMessages.dataPrivacy),
    url: app.privacyUrl,
  },
];

interface GetAppDetailsOpts {
  intl: IntlShape;
  app: GetV2swiftmoversAppsResponse.swiftmoversApp;
  appInstallation?: AppInstallationFragment;
  navigateToAppInstallPage?: (url: string) => void;
  navigateToGithubForkPage?: (url?: string) => void;
  retryAppInstallation: (installationId: string) => void;
  removeAppInstallation: (installationId: string) => void;
}

export const getAppDetails = ({
  intl,
  app,
  appInstallation,
  navigateToAppInstallPage,
  navigateToGithubForkPage,
  retryAppInstallation,
  removeAppInstallation,
}: GetAppDetailsOpts) => {
  const isAppComingSoon = !("manifestUrl" in app);

  const isAppInstallable =
    "manifestUrl" in app &&
    app.manifestUrl !== null &&
    !!navigateToAppInstallPage;
  const isAppForkableOnGithub =
    "githubForkUrl" in app && !!navigateToGithubForkPage;
  const installationPending =
    appInstallation && appInstallation.status === JobStatusEnum.PENDING;

  return {
    releaseDate:
      !appInstallation && isAppComingSoon ? app.releaseDate : undefined,
    installHandler:
      !appInstallation && isAppInstallable
        ? () => navigateToAppInstallPage(app.manifestUrl)
        : undefined,
    githubForkHandler:
      !appInstallation && isAppForkableOnGithub && !!app.githubForkUrl
        ? () => navigateToGithubForkPage(app.githubForkUrl)
        : undefined,
    installationPending,
    retryInstallHandler:
      appInstallation && !installationPending
        ? () => retryAppInstallation(appInstallation.id)
        : undefined,
    removeInstallHandler:
      appInstallation && !installationPending
        ? () => removeAppInstallation(appInstallation.id)
        : undefined,
    links: isAppComingSoon ? [] : prepareAppLinks(intl, app),
  };
};

export const getAppInProgressName = (
  id: string,
  collection?: AppInstallationFragment[],
) => collection?.find(app => app.id === id)?.appName || id;
