from app.models.dynamodb.base import Base


class ShortenUrl(Base):
    table_name = 'shorten-url'
    public_attrs = [
        'urlId',
        'url',
        'createdAt',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'serviceId',
        'isViaJumpPage',
        'name',
        'description',
        'createdBy',
    ]
    all_attrs = public_attrs + private_attrs
