# Genie Ops

A Databricks Asset Bundle (DAB) project for exporting and importing Genie spaces across different environments through CI/CD automation.

## Overview

This project provides automated workflows to export Genie spaces from a source environment and import them into target environments (dev, test, staging, production). It leverages Databricks Asset Bundles for seamless deployment and environment management.

## Features

- **Export Genie Spaces**: Export Genie space configurations as JSON files with environment-specific transformations
- **Import Genie Spaces**: Import Genie spaces into new or existing spaces across different environments
- **Multi-Environment Support**: Automatically generates environment-specific configurations (dev, tst, stg, prd)
- **CI/CD Ready**: Integrates with Databricks Asset Bundles for automated deployments
- **Environment Pattern Replacement**: Automatically replaces environment suffixes (_dev, _tst, _stg, _prd) in exported configurations

## Project Structure

```
genie_ops/
├── databricks.yml                      # Databricks Asset Bundle configuration
├── resources/
│   └── genie_import_export.yml        # Job definitions for import/export
├── src/
│   └── notebooks/
│       ├── genie_export.py            # Export notebook
│       ├── genie_import.py            # Import notebook
│       └── utils.py                   # Utility classes (ExportGenie, ImportGenie)
└── genie_space_exports/               # Directory for exported JSON files
    └── {genie_name}/                  # Subdirectory per Genie (e.g., sales_overview)
        └── exported_{space_id}_{env}.json
```

## Prerequisites

- Databricks workspace with Genie enabled
- Databricks CLI installed (`databricks` command)
- Access to source and target Genie spaces
- SQL warehouse configured in your workspace

## Configuration

### 1. Update `databricks.yml`

Configure the following variables for your environment:

```yaml
variables:
  src_genie_space_id:       # Source Genie space ID to export
  tgt_genie_space_id:       # Target Genie space ID (use "None" to create new)
  tgt_genie_dir:            # Path where Genie space lives on Databricks workspace
  path_to_genie_folder:     # Path to Genie space folder in the repo
  host_name:                # Databricks workspace hostname (with https://)
  warehouse_id:             # SQL warehouse ID (uses lookup for "Shared Endpoint")
  env:                      # Target environment (dev, tst, stg, prd)
```

### 2. Environment-Specific Configuration

The bundle supports two targets:

- **dev**: Development environment (default)
  - `env: dev` - uses `*_dev.json` export files
- **prod**: Production environment
  - `env: prd` - uses `*_prd.json` export files

Each target can have different values for:
- Genie space IDs
- Workspace paths
- Warehouse configurations
- Hostnames
- Environment identifiers

## Usage

### Export a Genie Space

Export a Genie space from the source environment:

```bash
# Using Databricks CLI
databricks bundle run job_genie_export --target dev
```

This will:
1. Connect to the source Genie space using `src_genie_space_id`
2. Export the space configuration via Databricks Genie API
3. Apply environment-specific pattern replacements
4. Generate 4 JSON files (one per environment: dev, tst, stg, prd)
5. Save files to `{path_to_genie_folder}/{genie_name}/` directory

**Exported file structure**: 
```
genie_space_exports/
  └── sales_overview/
      ├── exported_01f0c29c258819faa4a7b971e56ee7eb_dev.json
      ├── exported_01f0c29c258819faa4a7b971e56ee7eb_tst.json
      ├── exported_01f0c29c258819faa4a7b971e56ee7eb_stg.json
      └── exported_01f0c29c258819faa4a7b971e56ee7eb_prd.json
```

### Import a Genie Space

Import a Genie space to a target environment:

```bash
# Using Databricks CLI
databricks bundle run job_genie_import --target dev
```

This will:
1. Read the environment-specific exported JSON file (determined by `env` variable)
2. Load the file from `{path_to_genie_folder}/{genie_name}/exported_{space_id}_{env}.json`
3. Create a new Genie space (if `tgt_genie_space_id` is None) OR update an existing space
4. Configure the space with the specified warehouse and directory
5. Apply the serialized space configuration

**Important**: The `env` variable determines which JSON file is used:
- `--target dev` uses `env: dev` → reads `exported_*_dev.json`
- `--target prod` uses `env: prd` → reads `exported_*_prd.json`

### Deploy the Bundle

Deploy all resources to your Databricks workspace:

```bash
# Deploy to dev
databricks bundle deploy --target dev

# Deploy to prod
databricks bundle deploy --target prod
```

## How It Works

### Export Process

