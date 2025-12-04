"""
OCSP REST API for Team Agent PKI.

Provides HTTP endpoint for OCSP certificate status checking.
"""

from flask import Flask, request, Response
from typing import Optional, Dict, Any
from cryptography import x509
from cryptography.hazmat.backends import default_backend

try:
    from .ocsp import OCSPResponder
    from .pki import PKIManager, TrustDomain
    OCSP_AVAILABLE = True
except ImportError:
    OCSPResponder = None
    PKIManager = None
    TrustDomain = None
    OCSP_AVAILABLE = False


class OCSPApi:
    """
    OCSP REST API server.

    Provides HTTP endpoints for OCSP certificate status checking.
    """

    def __init__(
        self,
        pki_manager: 'PKIManager',
        host: str = "127.0.0.1",
        port: int = 8080,
        cache_duration: int = 300
    ):
        """
        Initialize OCSP API.

        Args:
            pki_manager: PKIManager instance
            host: API host (default: 127.0.0.1)
            port: API port (default: 8080)
            cache_duration: OCSP response cache duration in seconds
        """
        self.pki_manager = pki_manager
        self.host = host
        self.port = port
        self.cache_duration = cache_duration

        # Create OCSP responders for each trust domain
        self.responders: Dict[str, OCSPResponder] = {}
        for domain in TrustDomain:
            responder = pki_manager.create_ocsp_responder(
                domain,
                cache_duration=cache_duration
            )
            if responder:
                self.responders[domain.value] = responder

        # Create Flask app
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """Set up API routes."""

        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "responders": list(self.responders.keys()),
                "cache_duration": self.cache_duration
            }

        @self.app.route('/ocsp', methods=['POST'])
        def ocsp_check():
            """
            OCSP certificate status check endpoint.

            Expects JSON body:
            {
                "serial": "certificate_serial_hex",
                "trust_domain": "execution|government|logging"
            }

            Returns:
            {
                "status": "good|revoked|unknown",
                "serial": "serial_hex",
                "trust_domain": "domain",
                "revocation_info": {...} (if revoked)
            }
            """
            try:
                data = request.get_json()

                if not data or 'serial' not in data or 'trust_domain' not in data:
                    return {
                        "error": "Missing required fields: serial, trust_domain"
                    }, 400

                serial_hex = data['serial']
                trust_domain = data['trust_domain']

                # Get responder for trust domain
                responder = self.responders.get(trust_domain)
                if not responder:
                    return {
                        "error": f"Invalid trust domain: {trust_domain}"
                    }, 400

                # Check certificate status
                from .ocsp import OCSPStatus
                status, revocation_info = responder.check_certificate_status(serial_hex)

                response_data = {
                    "status": status.value,
                    "serial": serial_hex,
                    "trust_domain": trust_domain
                }

                if status == OCSPStatus.REVOKED and revocation_info:
                    response_data["revocation_info"] = revocation_info

                return response_data, 200

            except Exception as e:
                return {
                    "error": f"Internal server error: {str(e)}"
                }, 500

        @self.app.route('/ocsp/binary', methods=['POST'])
        def ocsp_binary():
            """
            OCSP binary request/response endpoint (standard OCSP protocol).

            This endpoint accepts and returns DER-encoded OCSP requests/responses
            as per RFC 6960.

            Note: This is a simplified implementation. For production use,
            consider using a full OCSP responder like OpenSSL's ocsp command.
            """
            try:
                # Parse OCSP request from body
                request_data = request.get_data()

                if not request_data:
                    return Response(
                        "Missing OCSP request",
                        status=400,
                        mimetype='text/plain'
                    )

                # For now, we'll require a trust domain header
                trust_domain = request.headers.get('X-Trust-Domain', 'execution')

                responder = self.responders.get(trust_domain)
                if not responder:
                    return Response(
                        f"Invalid trust domain: {trust_domain}",
                        status=400,
                        mimetype='text/plain'
                    )

                # Parse OCSP request (simplified - in production, parse actual OCSP request)
                # For now, this is a placeholder for future OCSP binary protocol support
                return Response(
                    "Binary OCSP protocol not fully implemented yet. Use /ocsp JSON endpoint.",
                    status=501,
                    mimetype='text/plain'
                )

            except Exception as e:
                return Response(
                    f"Internal server error: {str(e)}",
                    status=500,
                    mimetype='text/plain'
                )

        @self.app.route('/ocsp/cache/stats', methods=['GET'])
        def cache_stats():
            """Get cache statistics for all responders."""
            stats = {}
            for domain, responder in self.responders.items():
                stats[domain] = responder.get_cache_stats()
            return {
                "cache_stats": stats
            }

        @self.app.route('/ocsp/cache/clear', methods=['POST'])
        def clear_cache():
            """Clear cache for all responders."""
            try:
                data = request.get_json() or {}
                trust_domain = data.get('trust_domain')

                if trust_domain:
                    # Clear cache for specific domain
                    responder = self.responders.get(trust_domain)
                    if not responder:
                        return {
                            "error": f"Invalid trust domain: {trust_domain}"
                        }, 400
                    responder.clear_cache()
                    return {
                        "message": f"Cache cleared for {trust_domain}"
                    }
                else:
                    # Clear cache for all domains
                    for responder in self.responders.values():
                        responder.clear_cache()
                    return {
                        "message": "Cache cleared for all domains"
                    }

            except Exception as e:
                return {
                    "error": f"Internal server error: {str(e)}"
                }, 500

    def run(self, debug: bool = False):
        """
        Run the OCSP API server.

        Args:
            debug: Enable Flask debug mode (default: False)
        """
        self.app.run(
            host=self.host,
            port=self.port,
            debug=debug
        )


def create_ocsp_api(
    pki_manager: 'PKIManager',
    host: str = "127.0.0.1",
    port: int = 8080,
    cache_duration: int = 300
) -> OCSPApi:
    """
    Create OCSP API instance.

    Args:
        pki_manager: PKIManager instance
        host: API host (default: 127.0.0.1)
        port: API port (default: 8080)
        cache_duration: Response cache duration in seconds

    Returns:
        OCSPApi instance
    """
    return OCSPApi(
        pki_manager=pki_manager,
        host=host,
        port=port,
        cache_duration=cache_duration
    )


# Example usage
if __name__ == "__main__":
    from .pki import PKIManager

    # Initialize PKI
    pki = PKIManager()
    pki.initialize_pki()

    # Create and run OCSP API
    api = create_ocsp_api(pki, port=8080)
    print(f"Starting OCSP API on http://{api.host}:{api.port}")
    print("Endpoints:")
    print(f"  - GET  /health - Health check")
    print(f"  - POST /ocsp - Certificate status check (JSON)")
    print(f"  - POST /ocsp/binary - OCSP binary protocol (RFC 6960)")
    print(f"  - GET  /ocsp/cache/stats - Cache statistics")
    print(f"  - POST /ocsp/cache/clear - Clear cache")
    api.run(debug=True)
