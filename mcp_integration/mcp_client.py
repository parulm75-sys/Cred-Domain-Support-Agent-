import asyncio
from fastmcp import Client
async def main():
    async with Client("http://127.0.0.1:8001/mcp") as client:
        result = await client.call_tool("check_loan_status", {"record_id": "3"})
        out = await client.call_tool("check_loan_status", {"record_id": "27"})
        print(f"Record 3: {result} \n Record 27: {out}")
if __name__ == "__main__":
    asyncio.run(main())