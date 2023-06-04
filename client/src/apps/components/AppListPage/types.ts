import { GetV2swiftmoversAppsResponse } from "@dashboard/apps/marketplace.types";
import {
  AppInstallationFragment,
  AppListItemFragment,
} from "@dashboard/graphql";

export interface AppListPageSections {
  appsInstallations?: AppInstallationFragment[];
  installedApps?: AppListItemFragment[];
  installableMarketplaceApps?: GetV2swiftmoversAppsResponse.ReleasedswiftmoversApp[];
  comingSoonMarketplaceApps?: GetV2swiftmoversAppsResponse.ComingSoonswiftmoversApp[];
}
