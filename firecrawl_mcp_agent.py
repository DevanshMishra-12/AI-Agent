from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os

load_dotenv(dotenv_path="d:/AI Agent/.env")

model = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

server_params = StdioServerParameters(
    command="npx",
    env={
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY"),   
    },
    args=["firecrawl-mcp"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)


            messages = [
                {"role": "system", "content": "You are a helpful assistant that can scrape websites, crawl pages, and extract data using firecrawls tools. Think step by step and use the tools when necessary."} 
            ] 

            print(f"Available tools: {[tool.name for tool in tools]}")
            print("-"*60)

            while True:
                user_input = input("\nYou: ")
                if user_input == "quit":
                    print("Byee")
                    break

                messages.append({"role": "user", "content": user_input[:175000]})


                try:
                    response = await agent.ainvoke({"messages" : messages})


                    ai_messages = response["messages"][-1].content

                    print("\nAgent:", ai_messages)
                except Exception as e:
                    print(f"Error: {e}")    


if __name__ == "__main__":
    asyncio.run(main())

    