1. **API Call**: Uses Databricks Genie API endpoint `/api/2.0/genie/spaces/{space_id}?include_serialized_space=true`
2. **Pattern Replacement**: Replaces environment suffixes (_dev, _tst, _stg, _prd) with target environment
3. **Multi-File Generation**: Creates separate JSON files for each environment
4. **Version Control**: Exported files can be committed to Git for tracking changes

### Import Process

1. **File Reading**: Loads the environment-specific JSON file (e.g., `exported_{space_id}_dev.json`)
2. **API Decision**: 
   - If `tgt_genie_space_id` is None/empty → Creates new space (POST)
   - If `tgt_genie_space_id` exists → Updates existing space (PATCH)
3. **Configuration**: Sets warehouse ID, parent path, and serialized space data
4. **Validation**: Returns success/failure status with detailed error messages

## API Endpoints Used

- **Export**: `GET /api/2.0/genie/spaces/{space_id}?include_serialized_space=true`
- **Create**: `POST /api/2.0/genie/spaces/`
- **Update**: `PATCH /api/2.0/genie/spaces/{space_id}`

## Parameters

### Export Job Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `host_name` | Databricks hostname (with https://) | `https://e2-demo-field-eng.cloud.databricks.com` |
| `src_genie_space_id` | Source Genie space ID | `01f0c29c258819faa4a7b971e56ee7eb` |
| `path_to_genie_folder` | Path to export directory (variable) | `genie_space_exports` |
| `genie_name` | Name of the Genie space | `sales_overview` |
| `root_dir` | Root directory (optional) | `None` (uses workspace root) |
| `env` | Target environment (variable) | `dev`, `tst`, `stg`, `prd` |

### Import Job Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `host_name` | Databricks hostname (with https://) | `https://e2-demo-field-eng.cloud.databricks.com` |
| `src_genie_space_id` | Source space ID (for file lookup) | `01f0c29c258819faa4a7b971e56ee7eb` |
| `tgt_genie_space_id` | Target space ID (None = create new) | `None` |
| `src_genie_dir` | Directory with exported JSON | `../../genie_space_exports/sales_overview` |
| `tgt_genie_dir` | Target workspace directory | `/Workspace/Users/{user}/genie_space_exports/sales_overview/` |
| `warehouse_id` | SQL warehouse ID (variable) | Resolved via lookup to "Shared Endpoint" |
| `env` | Target environment (variable) | `dev`, `tst`, `stg`, `prd` |

## Environment Pattern Replacement

The export process automatically handles environment-specific naming:

- Replaces `_dev`, `_tst`, `_stg`, `_prd` suffixes in the configuration
- Generates environment-specific files for each target
- Ensures consistent naming across environments

Example:
- Source: `sales_data_dev` → Export to dev: `sales_data_dev`
- Source: `sales_data_dev` → Export to prd: `sales_data_prd`

## Troubleshooting

### Common Issues

1. **Invalid Genie Space ID**
   - Ensure `src_genie_space_id` is a valid 32-character hex string
   - Check that you have access to the source space

2. **Warehouse Not Found**
   - Verify `warehouse_id` or warehouse lookup name exists
   - Ensure you have permissions to use the warehouse

3. **File Not Found During Import**
   - Confirm the exported JSON file exists in `src_genie_dir/{genie_name}/`
   - Check the filename format: `exported_{src_genie_space_id}_{env}.json`
   - Verify the `env` variable matches the target (dev, tst, stg, prd)
   - Ensure `src_genie_dir` path includes the `{genie_name}` subdirectory

4. **API Authentication Errors**
   - Verify workspace hostname is correct (without https://)
   - Ensure notebook is running with proper authentication context

## Best Practices

1. **Version Control**: Commit exported JSON files to track configuration changes over time
2. **Environment Isolation**: Use separate `tgt_genie_space_id` values for each environment
3. **Testing**: Always test in dev before deploying to production
4. **Warehouse Management**: Use shared warehouses for Genie spaces when possible
5. **Naming Conventions**: Use environment suffixes (_dev, _tst, _stg, _prd) for easy pattern matching

## Contributing

When contributing to this project:
1. Test export/import workflows in dev environment first
2. Validate JSON files are correctly formatted
3. Update documentation for new parameters or features
4. Follow Databricks Asset Bundle best practices

## License

This project is intended for internal use with Databricks workspaces.

## Support

For issues or questions:
- Check Databricks Genie API documentation
- Review DAB documentation: https://docs.databricks.com/dev-tools/bundles/
- Contact your Databricks workspace administrator
