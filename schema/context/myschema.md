# NII-DG: Schema: myschema

See [GitHub - NII-DG/nii-dg - schema/README.md](https://github.com/NII-DG/nii-dg/blob/main/schema/README.md) for more information.

## MySchema
A test schema.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root (as stated in the identifier property of RootDataEntity) or an absolute URI. MUST end with `/`. This indicates the path to the directory. | `config` |
| `name` | `str` | Required. | Denotes the directory name. | `config` |
| `url` | `str` | Optional. | MUST be a direct URL link to the directory. | `https://github.com/username/repository/directory` |
| `message` | `str` | Optional. | MUST be a string. | `this is a test message .` |

## MyOutputSchema
An output file included in the research project.

| Property | Type | Required? | Description | Example |
| --- | --- | --- | --- | --- |
| `@id` | `str` | Required. | MUST be either a URI Path relative to the RO-Crate root directory or an absolute URI that is directly downloadable. If the file originates outside the repository, @id SHOULD allow for simple retrieval (e.g., HTTP GET), including redirections and HTTP/HTTPS authentication. RO-Crate metadata (ro-crate-metadata.json) is excluded. | `config/setting.txt` |
| `name` | `str` | Required. | Denotes the file name. | `setting.txt` |
| `contentSize` | `str` | Required. | MUST be an integer representing the file size, suffixed with `B` for bytes. Other units like "KB", "MB", "GB", "TB", and "PB" may also be used if necessary. | `1560B` |
| `encodingFormat` | `str` | Optional. | MUST be a MIME type, excluding any "x-" prefix. Specifies the file format. | `text/plain` |
| `sha256` | `str` | Optional. | MUST be the SHA-2 SHA256 hash of the file. | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `url` | `str` | Optional. | MUST be a direct URL link to the file. | `https://github.com/username/repository/file` |
| `sdDatePublished` | `str` | Required when the file is sourced from outside the RO-Crate Root. | Indicates the date the file was obtained. MUST be a string in ISO 8601 date format. | `2022-12-01` |
