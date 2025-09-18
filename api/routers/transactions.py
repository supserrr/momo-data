"""
Transactions Router
Team 11 - Enterprise Web Development
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..db import MySQLDatabaseManager

router = APIRouter(prefix="/transactions", tags=["transactions"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/")
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    status: Optional[str] = None,
    phone: Optional[str] = None,
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get transactions with optional filters."""
    try:
        transactions = db.get_transactions(
            limit=limit,
            offset=offset,
            category=category,
            status=status,
            phone=phone
        )
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get a specific transaction by ID."""
    try:
        transaction = db.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{transaction_id}/details")
async def get_transaction_details(
    transaction_id: int,
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get comprehensive transaction details with all parsed fields from the original message."""
    try:
        transaction = db.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Parse the original message to extract additional details
        from etl.parser import EnhancedMTNParser
        parser = EnhancedMTNParser()
        
        # Get the original message
        original_message = (transaction.get('original_message') or 
                          transaction.get('original_data') or 
                          transaction.get('raw_data') or 
                          transaction.get('raw_sms_data'))
        
        parsed_details = {}
        if original_message:
            # Re-parse the message to get all available fields
            parsed_transaction = parser.parse_message(original_message, transaction.get('date'))
            if parsed_transaction:
                parsed_details = {
                    'parsed_transaction_type': parsed_transaction.transaction_type,
                    'parsed_category': parsed_transaction.category,
                    'parsed_direction': parsed_transaction.direction,
                    'parsed_sender_name': parsed_transaction.sender_name,
                    'parsed_sender_phone': parsed_transaction.sender_phone,
                    'parsed_recipient_name': parsed_transaction.recipient_name,
                    'parsed_recipient_phone': parsed_transaction.recipient_phone,
                    'parsed_momo_code': parsed_transaction.momo_code,
                    'parsed_sender_momo_id': parsed_transaction.sender_momo_id,
                    'parsed_agent_momo_number': parsed_transaction.agent_momo_number,
                    'parsed_business_name': parsed_transaction.business_name,
                    'parsed_fee': parsed_transaction.fee,
                    'parsed_new_balance': parsed_transaction.new_balance,
                    'parsed_transaction_id': parsed_transaction.transaction_id,
                    'parsed_financial_transaction_id': parsed_transaction.financial_transaction_id,
                    'parsed_external_transaction_id': parsed_transaction.external_transaction_id,
                    'parsed_confidence': parsed_transaction.confidence
                }
        
        # Combine database data with parsed details, prioritizing parsed data
        comprehensive_details = {
            # Basic transaction info
            'id': transaction.get('id'),
            'amount': parsed_details.get('parsed_amount') or transaction.get('amount'),
            'currency': transaction.get('currency', 'RWF'),
            'date': transaction.get('date'),
            'status': transaction.get('status'),
            'direction': parsed_details.get('parsed_direction') or transaction.get('direction'),
            'transaction_type': parsed_details.get('parsed_transaction_type') or transaction.get('transaction_type'),
            'category': parsed_details.get('parsed_category') or transaction.get('category'),
            
            # Financial details
            'fee': parsed_details.get('parsed_fee') or transaction.get('fee', 0),
            'new_balance': parsed_details.get('parsed_new_balance') or transaction.get('new_balance'),
            'reference': transaction.get('reference'),
            
            # Transaction IDs - prioritize parsed data
            'transaction_id': parsed_details.get('parsed_transaction_id') or transaction.get('transaction_id'),
            'external_transaction_id': parsed_details.get('parsed_external_transaction_id') or transaction.get('external_transaction_id'),
            'financial_transaction_id': parsed_details.get('parsed_financial_transaction_id') or transaction.get('financial_transaction_id'),
            
            # Party information - prioritize parsed data
            'sender_name': parsed_details.get('parsed_sender_name') or transaction.get('sender_name'),
            'sender_phone': parsed_details.get('parsed_sender_phone') or transaction.get('sender_phone'),
            'recipient_name': parsed_details.get('parsed_recipient_name') or transaction.get('recipient_name'),
            'recipient_phone': parsed_details.get('parsed_recipient_phone') or transaction.get('recipient_phone'),
            'momo_code': parsed_details.get('parsed_momo_code') or transaction.get('momo_code'),
            'sender_momo_id': parsed_details.get('parsed_sender_momo_id') or transaction.get('sender_momo_id'),
            'agent_momo_number': parsed_details.get('parsed_agent_momo_number') or transaction.get('agent_momo_number'),
            'business_name': parsed_details.get('parsed_business_name') or transaction.get('business_name'),
            
            # Parsing metadata
            'confidence_score': parsed_details.get('parsed_confidence') or transaction.get('confidence_score'),
            'original_message': original_message,
            'xml_attributes': transaction.get('xml_attributes'),
            'processing_metadata': transaction.get('processing_metadata'),
            'loaded_at': transaction.get('loaded_at'),
            
            # Parsed details from message
            'parsed_details': parsed_details,
            
            # Categorized fields for easy access - use the best available data
            'categorized_fields': {
                'financial': {
                    'amount': parsed_details.get('parsed_amount') or transaction.get('amount'),
                    'fee': parsed_details.get('parsed_fee') or transaction.get('fee', 0),
                    'new_balance': parsed_details.get('parsed_new_balance') or transaction.get('new_balance'),
                    'currency': transaction.get('currency', 'RWF')
                },
                'identifiers': {
                    'transaction_id': parsed_details.get('parsed_transaction_id') or transaction.get('transaction_id'),
                    'external_transaction_id': parsed_details.get('parsed_external_transaction_id') or transaction.get('external_transaction_id'),
                    'financial_transaction_id': parsed_details.get('parsed_financial_transaction_id') or transaction.get('financial_transaction_id'),
                    'reference': transaction.get('reference')
                },
                'parties': {
                    'sender_name': parsed_details.get('parsed_sender_name') or transaction.get('sender_name'),
                    'sender_phone': parsed_details.get('parsed_sender_phone') or transaction.get('sender_phone'),
                    'recipient_name': parsed_details.get('parsed_recipient_name') or transaction.get('recipient_name'),
                    'recipient_phone': parsed_details.get('parsed_recipient_phone') or transaction.get('recipient_phone'),
                    'momo_code': parsed_details.get('parsed_momo_code') or transaction.get('momo_code'),
                    'sender_momo_id': parsed_details.get('parsed_sender_momo_id') or transaction.get('sender_momo_id'),
                    'agent_momo_number': parsed_details.get('parsed_agent_momo_number') or transaction.get('agent_momo_number'),
                    'business_name': parsed_details.get('parsed_business_name') or transaction.get('business_name')
                },
                'metadata': {
                    'transaction_type': parsed_details.get('parsed_transaction_type') or transaction.get('transaction_type'),
                    'category': parsed_details.get('parsed_category') or transaction.get('category'),
                    'direction': parsed_details.get('parsed_direction') or transaction.get('direction'),
                    'status': transaction.get('status'),
                    'confidence_score': parsed_details.get('parsed_confidence') or transaction.get('confidence_score'),
                    'date': transaction.get('date'),
                    'loaded_at': transaction.get('loaded_at')
                },
                'raw_data': {
                    'original_message': original_message,
                    'xml_attributes': transaction.get('xml_attributes'),
                    'processing_metadata': transaction.get('processing_metadata')
                }
            }
        }
        
        return comprehensive_details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
