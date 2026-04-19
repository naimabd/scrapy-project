from dagster import Config


class IngestionConfig(Config):
    start_date: str = "2024-01-01"
    end_date: str = "2024-01-31"
    bodies_str: str = "adjudication,labour-court,employment-appeals-tribunal"


class TransformationConfig(Config):
    start_date: str = "2024-01-01"
    end_date: str = "2024-01-31"
