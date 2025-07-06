import mysql.connector
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["inquisitive-crumble-09762b.netlify.app"],  # Allow all origins (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

VALID_USERNAME = "vebbox"
VALID_PASSWORD = "12345"

def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != VALID_USERNAME or credentials.password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def get_db_connection():
    return mysql.connector.connect(
        host="sh00u.h.filess.io",
        user="ajay_rushbellhe",
        password="f929a31142b51d4238b0859ffe09a0f142627e32",
        database="ajay_rushbellhe",
        port="3307"
    )

class Item (BaseModel) :
    Name:str
    Age:str
    PhoneNO:str
    P_Type:str

@app.get("/PatientDetail")
def get_details():
    try:
         mydb = get_db_connection()
         cursor = mydb.cursor(dictionary=True)  # Get results as dictionary

         cursor.execute("SELECT * FROM patient")
         students = cursor.fetchall()

         cursor.close()
         mydb.close()

         return students

    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/insertDetail")
def post_details(obj : Item):
    try:
        mydb = get_db_connection()
        cursor = mydb.cursor()

        query="""Insert into patient (Name,Age,PhoneNO,P_Type) values (%s,%s,%s,%s)"""
        values=(obj.Name,obj.Age,obj.PhoneNO,obj.P_Type)

        cursor.execute(query, values)
        mydb.commit()

        cursor.close()
        mydb.close()

        return {"message": "Patient added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

class DeleteRequest(BaseModel):
    id : int
@app.post("/deleteRequest")
def post_delete(d : DeleteRequest ):


    try:
        mydb = get_db_connection()
        cursor = mydb.cursor()

        cursor.execute("DELETE FROM patient WHERE S_NO = %s", (d.id,))
        mydb.commit()

        cursor.close()
        mydb.close()

        return {"message": "Student deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/getDetail/{id}")
def get_detail(id: int):
    try:
        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)  # Get results as dictionary

        cursor.execute("SELECT * FROM patient where S_NO=%s", (id,))
        students = cursor.fetchall()

        cursor.close()
        mydb.close()

        return students

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


class UpdateFieldRequest(BaseModel):
    field: str
    value: str


@app.patch("/updateField/{id}")
def update_field(id: int, data: UpdateFieldRequest):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        allowed_fields = ["Name", "Age", "PhoneNO",  "P_Type"]
        if data.field not in allowed_fields:
            raise HTTPException(status_code=400, detail=f"Field '{data.field}' is not allowed to update.")

        sql = f"UPDATE patient SET {data.field} = %s WHERE S_NO = %s"
        cursor.execute(sql, (data.value, id))
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found.")

        return {"message": f"{data.field} updated successfully!"}

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        connection.close()
