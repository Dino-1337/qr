import streamlit as st
import aiohttp
import asyncio
from streamlit_qrcode_scanner import qrcode_scanner

st.title("Lmao Attendance")

import streamlit as st

st.markdown(
    """
    <style>
        .stApp {
            background-color: white !important;
        }
        label, .stRadio div {
            color: black !important;
            font-weight: bold;
        }
        h1 {
            color: black !important;
            font-weight: bold;
        }
        
    </style>
    """,
    unsafe_allow_html=True
)


async def get_cookies(session, username, password):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en;q=0.8",
        "clienttzofst": "330",
        "content-type": "application/json",
        "origin": "https://student.bennetterp.camu.in",
        "priority": "u=1, i",
        "referer": "https://student.bennetterp.camu.in/v2/?id=663474b11dd0e9412a1f793f",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
    }

    json_data = {
        "dtype": "M",
        "Email": username,
        "pwd": password,
    }

    async with session.post(
        "https://student.bennetterp.camu.in/login/validate",
        headers=headers,
        json=json_data,
    ) as response:
        data = await response.json()
        stu_id = data["output"]["data"]["logindetails"]["Student"][0]["StuID"]
        cookie = response.cookies.get("connect.sid").value

    return cookie, stu_id


async def mark_attendance(session, stu_id, cookie, qr_code):
    cookies = {
        "connect.sid": cookie,
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en;q=0.8",
        "clienttzofst": "330",
        "content-type": "application/json",
        "origin": "https://student.bennetterp.camu.in",
        "priority": "u=1, i",
        "referer": "https://student.bennetterp.camu.in/v2/timetable",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
    }

    json_data = {
        "attendanceId": qr_code,
        "StuID": stu_id,
        "offQrCdEnbld": True,
    }

    async with session.post(
        "https://student.bennetterp.camu.in/api/Attendance/record-online-attendance",
        cookies=cookies,
        headers=headers,
        json=json_data,
    ) as response:
        data = await response.json()
        return data["output"]["data"]["code"]


async def process_student(session, student, qr_code):
    try:
        cookie, stu_id = await get_cookies(
            session, student["username"], student["password"]
        )
        response = await mark_attendance(session, stu_id, cookie, qr_code)
        return student["name"], response
    except Exception as e:
        return student["name"], f"Error: {str(e)}"


async def process_all_students(stu_profiles, category, qr_code):
    async with aiohttp.ClientSession() as session:
        tasks = [
            process_student(session, student, qr_code)
            for student in stu_profiles
            if category in student["category"]
        ]
        results = await asyncio.gather(*tasks)
    return results


stu_profiles = [
    {
        "username": "e22cseu0145@bennett.edu.in",
        "password": "14-03-2004",
        "name": "Priyanshu Dash",
        "category": ["AIandSociety", "TimeSeries", "InformationRetrieval", "DeepLearning", "Communication", "IVP"],
    },
    {
        "username": "e22cseu1234@bennett.edu.in",
        "password": "01-01-2003",
        "name": "New Student",
        "category": ["DeepLearning", "AIandSociety", "IVP","InformationRetrieval"],
    }
]

category = st.radio(
    "Category?",
    [
        "AiSociety",
        "Cpp",
        "Time Series",
        "IR",
        "IVP",
        "DeepLearning",
        "Communication",
    ],
)

col1, col2 = st.columns([1, 2])

if category:
    qr_code = qrcode_scanner(key="qrcode_scanner")

    if qr_code:
        results = asyncio.run(process_all_students(stu_profiles, category, qr_code))
        for name, response in results:
            st.write(name, response)
