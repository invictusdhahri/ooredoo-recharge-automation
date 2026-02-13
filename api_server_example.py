#!/usr/bin/env python3
"""
Flask REST API Example for Ooredoo Recharge
Shows how to integrate recharge_api.py into a web service
"""

from flask import Flask, request, jsonify
from recharge_api import api_recharge
import os
from datetime import datetime

app = Flask(__name__)

# Create logs directory
os.makedirs('api_logs', exist_ok=True)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Ooredoo Recharge API',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/v1/recharge', methods=['POST'])
def create_recharge():
    """
    Create and monitor recharge
    
    POST /api/v1/recharge
    Content-Type: application/json
    
    Body:
    {
        "phone": "27865121",
        "password": "mypassword",
        "beneficiary": "27865121",
        "amount": 20,
        "timeout": 300  // optional, default 300s
    }
    
    Response:
    {
        "success": true,
        "message": "Recharge completed successfully",
        "data": {
            "order_id": "12345",
            "transaction_id": "67890",
            "amount": 20,
            "beneficiary": "27865121",
            "elapsed_seconds": 45.2
        },
        "timestamp": "2025-02-13T16:30:00"
    }
    """
    
    # Validate request
    if not request.json:
        return jsonify({
            'success': False,
            'error': 'Invalid request: JSON body required'
        }), 400
    
    # Extract parameters
    phone = request.json.get('phone')
    password = request.json.get('password')
    beneficiary = request.json.get('beneficiary')
    amount = request.json.get('amount')
    timeout = request.json.get('timeout', 300)
    
    # Validate required fields
    missing = []
    if not phone: missing.append('phone')
    if not password: missing.append('password')
    if not beneficiary: missing.append('beneficiary')
    if not amount: missing.append('amount')
    
    if missing:
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {", ".join(missing)}'
        }), 400
    
    # Validate amount
    try:
        amount = int(amount)
        if amount <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': 'Invalid amount: must be positive integer'
        }), 400
    
    # Generate log file name
    log_file = f"api_logs/{phone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Execute recharge
    try:
        result = api_recharge(
            phone=phone,
            password=password,
            beneficiary=beneficiary,
            amount=amount,
            timeout_seconds=timeout,
            log_file=log_file
        )
        
        # Format response
        if result['success']:
            response = {
                'success': True,
                'message': result['message'],
                'data': {
                    'order_id': result.get('payment', {}).get('data', {}).get('order_id'),
                    'transaction_id': result.get('payment', {}).get('data', {}).get('transaction_id'),
                    'amount': amount,
                    'beneficiary': beneficiary,
                    'elapsed_seconds': result.get('payment', {}).get('data', {}).get('elapsed_seconds'),
                    'detection_method': result.get('payment', {}).get('data', {}).get('detection_method')
                },
                'timestamp': result.get('completed_at'),
                'log_file': log_file
            }
            return jsonify(response), 200
        
        else:
            response = {
                'success': False,
                'message': result['message'],
                'error': {
                    'stage': result.get('stage'),
                    'details': result.get('payment', {}).get('message')
                },
                'timestamp': result.get('completed_at'),
                'log_file': log_file
            }
            return jsonify(response), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}',
            'log_file': log_file
        }), 500


@app.route('/api/v1/status/<order_id>', methods=['GET'])
def check_status(order_id):
    """
    Check status of an order
    
    GET /api/v1/status/<order_id>
    
    Note: This is a placeholder. In production, you'd:
    1. Store order status in database during recharge
    2. Query database by order_id
    3. Return current status
    """
    return jsonify({
        'order_id': order_id,
        'message': 'Status check not yet implemented',
        'note': 'Store order details in database during recharge creation'
    }), 501


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /health',
            'POST /api/v1/recharge',
            'GET /api/v1/status/<order_id>'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(e)
    }), 500


if __name__ == '__main__':
    print()
    print("=" * 70)
    print("OOREDOO RECHARGE API SERVER")
    print("=" * 70)
    print()
    print("Available endpoints:")
    print("  GET  /health                - Health check")
    print("  POST /api/v1/recharge       - Create and monitor recharge")
    print("  GET  /api/v1/status/<id>    - Check order status (not implemented)")
    print()
    print("Starting server on http://localhost:5000")
    print("=" * 70)
    print()
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True)
