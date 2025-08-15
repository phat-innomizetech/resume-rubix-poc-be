from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar("T")


class StatusCode(str, Enum):
    """Standard status codes for API responses"""

    SUCCESS = "200"
    BAD_REQUEST = "400"
    UNAUTHORIZED = "401"
    FORBIDDEN = "403"
    NOT_FOUND = "404"
    CONFLICT = "409"
    INTERNAL_ERROR = "500"
    SERVICE_UNAVAILABLE = "503"


class ResponseStatus(str, Enum):
    """Standard response statuses"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class PaginationInfo(BaseModel):
    """Pagination information for paginated responses"""

    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")


class ResponseMetadata(BaseModel):
    """Additional metadata for responses"""

    timestamp: str = Field(
        default=datetime.today().strftime("%m/%d/%Y, %H:%M:%S"),
        description="Response timestamp",
    )
    requestId: Optional[str] = Field(None, description="Request ID for tracking")
    pagination: Optional[PaginationInfo] = Field(
        None, description="Pagination information if applicable"
    )


class ResponseBase(BaseModel):
    """Base response model with common fields"""

    status: ResponseStatus = Field(..., description="Response status")
    code: StatusCode = Field(..., description="Response code")
    message: str = Field(..., description="Response message")
    metadata: Optional[ResponseMetadata] = Field(None, description="Response metadata")

    def with_metadata(self, metadata: ResponseMetadata) -> "ResponseBase":
        """Add metadata to the response"""
        self.metadata = metadata
        return self


class DataResponse(ResponseBase, Generic[T]):
    """Response model for data payloads"""

    data: Optional[T] = Field(None, description="Response data")

    @classmethod
    def success(
        cls,
        data: T,
        message: str = "Success",
        metadata: Optional[ResponseMetadata] = None,
    ) -> "DataResponse[T]":
        """Create a successful response with data"""
        return cls(
            status=ResponseStatus.SUCCESS,
            code=StatusCode.SUCCESS,
            message=message,
            data=data,
            metadata=metadata,
        )

    @classmethod
    def error(
        cls,
        message: str,
        code: StatusCode = StatusCode.INTERNAL_ERROR,
        metadata: Optional[ResponseMetadata] = None,
    ) -> "DataResponse[T]":
        """Create an error response"""
        return cls(
            status=ResponseStatus.ERROR, code=code, message=message, metadata=metadata
        )


class ListResponse(DataResponse[List[T]], Generic[T]):
    """Response model for list data with pagination"""

    pagination: Optional[PaginationInfo] = Field(
        None, description="Pagination information"
    )

    @classmethod
    def success(
        cls,
        data: List[T],
        pagination: Optional[PaginationInfo] = None,
        message: str = "Success",
        metadata: Optional[ResponseMetadata] = None,
    ) -> "ListResponse[T]":
        """Create a successful response with paginated list data"""
        return cls(
            status=ResponseStatus.SUCCESS,
            code=StatusCode.SUCCESS,
            message=message,
            data=data,
            pagination=pagination,
            metadata=metadata,
        )


class ErrorResponse(ResponseBase):
    """Response model for errors"""

    errors: Optional[List[dict[str, Any]]] = Field(
        None, description="Detailed error information"
    )

    @classmethod
    def create(
        cls,
        message: str,
        code: StatusCode = StatusCode.INTERNAL_ERROR,
        errors: Optional[List[dict[str, Any]]] = None,
        metadata: Optional[ResponseMetadata] = None,
    ) -> "ErrorResponse":
        """Create an error response with optional detailed errors"""
        return cls(
            status=ResponseStatus.ERROR,
            code=code,
            message=message,
            errors=errors,
            metadata=metadata,
        )


# Type alias for all possible response types
ResponseType = Union[DataResponse[T], ListResponse[T], ErrorResponse]
