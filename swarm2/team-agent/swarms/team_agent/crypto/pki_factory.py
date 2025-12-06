"""
PKI Factory - Creates PKI providers based on configuration.

This factory allows Team Agent to instantiate different PKI providers
(self-signed, ACME, blockchain, enterprise) based on YAML configuration,
enabling easy switching between PKI backends without code changes.
"""
from typing import Dict, Any, Type
from .pki_provider import PKIProvider


class PKIFactory:
    """
    Factory for creating PKI provider instances.

    Supports built-in providers:
    - 'self-signed': Self-signed three-tier CA hierarchy
    - 'acme': Let's Encrypt / ACME protocol (when implemented)
    - 'letsencrypt': Alias for 'acme'
    - 'blockchain': Blockchain-based PKI (when implemented)

    Custom providers can be registered via register_provider().
    """

    # Registry of available providers
    PROVIDERS: Dict[str, Type[PKIProvider]] = {}

    @classmethod
    def _initialize_providers(cls):
        """Initialize built-in provider registry (lazy loading)."""
        if cls.PROVIDERS:
            return  # Already initialized

        # Import and register built-in providers
        from .providers.self_signed_provider import SelfSignedCAProvider
        cls.PROVIDERS['self-signed'] = SelfSignedCAProvider

        # Future providers (will be implemented):
        # from .providers.acme_provider import ACMEProvider
        # cls.PROVIDERS['acme'] = ACMEProvider
        # cls.PROVIDERS['letsencrypt'] = ACMEProvider  # Alias

        # from .providers.blockchain_provider import BlockchainPKIProvider
        # cls.PROVIDERS['blockchain'] = BlockchainPKIProvider

    @classmethod
    def create_provider(cls, config: Dict[str, Any]) -> PKIProvider:
        """
        Create PKI provider from configuration.

        Args:
            config: Configuration dict with 'type' key and provider-specific settings

        Returns:
            Initialized PKI provider instance

        Raises:
            ValueError: If provider type is unknown or configuration is invalid

        Example config for self-signed:
            {
                "type": "self-signed",
                "base_dir": "~/.team_agent/pki",
                "force_reinit": False
            }

        Example config for ACME (when implemented):
            {
                "type": "acme",
                "email": "admin@example.com",
                "staging": False,
                "domain_name": "example.com"
            }

        Example config for blockchain (when implemented):
            {
                "type": "blockchain",
                "blockchain_type": "ethereum",
                "rpc_url": "http://localhost:8545",
                "contract_address": "0x1234..."
            }
        """
        # Ensure providers are loaded
        cls._initialize_providers()

        # Get provider type from config
        provider_type = config.get('type', 'self-signed')

        if not provider_type:
            raise ValueError("Config must specify 'type' field")

        if provider_type not in cls.PROVIDERS:
            available = ', '.join(cls.PROVIDERS.keys())
            raise ValueError(
                f"Unknown PKI provider type: '{provider_type}'. "
                f"Available providers: {available}"
            )

        # Instantiate provider
        provider_class = cls.PROVIDERS[provider_type]
        provider = provider_class()

        # Initialize with config
        try:
            provider.initialize(config)
        except Exception as e:
            raise ValueError(
                f"Failed to initialize {provider_type} provider: {str(e)}"
            ) from e

        return provider

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[PKIProvider]) -> None:
        """
        Register a custom PKI provider.

        This allows users to add their own PKI provider implementations
        (e.g., enterprise CA, custom blockchain, hardware security module).

        Args:
            name: Provider type name (used in configuration)
            provider_class: Provider class (must inherit from PKIProvider)

        Raises:
            ValueError: If provider_class doesn't inherit from PKIProvider

        Example:
            class MyCustomProvider(PKIProvider):
                def initialize(self, config): ...
                def issue_certificate(self, domain, validity_days): ...
                # ... implement all abstract methods

            PKIFactory.register_provider('my-custom', MyCustomProvider)

            # Now can use in config:
            config = {'type': 'my-custom', ...}
            provider = PKIFactory.create_provider(config)
        """
        if not issubclass(provider_class, PKIProvider):
            raise ValueError(
                f"{provider_class.__name__} must inherit from PKIProvider"
            )

        cls.PROVIDERS[name] = provider_class

    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """
        List all registered providers.

        Returns:
            Dict mapping provider type to provider name

        Example:
            {
                'self-signed': 'Self-Signed CA (Three-Tier Hierarchy)',
                'acme': 'Let\'s Encrypt (ACME)',
                'blockchain': 'Blockchain PKI (Decentralized Trust)'
            }
        """
        cls._initialize_providers()

        # Instantiate each provider to get its name
        provider_names = {}
        for provider_type, provider_class in cls.PROVIDERS.items():
            try:
                # Create temporary instance to get name
                temp_provider = provider_class()
                provider_names[provider_type] = temp_provider.provider_name
            except Exception:
                # If instantiation fails, use class name
                provider_names[provider_type] = provider_class.__name__

        return provider_names

    @classmethod
    def get_provider_info(cls, provider_type: str) -> Dict[str, Any]:
        """
        Get information about a specific provider type.

        Args:
            provider_type: Provider type identifier

        Returns:
            Dict with provider information:
            - type: Provider type identifier
            - name: Human-readable name
            - class: Provider class name
            - available: Whether provider is available

        Example:
            {
                'type': 'self-signed',
                'name': 'Self-Signed CA (Three-Tier Hierarchy)',
                'class': 'SelfSignedCAProvider',
                'available': True
            }
        """
        cls._initialize_providers()

        if provider_type not in cls.PROVIDERS:
            return {
                'type': provider_type,
                'name': 'Unknown',
                'class': 'Unknown',
                'available': False
            }

        provider_class = cls.PROVIDERS[provider_type]

        try:
            temp_provider = provider_class()
            provider_name = temp_provider.provider_name
        except Exception:
            provider_name = provider_class.__name__

        return {
            'type': provider_type,
            'name': provider_name,
            'class': provider_class.__name__,
            'available': True
        }


# Convenience function for quick provider creation
def create_pki_provider(provider_type: str = 'self-signed', **config_kwargs) -> PKIProvider:
    """
    Convenience function to create a PKI provider with minimal code.

    Args:
        provider_type: Provider type ('self-signed', 'acme', 'blockchain', etc.)
        **config_kwargs: Configuration parameters as keyword arguments

    Returns:
        Initialized PKI provider

    Example:
        # Create self-signed provider
        provider = create_pki_provider('self-signed', base_dir='~/.team_agent/pki')

        # Create ACME provider (when implemented)
        provider = create_pki_provider('acme', email='admin@example.com', staging=True)
    """
    config = {'type': provider_type, **config_kwargs}
    return PKIFactory.create_provider(config)
