# Generated by Django 3.2.19 on 2023-06-04 17:14

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('page', '0001_initial'),
        ('attribute', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributevariant',
            name='assigned_variants',
            field=models.ManyToManyField(blank=True, related_name='attributesrelated', through='attribute.AssignedVariantAttribute', to='product.ProductVariant'),
        ),
        migrations.AddField(
            model_name='attributevariant',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributevariant', to='attribute.attribute'),
        ),
        migrations.AddField(
            model_name='attributevariant',
            name='product_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributevariant', to='product.producttype'),
        ),
        migrations.AddField(
            model_name='attributevaluetranslation',
            name='attribute_value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='attribute.attributevalue'),
        ),
        migrations.AddField(
            model_name='attributevalue',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='attribute.attribute'),
        ),
        migrations.AddField(
            model_name='attributevalue',
            name='reference_page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='references', to='page.page'),
        ),
        migrations.AddField(
            model_name='attributevalue',
            name='reference_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='references', to='product.product'),
        ),
        migrations.AddField(
            model_name='attributevalue',
            name='reference_variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='references', to='product.productvariant'),
        ),
        migrations.AddField(
            model_name='attributetranslation',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='attribute.attribute'),
        ),
        migrations.AddField(
            model_name='attributeproduct',
            name='assigned_products',
            field=models.ManyToManyField(blank=True, related_name='attributesrelated', through='attribute.AssignedProductAttribute', to='product.Product'),
        ),
        migrations.AddField(
            model_name='attributeproduct',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributeproduct', to='attribute.attribute'),
        ),
        migrations.AddField(
            model_name='attributeproduct',
            name='product_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributeproduct', to='product.producttype'),
        ),
        migrations.AddField(
            model_name='attributepage',
            name='assigned_pages',
            field=models.ManyToManyField(blank=True, related_name='attributesrelated', through='attribute.AssignedPageAttribute', to='page.Page'),
        ),
        migrations.AddField(
            model_name='attributepage',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributepage', to='attribute.attribute'),
        ),
        migrations.AddField(
            model_name='attributepage',
            name='page_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributepage', to='page.pagetype'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='page_types',
            field=models.ManyToManyField(blank=True, related_name='page_attributes', through='attribute.AttributePage', to='page.PageType'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='product_types',
            field=models.ManyToManyField(blank=True, related_name='product_attributes', through='attribute.AttributeProduct', to='product.ProductType'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='product_variant_types',
            field=models.ManyToManyField(blank=True, related_name='variant_attributes', through='attribute.AttributeVariant', to='product.ProductType'),
        ),
        migrations.AddField(
            model_name='assignedvariantattributevalue',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variantvalueassignment', to='attribute.assignedvariantattribute'),
        ),
        migrations.AddField(
            model_name='assignedvariantattributevalue',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variantvalueassignment', to='attribute.attributevalue'),
        ),
        migrations.AddField(
            model_name='assignedvariantattribute',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variantassignments', to='attribute.attributevariant'),
        ),
        migrations.AddField(
            model_name='assignedvariantattribute',
            name='values',
            field=models.ManyToManyField(blank=True, related_name='variantassignments', through='attribute.AssignedVariantAttributeValue', to='attribute.AttributeValue'),
        ),
        migrations.AddField(
            model_name='assignedvariantattribute',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='product.productvariant'),
        ),
        migrations.AddField(
            model_name='assignedproductattributevalue',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productvalueassignment', to='attribute.assignedproductattribute'),
        ),
        migrations.AddField(
            model_name='assignedproductattributevalue',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productvalueassignment', to='attribute.attributevalue'),
        ),
        migrations.AddField(
            model_name='assignedproductattribute',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productassignments', to='attribute.attributeproduct'),
        ),
        migrations.AddField(
            model_name='assignedproductattribute',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='product.product'),
        ),
        migrations.AddField(
            model_name='assignedproductattribute',
            name='values',
            field=models.ManyToManyField(blank=True, related_name='productassignments', through='attribute.AssignedProductAttributeValue', to='attribute.AttributeValue'),
        ),
        migrations.AddField(
            model_name='assignedpageattributevalue',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagevalueassignment', to='attribute.assignedpageattribute'),
        ),
        migrations.AddField(
            model_name='assignedpageattributevalue',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagevalueassignment', to='attribute.attributevalue'),
        ),
        migrations.AddField(
            model_name='assignedpageattribute',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pageassignments', to='attribute.attributepage'),
        ),
        migrations.AddField(
            model_name='assignedpageattribute',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='page.page'),
        ),
        migrations.AddField(
            model_name='assignedpageattribute',
            name='values',
            field=models.ManyToManyField(blank=True, related_name='pageassignments', through='attribute.AssignedPageAttributeValue', to='attribute.AttributeValue'),
        ),
        migrations.AlterUniqueTogether(
            name='attributevariant',
            unique_together={('attribute', 'product_type')},
        ),
        migrations.AlterUniqueTogether(
            name='attributevaluetranslation',
            unique_together={('language_code', 'attribute_value')},
        ),
        migrations.AddIndex(
            model_name='attributevalue',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name', 'slug'], name='attribute_search_gin', opclasses=['gin_trgm_ops', 'gin_trgm_ops']),
        ),
        migrations.AlterUniqueTogether(
            name='attributevalue',
            unique_together={('slug', 'attribute')},
        ),
        migrations.AlterUniqueTogether(
            name='attributetranslation',
            unique_together={('language_code', 'attribute')},
        ),
        migrations.AlterUniqueTogether(
            name='attributeproduct',
            unique_together={('attribute', 'product_type')},
        ),
        migrations.AlterUniqueTogether(
            name='attributepage',
            unique_together={('attribute', 'page_type')},
        ),
        migrations.AddIndex(
            model_name='attribute',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='attribute_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='attribute',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='attribute_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='attribute',
            index=django.contrib.postgres.indexes.GinIndex(fields=['slug', 'name', 'type', 'input_type', 'entity_type', 'unit'], name='attribute_gin', opclasses=['gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops']),
        ),
        migrations.AlterUniqueTogether(
            name='assignedvariantattributevalue',
            unique_together={('value', 'assignment')},
        ),
        migrations.AlterUniqueTogether(
            name='assignedvariantattribute',
            unique_together={('variant', 'assignment')},
        ),
        migrations.AlterUniqueTogether(
            name='assignedproductattributevalue',
            unique_together={('value', 'assignment')},
        ),
        migrations.AlterUniqueTogether(
            name='assignedproductattribute',
            unique_together={('product', 'assignment')},
        ),
        migrations.AlterUniqueTogether(
            name='assignedpageattributevalue',
            unique_together={('value', 'assignment')},
        ),
        migrations.AlterUniqueTogether(
            name='assignedpageattribute',
            unique_together={('page', 'assignment')},
        ),
    ]