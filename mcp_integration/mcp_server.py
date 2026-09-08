from fastmcp import FastMCP
from agent.tools import check_loan_application_status

mcp = FastMCP("cred-support")
@mcp.tool()
def check_loan_status(record_id: str) -> dict:
    """Look up a loan application by record ID"""
    return check_loan_application_status(record_id)
if __name__ == "__main__":
    mcp.run(transport="http", port=8001)