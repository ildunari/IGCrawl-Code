"""Service for handling Instagram credential storage and retrieval"""
from typing import Optional, Tuple
from sqlmodel import Session, select
from ..models import Account
from ..utils.crypto import encrypt_credential, decrypt_credential
from ..database import get_session


class CredentialService:
    """Handle Instagram credential encryption and storage"""
    
    @staticmethod
    def store_credentials(username: str, password: str, session: Session) -> bool:
        """
        Store Instagram credentials securely
        Automatically encrypts the password before storage
        """
        try:
            # Check if account exists
            account = session.exec(
                select(Account).where(Account.username == username)
            ).first()
            
            if not account:
                # Create new account
                account = Account(username=username)
                session.add(account)
            
            # Encrypt and store password
            encrypted_password = encrypt_credential(password)
            account.encrypted_password = encrypted_password
            
            session.commit()
            return True
            
        except Exception as e:
            print(f"Error storing credentials: {e}")
            session.rollback()
            return False
    
    @staticmethod
    def get_credentials(username: str, session: Session) -> Optional[Tuple[str, str]]:
        """
        Retrieve decrypted Instagram credentials
        Returns: (username, decrypted_password) or None
        """
        try:
            account = session.exec(
                select(Account).where(Account.username == username)
            ).first()
            
            if not account or not account.encrypted_password:
                return None
            
            decrypted_password = decrypt_credential(account.encrypted_password)
            return (username, decrypted_password)
            
        except Exception as e:
            print(f"Error retrieving credentials: {e}")
            return None
    
    @staticmethod
    def remove_credentials(username: str, session: Session) -> bool:
        """Remove stored Instagram credentials"""
        try:
            account = session.exec(
                select(Account).where(Account.username == username)
            ).first()
            
            if account:
                account.encrypted_password = None
                session.commit()
                return True
                
            return False
            
        except Exception as e:
            print(f"Error removing credentials: {e}")
            session.rollback()
            return False