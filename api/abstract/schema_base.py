class SchemaBase:
    """Base interface for schemas to enforce a flexible schemas structure."""

    def validate(self):
        """Validate the schemas instance."""
        raise NotImplementedError("Schema must implement `validate` method.")

    def to_dict(self) -> dict:
        """Convert schemas instance to a dictionary."""
        raise NotImplementedError("Schema must implement `to_dict` method.")
