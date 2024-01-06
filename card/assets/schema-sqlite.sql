DROP TABLE IF EXISTS [Templates];
DROP TABLE IF EXISTS [Batches];

CREATE TABLE [Templates] (
	[id] INTEGER PRIMARY KEY NOT NULL,
	[name] TEXT NOT NULL,
	[definition] TEXT NOT NULL,
	[created_at] TEXT NOT NULL,
	[updated_at] TEXT NOT NULL,
	[deleted_at] TEXT NULL
);

CREATE TABLE [Batches] (
	[id] INTEGER PRIMARY KEY NOT NULL,
	[name] TEXT NOT NULL,
	[template_id] INTEGER NOT NULL,
	[data_file_path] TEXT NOT NULL,
	[status] TEXT NOT NULL,
	[processed_item_count] INTEGER NOT NULL,
	[created_at] TEXT NOT NULL,
	[picked_at] TEXT NULL,
	[finished_at] TEXT NULL,
	[deleted_at] TEXT NULL,
	FOREIGN KEY ([template_id])
		REFERENCES [Templates] (id)
);

CREATE TABLE [allowed_users](
	[id] INTEGER PRIMARY KEY NOT NULL,
	[national_code] TEXT NOT NULL,
	[first_name] TEXT NOT NULL,
	[last_name] TEXT NOT NULL,
	[role] TEXT NOT NULL,
	[created_at] TEXT NOT NULL,
	[updated_at] TEXT NOT NULL,
	[deleted_at] TEXT NULL
);