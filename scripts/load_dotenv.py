import pathlib
import dotenv

here = pathlib.Path(__file__).parents[1] / ".env"
result = dotenv.load_dotenv(dotenv_path=here)
print(result)