from vectors.schema.schema_initializer import SchemaInitializer


def main() -> None:
    print("Initializing schema...")
    SchemaInitializer.create_schema()
    print("Schema initialized.")


if __name__ == "__main__":
    main()
