
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings, ChatOpenAI


load_dotenv()

class Settings(BaseSettings):
    MODE:str = "HOME"

    AOAI_ENDPOINT:str
    AOAI_API_KEY:str
    AOAI_DEPLOY_GPT4O_MINI:str
    AOAI_DEPLOY_GPT4O:str
    AOAI_DEPLOY_EMBED_3_LARGE:str
    AOAI_DEPLOY_EMBED_3_SMALL:str
    AOAI_DEPLOY_EMBED_ADA:str

    LANGFUSE_SECRET_KEY:str
    LANGFUSE_PUBLIC_KEY:str
    LANGFUSE_BASE_URL:str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")




    def get_llm(self):
        # update HOME
        if self.MODE == "HOME":
            return ChatOpenAI(
                base_url=self.AOAI_ENDPOINT,
                api_key=self.AOAI_API_KEY,
                model_name=self.AOAI_DEPLOY_GPT4O_MINI,
            )
        elif self.MODE == "WORK":
            return AzureChatOpenAI(
                openai_api_key=self.AOAI_API_KEY,
                azure_endpoint=self.AOAI_ENDPOINT,
                azure_deployment=self.AOAI_DEPLOY_GPT4O,
                api_version="2024-02-15-preview",
                temperature=0.7,
                streaming=True,
            )
        else:
            raise ValueError("Invalid MODE")

    def get_embeddings(self):
        # update HOME
        if self.MODE == "HOME":
            return OpenAIEmbeddings(
                base_url=self.AOAI_ENDPOINT,
                api_key=self.AOAI_API_KEY,
                model_name=self.AOAI_DEPLOY_EMBED_3_LARGE,
            )
        elif self.MODE == "WORK":
            return AzureOpenAIEmbeddings(
                model=self.AOAI_DEPLOY_EMBED_3_LARGE,
                api_key=self.AOAI_API_KEY,
                azure_endpoint=self.AOAI_ENDPOINT,
            )
        else:
            raise ValueError("Invalid MODE")



settings = Settings()


def get_llm():
    return settings.get_llm()


