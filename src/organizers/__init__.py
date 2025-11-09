"""
URL Organization Methods

This package contains 30+ different methods to organize and analyze URLs
"""

# Import all organizers for easy access
from .method_01_by_domain import ByDomainOrganizer
from .method_02_by_depth import ByDepthOrganizer
from .method_03_by_subdomain import BySubdomainOrganizer
from .method_04_by_path_structure import ByPathStructureOrganizer
from .method_05_by_query_params import ByQueryParamsOrganizer
from .method_06_by_parent_domain import ByParentDomainOrganizer
from .method_07_by_tld import ByTLDOrganizer
from .method_08_by_protocol import ByProtocolOrganizer
from .method_09_by_port import ByPortOrganizer
from .method_10_by_path_depth import ByPathDepthOrganizer
from .method_11_by_file_extension import ByFileExtensionOrganizer
from .method_12_by_content_type import ByContentTypeOrganizer
from .method_13_hierarchical_tree import HierarchicalTreeOrganizer
from .method_14_by_discovery_time import ByDiscoveryTimeOrganizer
from .method_15_by_crawl_status import ByCrawlStatusOrganizer
from .method_16_canonical_deduplication import CanonicalDeduplicationOrganizer
from .method_17_by_resource_type import ByResourceTypeOrganizer
from .method_18_by_url_length import ByURLLengthOrganizer
from .method_19_network_graph import NetworkGraphOrganizer
from .method_20_by_param_patterns import ByParamPatternsOrganizer
from .method_21_domain_and_depth_matrix import DomainDepthMatrixOrganizer

__all__ = [
    'ByDomainOrganizer',
    'ByDepthOrganizer',
    'BySubdomainOrganizer',
    'ByPathStructureOrganizer',
    'ByQueryParamsOrganizer',
    'ByParentDomainOrganizer',
    'ByTLDOrganizer',
    'ByProtocolOrganizer',
    'ByPortOrganizer',
    'ByPathDepthOrganizer',
    'ByFileExtensionOrganizer',
    'ByContentTypeOrganizer',
    'HierarchicalTreeOrganizer',
    'ByDiscoveryTimeOrganizer',
    'ByCrawlStatusOrganizer',
    'CanonicalDeduplicationOrganizer',
    'ByResourceTypeOrganizer',
    'ByURLLengthOrganizer',
    'NetworkGraphOrganizer',
    'ByParamPatternsOrganizer',
    'DomainDepthMatrixOrganizer',
]
