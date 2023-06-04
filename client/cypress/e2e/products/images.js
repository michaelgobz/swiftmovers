/// <reference types="cypress"/>
/// <reference types="../../support"/>

import { PRODUCT_DETAILS } from "../../elements/catalog/products/product-details";
import { SHARED_ELEMENTS } from "../../elements/shared/sharedElements";
import { demoProductsNames } from "../../fixtures/products";
import { productDetailsUrl } from "../../fixtures/urlList";
import { getFirstProducts } from "../../support/api/requests/Product";
import { deleteCollectionsStartsWith } from "../../support/api/utils/catalog/collectionsUtils";
import {
  createNewProductWithNewDataAndDefaultChannel,
  deleteProductsStartsWith,
  iterateThroughThumbnails,
} from "../../support/api/utils/products/productsUtils";

describe("Tests for images", () => {
  beforeEach(() => {
    cy.clearSessionData().loginUserViaRequest();
  });

  it(
    "Should display product image",
    { tags: ["@products", "@allEnv", "@stable"] },
    () => {
      getFirstProducts(1, demoProductsNames.carrotJuice)
        .then(resp => {
          const product = resp[0].node;
          cy.visit(productDetailsUrl(product.id))
            .get(PRODUCT_DETAILS.productImage)
            .find("img")
            .invoke("attr", "src");
        })
        .then(imageUrl => {
          cy.request(imageUrl);
        })
        .then(imageResp => {
          expect(imageResp.status).to.equal(200);
        });
    },
  );

  it(
    "Should upload saved image",
    { tags: ["@products", "@allEnv", "@stable"] },
    () => {
      const name = "CyImages";

      deleteProductsStartsWith(name);
      deleteCollectionsStartsWith(name);
      cy.clearSessionData().loginUserViaRequest();
      createNewProductWithNewDataAndDefaultChannel({ name })
        .then(({ product }) => {
          cy.visit(productDetailsUrl(product.id))
            .waitForProgressBarToNotBeVisible()
            .get(PRODUCT_DETAILS.uploadImageButton)
            .click()
            .get(PRODUCT_DETAILS.uploadSavedImagesButton)
            .click()
            .get(SHARED_ELEMENTS.fileInput)
            .attachFile("images/swiftmoversDemoProductSneakers.png")
            .get(PRODUCT_DETAILS.productImage)
            .find("img")
            .invoke("attr", "src");
        })
        .then(imageUrl => {
          cy.request(imageUrl);
        })
        .then(imageResp => {
          expect(imageResp.status).to.equal(200);
        });
    },
  );

  it(
    "should create thumbnail url after entering image url",
    { tags: ["@products", "@allEnv", "@stable"] },
    () => {
      let failedRequests;
      getFirstProducts(100)
        .then(products => {
          const productsWithThumbnails = products.filter(
            product => product.node.thumbnail !== null,
          );
          failedRequests = iterateThroughThumbnails(productsWithThumbnails);
        })
        .then(() => {
          if (failedRequests && failedRequests.length > 0) {
            throw new Error(failedRequests.join("\n"));
          }
        });
    },
  );
});
