from typing import List
from .subscriber import Subscriber

class DiameterSession:
    subscriber: Subscriber
    session_id: str
    start_time: str
    end_time: str
    
    def __init__(self, subscriber, session_id: str):
        self.subscriber = subscriber
        self.session_id = session_id
        self.start_time = None
        self.end_time = None
   
    def set_start_time(self, start_time: str):
        self.start_time = start_time

    def set_end_time(self, end_time: str):
        self.end_time = end_time



class DiameterSessions:
    diameter_sessions: List[DiameterSession]
    
    def __init__(self):
        self.diameter_sessions: List[DiameterSession] = []
    
    def add_diameter_session(self, diameter_session: DiameterSession):
        self.diameter_sessions.append(diameter_session)
    
    def get_diameter_session(self, session_id: str) -> DiameterSession:
        for diameter_session in self.diameter_sessions:
            if diameter_session.session_id == session_id:
                return diameter_session
        raise ValueError("DiameterSession not found")
    
    def remove_diameter_session(self, session_id: str):
        for diameter_session in self.diameter_sessions:
            if diameter_session.session_id == session_id:
                self.diameter_sessions.remove(diameter_session)
                return
        raise ValueError("DiameterSession not found")