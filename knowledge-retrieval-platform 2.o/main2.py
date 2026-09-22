# import os
# import uvicorn

# if __name__ == "__main__":
#     print("Starting AI Knowledge Retrieval Platform on http://127.0.0.1:8000 ...")
#     uvicorn.run(
#         "app.main:app",
#         host="127.0.0.1",
#         port=8000,
#         reload=True
#     )

import uvicorn

if __name__ == "__main__":
    print("Starting AI Knowledge Retrieval Platform on http://127.0.0.1:8000 ...")
    uvicorn.main(["app.main:app", "--reload", "--port", "8000"])