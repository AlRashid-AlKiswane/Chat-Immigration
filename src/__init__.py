import warnings

warnings.filterwarnings(
    "ignore",
    message='directory "/run/secrets" does not exist',
    category=UserWarning,
)
